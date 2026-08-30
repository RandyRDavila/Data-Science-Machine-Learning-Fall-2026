"""Structured logs and bounded-cardinality Prometheus instruments."""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from types import TracebackType
from typing import TextIO
from uuid import uuid4

from opentelemetry import trace
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

_EVENT_FIELDS = (
    "event",
    "request_id",
    "trace_id",
    "prediction_id",
    "method",
    "route",
    "status_code",
    "duration_ms",
    "scenario",
    "model_version",
    "release_version",
    "risk_band",
    "failure_probability",
    "temperature_unit_assumption",
    "error_type",
    "joined_outcomes",
    "brier_score",
)


class JsonEventFormatter(logging.Formatter):
    """Render approved operational fields as one JSON object per line."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in _EVENT_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def build_event_logger(
    log_path: Path, *, stream: TextIO | None = None
) -> logging.Logger:
    """Create an isolated logger that writes to stdout and a JSON Lines file."""

    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(f"rice_dsm.monitoring_lab.{uuid4().hex}")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    formatter = JsonEventFormatter()

    stream_handler = logging.StreamHandler(stream or sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def trace_id() -> str | None:
    """Return the active OpenTelemetry trace identifier when one exists."""

    span_context = trace.get_current_span().get_span_context()
    if not span_context.is_valid:
        return None
    return f"{span_context.trace_id:032x}"


def log_event(
    logger: logging.Logger,
    level: int,
    event: str,
    message: str,
    *,
    exc_info: tuple[type[BaseException], BaseException, TracebackType] | None = None,
    **fields: object,
) -> None:
    """Emit one event using only formatter-approved structured fields."""

    logger.log(
        level,
        message,
        extra={"event": event, **fields},
        exc_info=exc_info,
    )


@dataclass(slots=True)
class ServiceMetrics:
    """Prometheus instruments owned by one application instance."""

    registry: CollectorRegistry
    requests: Counter
    latency: Histogram
    predictions: Counter
    prediction_score: Histogram
    input_rejections: Counter
    outcomes: Counter
    joined_outcomes: Gauge
    brier_score: Gauge
    observed_failure_rate: Gauge
    model_info: Gauge

    @classmethod
    def create(cls, *, model_version: str, release_version: str) -> ServiceMetrics:
        """Create instruments in an isolated registry for tests and factories."""

        registry = CollectorRegistry()
        metrics = cls(
            registry=registry,
            requests=Counter(
                "rice_dsm_http_requests_total",
                "Completed HTTP requests.",
                ("method", "route", "status_code"),
                registry=registry,
            ),
            latency=Histogram(
                "rice_dsm_http_request_duration_seconds",
                "HTTP request duration in seconds.",
                ("method", "route"),
                buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5),
                registry=registry,
            ),
            predictions=Counter(
                "rice_dsm_predictions_total",
                "Predictions by bounded operational dimensions.",
                ("risk_band", "model_version", "scenario"),
                registry=registry,
            ),
            prediction_score=Histogram(
                "rice_dsm_prediction_score",
                "Distribution of predicted failure probabilities.",
                ("model_version", "scenario"),
                buckets=(0.05, 0.1, 0.25, 0.5, 0.65, 0.8, 0.95, 1.0),
                registry=registry,
            ),
            input_rejections=Counter(
                "rice_dsm_input_rejections_total",
                "Requests rejected before prediction.",
                ("reason",),
                registry=registry,
            ),
            outcomes=Counter(
                "rice_dsm_outcomes_total",
                "Delayed outcomes accepted by the feedback path.",
                ("failed",),
                registry=registry,
            ),
            joined_outcomes=Gauge(
                "rice_dsm_joined_outcomes",
                "Number of predictions joined to delayed outcomes.",
                registry=registry,
            ),
            brier_score=Gauge(
                "rice_dsm_brier_score",
                "Brier score over joined delayed outcomes.",
                registry=registry,
            ),
            observed_failure_rate=Gauge(
                "rice_dsm_observed_failure_rate",
                "Observed failure rate over joined delayed outcomes.",
                registry=registry,
            ),
            model_info=Gauge(
                "rice_dsm_model_info",
                "Identity of the model and application release.",
                ("model_version", "release_version"),
                registry=registry,
            ),
        )
        metrics.model_info.labels(model_version, release_version).set(1)
        return metrics
