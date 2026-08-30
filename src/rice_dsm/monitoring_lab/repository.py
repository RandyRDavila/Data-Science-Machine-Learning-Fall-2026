"""Durable prediction and outcome records for the monitoring laboratory."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class QualitySummary:
    """Aggregate delayed-outcome evidence."""

    joined_outcomes: int
    brier_score: float | None
    observed_failure_rate: float | None


class PredictionRepository:
    """Persist prediction lineage and idempotent delayed outcomes in SQLite."""

    def __init__(self, path: Path) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self._path, timeout=5.0)
        try:
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            with connection:
                yield connection
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS predictions (
                    prediction_id TEXT PRIMARY KEY,
                    predicted_at TEXT NOT NULL,
                    failure_probability REAL NOT NULL
                        CHECK (failure_probability BETWEEN 0.0 AND 1.0),
                    risk_band TEXT NOT NULL,
                    model_version TEXT NOT NULL,
                    release_version TEXT NOT NULL,
                    scenario TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS outcomes (
                    prediction_id TEXT PRIMARY KEY,
                    observed_at TEXT NOT NULL,
                    failed INTEGER NOT NULL CHECK (failed IN (0, 1)),
                    FOREIGN KEY (prediction_id)
                        REFERENCES predictions(prediction_id)
                );
                """
            )

    def record_prediction(
        self,
        *,
        prediction_id: str,
        predicted_at: datetime,
        failure_probability: float,
        risk_band: str,
        model_version: str,
        release_version: str,
        scenario: str,
    ) -> None:
        """Record the evidence needed to interpret a future outcome."""

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO predictions (
                    prediction_id, predicted_at, failure_probability, risk_band,
                    model_version, release_version, scenario
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    prediction_id,
                    predicted_at.isoformat(),
                    failure_probability,
                    risk_band,
                    model_version,
                    release_version,
                    scenario,
                ),
            )

    def record_outcome(
        self, *, prediction_id: str, observed_at: datetime, failed: bool
    ) -> bool:
        """Record an outcome once and return whether a row was inserted."""

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO outcomes (prediction_id, observed_at, failed)
                VALUES (?, ?, ?)
                ON CONFLICT (prediction_id) DO NOTHING
                """,
                (prediction_id, observed_at.isoformat(), int(failed)),
            )
            return cursor.rowcount == 1

    def quality_summary(self) -> QualitySummary:
        """Compute joined outcome count, Brier score, and event rate."""

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    COUNT(*) AS joined_outcomes,
                    AVG((p.failure_probability - o.failed)
                        * (p.failure_probability - o.failed)) AS brier_score,
                    AVG(o.failed) AS observed_failure_rate
                FROM predictions AS p
                JOIN outcomes AS o USING (prediction_id)
                """
            ).fetchone()

        count = int(row["joined_outcomes"])
        return QualitySummary(
            joined_outcomes=count,
            brier_score=None if count == 0 else float(row["brier_score"]),
            observed_failure_rate=(
                None if count == 0 else float(row["observed_failure_rate"])
            ),
        )

    def is_ready(self) -> bool:
        """Return whether the persistence dependency answers a trivial query."""

        try:
            with self._connect() as connection:
                return connection.execute("SELECT 1").fetchone()[0] == 1
        except sqlite3.Error:
            return False
