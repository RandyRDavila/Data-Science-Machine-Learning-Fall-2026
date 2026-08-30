"""Contracts for the executable production monitoring laboratory."""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from rice_dsm.monitoring_lab import BatteryInput, BatteryRiskModel, LabSettings
from rice_dsm.monitoring_lab.app import create_app
from rice_dsm.monitoring_lab.repository import PredictionRepository

PROJECT_ROOT = Path(__file__).parents[1]
LAB_ROOT = PROJECT_ROOT / "projects" / "production-monitoring-lab"


def settings(tmp_path: Path, *, slow_seconds: float = 0.02) -> LabSettings:
    """Return isolated settings for one application test."""

    return LabSettings(
        database_path=tmp_path / "predictions.sqlite3",
        incident_path=tmp_path / "incident.json",
        log_path=tmp_path / "logs" / "api.jsonl",
        slow_dependency_seconds=slow_seconds,
    )


def payload() -> dict[str, float | int]:
    """Return one valid, moderately risky synthetic battery state."""

    return {
        "ambient_temperature_c": 52.125,
        "charge_rate_c": 1.8,
        "state_of_charge_pct": 91.0,
        "cycle_count": 1_650,
        "internal_resistance_mohm": 72.25,
    }


def select_incident(configuration: LabSettings, scenario: str) -> None:
    configuration.incident_path.write_text(
        json.dumps({"scenario": scenario}), encoding="utf-8"
    )


def test_model_contract_is_bounded_and_unit_mismatch_changes_semantics() -> None:
    model = BatteryRiskModel("test-model")
    features = BatteryInput.model_validate(payload())

    correct = model.predict(features)
    mistaken = model.predict(
        features,
        temperature_c=(features.ambient_temperature_c - 32.0) * 5.0 / 9.0,
    )

    assert 0.0 <= correct.failure_probability <= 1.0
    assert correct.risk_band in {"low", "medium", "high"}
    assert mistaken.failure_probability < correct.failure_probability


def test_prediction_emits_lineage_metrics_and_privacy_bounded_logs(
    tmp_path: Path,
) -> None:
    configuration = settings(tmp_path)
    app = create_app(configuration)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/predictions",
            json=payload(),
            headers={"x-request-id": "student-diagnosis-001"},
        )
        metrics = client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "student-diagnosis-001"
    assert response.json()["model_version"] == configuration.model_version
    assert "rice_dsm_http_requests_total" in metrics.text
    assert "rice_dsm_predictions_total" in metrics.text
    assert "rice_dsm_model_info" in metrics.text
    assert "request_id" not in metrics.text
    assert "prediction_id" not in metrics.text

    events = [
        json.loads(line)
        for line in configuration.log_path.read_text(encoding="utf-8").splitlines()
    ]
    prediction_event = next(
        event for event in events if event.get("event") == "prediction_completed"
    )
    assert prediction_event["request_id"] == "student-diagnosis-001"
    assert prediction_event["model_version"] == configuration.model_version
    serialized_events = json.dumps(events)
    for raw_value in ("52.125", "72.25", "1650"):
        assert raw_value not in serialized_events


def test_validation_failure_is_counted_without_logging_payload(tmp_path: Path) -> None:
    configuration = settings(tmp_path)
    app = create_app(configuration)

    with TestClient(app) as client:
        invalid = client.post(
            "/api/v1/predictions",
            json=payload() | {"ambient_temperature_f": 125.0},
        )
        metrics = client.get("/metrics")

    assert invalid.status_code == 422
    assert (
        'rice_dsm_input_rejections_total{reason="schema-or-range"} 1.0'
        in metrics.text
    )
    logs = configuration.log_path.read_text(encoding="utf-8")
    assert "input_rejected" in logs
    assert "ambient_temperature_f" not in logs
    assert "125.0" not in logs


@pytest.mark.parametrize(
    ("scenario", "expected_status"),
    [("healthy", 200), ("artifact-mismatch", 503)],
)
def test_artifact_incident_changes_availability_explicitly(
    tmp_path: Path, scenario: str, expected_status: int
) -> None:
    configuration = settings(tmp_path)
    select_incident(configuration, scenario)
    app = create_app(configuration)

    with TestClient(app) as client:
        response = client.post("/api/v1/predictions", json=payload())

    assert response.status_code == expected_status
    if scenario == "artifact-mismatch":
        assert response.json() == {"detail": "prediction model unavailable"}
        assert "artifact_compatibility_failed" in configuration.log_path.read_text(
            encoding="utf-8"
        )


def test_slow_incident_is_visible_in_latency_evidence(tmp_path: Path) -> None:
    configuration = settings(tmp_path, slow_seconds=0.03)
    select_incident(configuration, "slow-dependency")
    app = create_app(configuration)

    started = time.perf_counter()
    with TestClient(app) as client:
        response = client.post("/api/v1/predictions", json=payload())
    elapsed = time.perf_counter() - started

    assert response.status_code == 200
    assert elapsed >= configuration.slow_dependency_seconds
    assert '"scenario":"slow-dependency"' in configuration.log_path.read_text(
        encoding="utf-8"
    )


def test_delayed_outcomes_are_joined_and_scored(tmp_path: Path) -> None:
    configuration = settings(tmp_path)
    app = create_app(configuration)

    with TestClient(app) as client:
        prediction = client.post("/api/v1/predictions", json=payload()).json()
        outcome_document = {
            "prediction_id": prediction["prediction_id"],
            "failed": True,
            "observed_at": datetime.now(UTC).isoformat(),
        }
        first = client.post("/api/v1/outcomes", json=outcome_document)
        retry = client.post("/api/v1/outcomes", json=outcome_document)
        quality = client.get("/internal/quality")

    expected_brier = (float(prediction["failure_probability"]) - 1.0) ** 2
    assert first.json()["created"] is True
    assert retry.json()["created"] is False
    assert quality.json()["joined_outcomes"] == 1
    assert quality.json()["brier_score"] == pytest.approx(expected_brier)


def test_unknown_outcome_does_not_create_orphaned_feedback(tmp_path: Path) -> None:
    repository = PredictionRepository(tmp_path / "predictions.sqlite3")

    with pytest.raises(Exception, match="FOREIGN KEY constraint failed"):
        repository.record_outcome(
            prediction_id="not-a-prediction",
            observed_at=datetime.now(UTC),
            failed=True,
        )


def test_stack_configuration_is_pinned_local_and_preprovisioned() -> None:
    compose = yaml.safe_load((LAB_ROOT / "compose.yaml").read_text(encoding="utf-8"))
    services = compose["services"]

    assert set(services) == {"api", "prometheus", "loki", "tempo", "alloy", "grafana"}
    for service in ("prometheus", "loki", "tempo", "alloy", "grafana"):
        image = services[service]["image"]
        assert ":" in image
        assert not image.endswith(":latest")

    environment = services["api"]["environment"]
    assert environment["OTEL_EXPORTER_OTLP_ENDPOINT"] == "http://alloy:4318"
    assert not any("PASSWORD" in key or "TOKEN" in key for key in environment)
    assert services["grafana"]["ports"] == ["3000:3000"]

    dashboard = json.loads(
        (
            LAB_ROOT
            / "monitoring"
            / "grafana"
            / "dashboards"
            / "battery-risk.json"
        ).read_text(encoding="utf-8")
    )
    titles = {panel["title"] for panel in dashboard["panels"]}
    assert {
        "Prediction request rate",
        "Prediction 5xx ratio",
        "Prediction latency p95",
        "Prediction decisions by scenario",
        "Rejected model inputs",
        "Delayed-outcome Brier score",
        "Structured application events",
    } <= titles


def test_lab_manual_teaches_incident_reasoning_not_dashboard_clicking() -> None:
    manual = (LAB_ROOT / "README.md").read_text(encoding="utf-8")
    runbook = (LAB_ROOT / "runbooks" / "prediction-service.md").read_text(
        encoding="utf-8"
    )

    for required in (
        "This is an executable application, not a notebook simulation",
        "Evidence has different jobs",
        "Incident exercise",
        "silent-failure exercise",
        "bounded cardinality",
        "Retraining",
        "delayed outcomes",
        "PromQL",
        "LogQL",
        "post-incident review",
    ):
        assert required.lower() in manual.lower()

    assert "Do not restart services or retrain" in runbook
    assert "Competing hypothesis rejected" in (
        LAB_ROOT / "runbooks" / "post-incident-template.md"
    ).read_text(encoding="utf-8")
