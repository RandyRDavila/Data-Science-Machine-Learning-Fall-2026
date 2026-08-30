"""Tests for the package-backed end-to-end teaching data product."""

from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from rice_dsm.data_product import (
    MeasurementInput,
    MeasurementService,
    SQLiteMeasurementRepository,
    create_app,
    dashboard_html,
)


def example_payload() -> dict[str, object]:
    """Return one valid JSON-compatible request payload."""

    return {
        "idempotency_key": "instrument-run-0001",
        "sensor_id": "sensor-alpha",
        "observed_at": "2026-08-29T14:30:00Z",
        "temperature_c": 84.5,
    }


def test_input_requires_timezone_and_forbids_unknown_fields() -> None:
    with pytest.raises(ValidationError, match="timezone offset"):
        MeasurementInput(
            idempotency_key="instrument-run-0001",
            sensor_id="sensor-alpha",
            observed_at=datetime(2026, 8, 29, 14, 30),
            temperature_c=20.0,
        )

    payload = example_payload() | {"unreviewed_field": "surprise"}
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        MeasurementInput.model_validate(payload)


@pytest.mark.parametrize(
    ("temperature_c", "expected"),
    [(20.0, "normal"), (80.0, "elevated"), (100.0, "critical")],
)
def test_service_classification_boundaries(
    temperature_c: float, expected: str
) -> None:
    assert MeasurementService.classify_temperature(temperature_c) == expected


def test_repository_makes_retries_idempotent(tmp_path: Path) -> None:
    repository = SQLiteMeasurementRepository(tmp_path / "measurements.sqlite3")
    measurement = MeasurementInput(
        idempotency_key="instrument-run-0001",
        sensor_id="sensor-alpha",
        observed_at=datetime(2026, 8, 29, 14, 30, tzinfo=UTC),
        temperature_c=84.5,
    )

    first, first_created = repository.save(measurement)
    second, second_created = repository.save(measurement)

    assert first_created is True
    assert second_created is False
    assert first.measurement_id == second.measurement_id
    assert len(repository.latest(limit=100)) == 1


def test_api_exercises_database_service_and_http_contract(tmp_path: Path) -> None:
    app = create_app(tmp_path / "measurements.sqlite3")

    with TestClient(app) as client:
        first = client.post(
            "/api/v1/measurements",
            json=example_payload(),
            headers={"x-request-id": "course-trace-001"},
        )
        retry = client.post("/api/v1/measurements", json=example_payload())
        latest = client.get("/api/v1/measurements/latest?limit=10")

    assert first.status_code == 201
    assert first.headers["x-request-id"] == "course-trace-001"
    assert first.json()["risk_level"] == "elevated"
    assert first.json()["created"] is True
    assert retry.status_code == 200
    assert retry.json()["created"] is False
    assert retry.json()["measurement_id"] == first.json()["measurement_id"]
    assert len(latest.json()) == 1


def test_api_validation_readiness_and_openapi_contract(tmp_path: Path) -> None:
    app = create_app(tmp_path / "measurements.sqlite3")

    with TestClient(app) as client:
        invalid = client.post(
            "/api/v1/measurements",
            json=example_payload() | {"temperature_c": -300},
        )
        ready = client.get("/health/ready")
        openapi = client.get("/openapi.json")

    assert invalid.status_code == 422
    assert ready.json() == {"status": "ready"}
    assert "/api/v1/measurements" in openapi.json()["paths"]


def test_frontend_is_relative_responsive_accessible_and_injection_resistant() -> None:
    html = dashboard_html()

    for contract in (
        'name="viewport"',
        "width=device-width",
        "@media (min-width: 48rem)",
        "prefers-reduced-motion",
        'aria-live="polite"',
        'fetch("/api/v1/measurements/latest?limit=20"',
        ".textContent =",
    ):
        assert contract in html

    assert "http://localhost" not in html
    assert ".innerHTML" not in html


@pytest.mark.parametrize(
    "user_agent",
    [
        "course-desktop/chromium",
        "course-phone/android-chromium",
        "course-phone/ios-webkit",
    ],
)
def test_public_contract_does_not_depend_on_user_agent(
    tmp_path: Path, user_agent: str
) -> None:
    app = create_app(tmp_path / "measurements.sqlite3")

    with TestClient(app, headers={"user-agent": user_agent}) as client:
        response = client.get("/api/v1/measurements/latest")

    assert response.status_code == 200
    assert response.json() == []
