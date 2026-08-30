"""A small package-backed scientific data product for end-to-end teaching."""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from importlib.resources import files
from pathlib import Path
from typing import Annotated, Literal
from uuid import uuid4

from fastapi import FastAPI, Query, Request, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

RiskLevel = Literal["normal", "elevated", "critical"]
_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,80}$")


class MeasurementInput(BaseModel):
    """Validated measurement accepted by the public API.

    Parameters
    ----------
    idempotency_key : str
        Stable identifier supplied by the producer for safe retries.
    sensor_id : str
        Nonblank instrument identifier.
    observed_at : datetime
        Timezone-aware observation time.
    temperature_c : float
        Temperature in degrees Celsius at or above absolute zero.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    idempotency_key: Annotated[str, Field(min_length=8, max_length=100)]
    sensor_id: Annotated[str, Field(min_length=1, max_length=80)]
    observed_at: datetime
    temperature_c: Annotated[float, Field(ge=-273.15, le=2_000.0)]

    @field_validator("observed_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        """Reject ambiguous timestamps without a UTC offset."""

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("observed_at must include a timezone offset")
        return value


class MeasurementOutput(BaseModel):
    """Public representation returned after ingestion or retrieval."""

    measurement_id: int
    idempotency_key: str
    sensor_id: str
    observed_at: datetime
    temperature_c: float
    risk_level: RiskLevel
    created: bool


@dataclass(frozen=True, slots=True)
class StoredMeasurement:
    """Framework-independent row returned by the repository."""

    measurement_id: int
    idempotency_key: str
    sensor_id: str
    observed_at: datetime
    temperature_c: float


class SQLiteMeasurementRepository:
    """Persist measurements behind a narrow repository interface."""

    def __init__(self, database_path: Path) -> None:
        """Store a platform-independent path and initialize the schema."""

        self._database_path = Path(database_path)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        """Open one short-lived connection with consistent configuration."""

        connection = sqlite3.connect(self._database_path, timeout=5.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        """Create the teaching schema when it does not yet exist."""

        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS measurements (
                    measurement_id INTEGER PRIMARY KEY,
                    idempotency_key TEXT NOT NULL UNIQUE,
                    sensor_id TEXT NOT NULL,
                    observed_at TEXT NOT NULL,
                    temperature_c REAL NOT NULL
                        CHECK (temperature_c >= -273.15)
                )
                """
            )

    def save(self, measurement: MeasurementInput) -> tuple[StoredMeasurement, bool]:
        """Store once by idempotency key and return the canonical row.

        Parameters
        ----------
        measurement : MeasurementInput
            Validated command from the service layer.

        Returns
        -------
        tuple of StoredMeasurement and bool
            Canonical row and whether this call created it.
        """

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO measurements (
                    idempotency_key, sensor_id, observed_at, temperature_c
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT (idempotency_key) DO NOTHING
                """,
                (
                    measurement.idempotency_key,
                    measurement.sensor_id,
                    measurement.observed_at.isoformat(),
                    measurement.temperature_c,
                ),
            )
            created = cursor.rowcount == 1
            row = connection.execute(
                """
                SELECT measurement_id, idempotency_key, sensor_id,
                       observed_at, temperature_c
                FROM measurements
                WHERE idempotency_key = ?
                """,
                (measurement.idempotency_key,),
            ).fetchone()

        if row is None:  # pragma: no cover - defensive invariant
            raise RuntimeError("persisted measurement could not be read")
        return _stored_measurement(row), created

    def latest(self, *, limit: int) -> tuple[StoredMeasurement, ...]:
        """Return a bounded newest-first snapshot."""

        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT measurement_id, idempotency_key, sensor_id,
                       observed_at, temperature_c
                FROM measurements
                ORDER BY observed_at DESC, measurement_id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return tuple(_stored_measurement(row) for row in rows)

    def is_ready(self) -> bool:
        """Return whether a minimal database dependency check succeeds."""

        try:
            with self._connect() as connection:
                return connection.execute("SELECT 1").fetchone()[0] == 1
        except sqlite3.Error:
            return False


def _stored_measurement(row: sqlite3.Row) -> StoredMeasurement:
    """Map one private storage row to a framework-independent object."""

    return StoredMeasurement(
        measurement_id=row["measurement_id"],
        idempotency_key=row["idempotency_key"],
        sensor_id=row["sensor_id"],
        observed_at=datetime.fromisoformat(row["observed_at"]),
        temperature_c=row["temperature_c"],
    )


class MeasurementService:
    """Coordinate domain policy without depending on HTTP."""

    def __init__(self, repository: SQLiteMeasurementRepository) -> None:
        self._repository = repository

    @staticmethod
    def classify_temperature(temperature_c: float) -> RiskLevel:
        """Map temperature to the demonstration alert policy."""

        if temperature_c >= 100.0:
            return "critical"
        if temperature_c >= 80.0:
            return "elevated"
        return "normal"

    def ingest(self, measurement: MeasurementInput) -> MeasurementOutput:
        """Persist a validated command and return its public representation."""

        stored, created = self._repository.save(measurement)
        return self._to_output(stored, created=created)

    def latest(self, *, limit: int) -> list[MeasurementOutput]:
        """Return a bounded list suitable for an API response."""

        return [
            self._to_output(stored, created=False)
            for stored in self._repository.latest(limit=limit)
        ]

    def _to_output(
        self, stored: StoredMeasurement, *, created: bool
    ) -> MeasurementOutput:
        """Add service-owned policy to one stored row."""

        return MeasurementOutput(
            measurement_id=stored.measurement_id,
            idempotency_key=stored.idempotency_key,
            sensor_id=stored.sensor_id,
            observed_at=stored.observed_at,
            temperature_c=stored.temperature_c,
            risk_level=self.classify_temperature(stored.temperature_c),
            created=created,
        )


def dashboard_html() -> str:
    """Load the packaged responsive frontend."""

    return files("rice_dsm").joinpath("static/dashboard.html").read_text(
        encoding="utf-8"
    )


def create_app(database_path: Path) -> FastAPI:
    """Create an application with explicit dependency construction.

    Parameters
    ----------
    database_path : pathlib.Path
        SQLite path used by this application instance.

    Returns
    -------
    fastapi.FastAPI
        Configured ASGI application. No network server is started.
    """

    repository = SQLiteMeasurementRepository(database_path)
    service = MeasurementService(repository)
    app = FastAPI(
        title="Rice DSM Measurement API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url=None,
    )

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):  # type: ignore[no-untyped-def]
        supplied = request.headers.get("x-request-id", "")
        request_id = (
            supplied if _REQUEST_ID_PATTERN.fullmatch(supplied) else uuid4().hex
        )
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def dashboard() -> str:
        return dashboard_html()

    @app.get("/health/live")
    def live() -> dict[str, str]:
        return {"status": "alive"}

    @app.get("/health/ready")
    def ready(response: Response) -> dict[str, str]:
        if not repository.is_ready():
            response.status_code = 503
            return {"status": "not-ready"}
        return {"status": "ready"}

    @app.post(
        "/api/v1/measurements",
        response_model=MeasurementOutput,
        status_code=201,
    )
    def ingest_measurement(
        measurement: MeasurementInput, response: Response
    ) -> MeasurementOutput:
        output = service.ingest(measurement)
        response.status_code = 201 if output.created else 200
        return output

    @app.get("/api/v1/measurements/latest", response_model=list[MeasurementOutput])
    def latest_measurements(
        limit: Annotated[int, Query(ge=1, le=100)] = 20,
    ) -> list[MeasurementOutput]:
        return service.latest(limit=limit)

    return app
