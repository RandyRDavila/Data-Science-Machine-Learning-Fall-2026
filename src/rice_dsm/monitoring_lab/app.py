"""Instrumented FastAPI service for the production monitoring laboratory."""

from __future__ import annotations

import logging
import re
import sqlite3
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from opentelemetry import trace
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel, ConfigDict

from rice_dsm.monitoring_lab.model import BatteryInput, BatteryRiskModel, RiskBand
from rice_dsm.monitoring_lab.repository import PredictionRepository
from rice_dsm.monitoring_lab.settings import IncidentController, LabSettings
from rice_dsm.monitoring_lab.telemetry import (
    ServiceMetrics,
    build_event_logger,
    log_event,
    trace_id,
)

_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,80}$")
_tracer = trace.get_tracer("rice_dsm.monitoring_lab")


class PredictionOutput(BaseModel):
    """Public prediction response with lineage identifiers."""

    prediction_id: str
    failure_probability: float
    risk_band: RiskBand
    model_version: str


class OutcomeInput(BaseModel):
    """Delayed outcome joined to one earlier prediction."""

    model_config = ConfigDict(extra="forbid")

    prediction_id: str
    failed: bool
    observed_at: datetime


class OutcomeOutput(BaseModel):
    """Result of an idempotent outcome submission."""

    prediction_id: str
    created: bool


class QualityOutput(BaseModel):
    """Current aggregate evidence from joined outcomes."""

    joined_outcomes: int
    brier_score: float | None
    observed_failure_rate: float | None


def _close_logger(logger: logging.Logger) -> None:
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)


def create_app(settings: LabSettings) -> FastAPI:
    """Construct the instrumented application without starting a server.

    Parameters
    ----------
    settings : LabSettings
        Explicit paths, versions, and incident timing used by this instance.

    Returns
    -------
    fastapi.FastAPI
        Application exposing prediction, feedback, health, and metrics paths.
    """

    repository = PredictionRepository(settings.database_path)
    model = BatteryRiskModel(settings.model_version)
    incidents = IncidentController(settings.incident_path)
    metrics = ServiceMetrics.create(
        model_version=settings.model_version,
        release_version=settings.release_version,
    )
    logger = build_event_logger(settings.log_path)

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        yield
        _close_logger(logger)

    app = FastAPI(
        title="Rice DSM Battery Risk Monitoring Lab",
        version=settings.release_version,
        redoc_url=None,
        lifespan=lifespan,
    )
    app.state.metrics = metrics
    app.state.repository = repository
    app.state.event_logger = logger

    @app.middleware("http")
    async def observe_request(request: Request, call_next):  # type: ignore[no-untyped-def]
        started = time.perf_counter()
        supplied = request.headers.get("x-request-id", "")
        request_id = (
            supplied if _REQUEST_ID_PATTERN.fullmatch(supplied) else uuid4().hex
        )
        request.state.request_id = request_id
        status_code = 500
        response: Response | None = None
        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["x-request-id"] = request_id
            return response
        except Exception as error:
            log_event(
                logger,
                logging.ERROR,
                "http_request_failed",
                "Unhandled request failure",
                request_id=request_id,
                trace_id=trace_id(),
                method=request.method,
                route=request.url.path,
                status_code=500,
                error_type=type(error).__name__,
                exc_info=(type(error), error, error.__traceback__),
            )
            raise
        finally:
            duration = time.perf_counter() - started
            route_object = request.scope.get("route")
            route = getattr(route_object, "path", request.url.path)
            metrics.requests.labels(request.method, route, str(status_code)).inc()
            metrics.latency.labels(request.method, route).observe(duration)
            log_event(
                logger,
                logging.INFO if status_code < 500 else logging.ERROR,
                "http_request_completed",
                "HTTP request completed",
                request_id=request_id,
                trace_id=trace_id(),
                method=request.method,
                route=route,
                status_code=status_code,
                duration_ms=round(duration * 1_000, 3),
                scenario=incidents.current(),
                model_version=settings.model_version,
                release_version=settings.release_version,
            )

    @app.exception_handler(RequestValidationError)
    async def validation_error(
        request: Request, error: RequestValidationError
    ) -> JSONResponse:
        metrics.input_rejections.labels("schema-or-range").inc()
        log_event(
            logger,
            logging.WARNING,
            "input_rejected",
            "Request failed schema or range validation",
            trace_id=trace_id(),
            method=request.method,
            route=request.url.path,
            status_code=422,
            error_type=type(error).__name__,
        )
        return JSONResponse(status_code=422, content={"detail": error.errors()})

    @app.get("/health/live")
    def live() -> dict[str, str]:
        return {"status": "alive"}

    @app.get("/health/ready")
    def ready(response: Response) -> dict[str, str]:
        if not repository.is_ready():
            response.status_code = 503
            return {"status": "not-ready"}
        return {"status": "ready"}

    @app.post("/api/v1/predictions", response_model=PredictionOutput)
    def predict(
        features: BatteryInput,
        request: Request,
    ) -> PredictionOutput:
        request_id = request.state.request_id
        scenario = incidents.current()
        if scenario == "artifact-mismatch":
            log_event(
                logger,
                logging.ERROR,
                "artifact_compatibility_failed",
                "Model artifact is incompatible with the feature contract",
                request_id=request_id,
                trace_id=trace_id(),
                scenario=scenario,
                model_version=settings.model_version,
                release_version=settings.release_version,
                error_type="ArtifactCompatibilityError",
            )
            raise HTTPException(status_code=503, detail="prediction model unavailable")

        transformed_temperature = features.ambient_temperature_c
        unit_assumption = "celsius"
        with _tracer.start_as_current_span("feature_contract.apply") as span:
            span.set_attribute("lab.incident.scenario", scenario)
            if scenario == "slow-dependency":
                time.sleep(settings.slow_dependency_seconds)
                span.set_attribute("feature.lookup.simulated_delay", True)
            if scenario == "unit-mismatch":
                transformed_temperature = (
                    features.ambient_temperature_c - 32.0
                ) * 5.0 / 9.0
                unit_assumption = "fahrenheit"
            span.set_attribute("feature.temperature.unit_assumption", unit_assumption)

        prediction = model.predict(
            features, temperature_c=transformed_temperature
        )
        prediction_id = uuid4().hex
        repository.record_prediction(
            prediction_id=prediction_id,
            predicted_at=datetime.now(UTC),
            failure_probability=prediction.failure_probability,
            risk_band=prediction.risk_band,
            model_version=model.version,
            release_version=settings.release_version,
            scenario=scenario,
        )
        metrics.predictions.labels(prediction.risk_band, model.version, scenario).inc()
        metrics.prediction_score.labels(model.version, scenario).observe(
            prediction.failure_probability
        )
        log_event(
            logger,
            logging.INFO,
            "prediction_completed",
            "Battery risk prediction completed",
            request_id=request_id,
            trace_id=trace_id(),
            prediction_id=prediction_id,
            scenario=scenario,
            model_version=model.version,
            release_version=settings.release_version,
            risk_band=prediction.risk_band,
            failure_probability=round(prediction.failure_probability, 6),
            temperature_unit_assumption=unit_assumption,
        )
        return PredictionOutput(
            prediction_id=prediction_id,
            failure_probability=prediction.failure_probability,
            risk_band=prediction.risk_band,
            model_version=model.version,
        )

    @app.post("/api/v1/outcomes", response_model=OutcomeOutput)
    def record_outcome(outcome: OutcomeInput) -> OutcomeOutput:
        if (
            outcome.observed_at.tzinfo is None
            or outcome.observed_at.utcoffset() is None
        ):
            raise HTTPException(
                status_code=422, detail="observed_at must include a timezone offset"
            )
        try:
            created = repository.record_outcome(
                prediction_id=outcome.prediction_id,
                observed_at=outcome.observed_at,
                failed=outcome.failed,
            )
        except sqlite3.IntegrityError as error:
            raise HTTPException(
                status_code=404, detail="prediction not found"
            ) from error
        if created:
            metrics.outcomes.labels(str(outcome.failed).lower()).inc()
        return OutcomeOutput(prediction_id=outcome.prediction_id, created=created)

    @app.get("/internal/quality", response_model=QualityOutput)
    def quality() -> QualityOutput:
        summary = repository.quality_summary()
        metrics.joined_outcomes.set(summary.joined_outcomes)
        if summary.brier_score is not None:
            metrics.brier_score.set(summary.brier_score)
        if summary.observed_failure_rate is not None:
            metrics.observed_failure_rate.set(summary.observed_failure_rate)
        log_event(
            logger,
            logging.INFO,
            "quality_summary_computed",
            "Delayed outcomes were joined to prediction evidence",
            joined_outcomes=summary.joined_outcomes,
            brier_score=summary.brier_score,
            model_version=model.version,
            release_version=settings.release_version,
        )
        return QualityOutput(
            joined_outcomes=summary.joined_outcomes,
            brier_score=summary.brier_score,
            observed_failure_rate=summary.observed_failure_rate,
        )

    @app.get("/metrics", include_in_schema=False)
    def prometheus_metrics() -> Response:
        quality()
        return Response(
            content=generate_latest(metrics.registry),
            media_type=CONTENT_TYPE_LATEST,
        )

    return app


def create_app_from_environment() -> FastAPI:
    """Uvicorn factory that reads paths and versions from the environment."""

    return create_app(LabSettings.from_environment())


def default_runtime_path() -> Path:
    """Return the default local runtime path for command-line documentation."""

    return Path("runtime")
