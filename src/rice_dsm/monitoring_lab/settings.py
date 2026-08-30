"""Configuration and controlled fault injection for the monitoring laboratory."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

IncidentScenario = Literal[
    "healthy",
    "unit-mismatch",
    "slow-dependency",
    "artifact-mismatch",
]
INCIDENT_SCENARIOS: tuple[IncidentScenario, ...] = (
    "healthy",
    "unit-mismatch",
    "slow-dependency",
    "artifact-mismatch",
)


@dataclass(frozen=True, slots=True)
class LabSettings:
    """Runtime settings with platform-independent paths.

    Parameters
    ----------
    database_path : pathlib.Path
        SQLite database used for prediction and outcome records.
    incident_path : pathlib.Path
        JSON control file read before each prediction.
    log_path : pathlib.Path
        JSON Lines file collected by the local observability stack.
    model_version : str
        Identifier recorded with every prediction.
    release_version : str
        Identifier for the deployed application release.
    slow_dependency_seconds : float
        Delay introduced by the controlled latency incident.
    """

    database_path: Path
    incident_path: Path
    log_path: Path
    model_version: str = "battery-risk-1.0.0"
    release_version: str = "course-lab-1.0.0"
    slow_dependency_seconds: float = 0.6

    @classmethod
    def from_environment(cls) -> LabSettings:
        """Construct settings from environment variables with local defaults."""

        runtime = Path(os.environ.get("RICE_DSM_MONITORING_RUNTIME", "runtime"))
        return cls(
            database_path=Path(
                os.environ.get(
                    "RICE_DSM_MONITORING_DATABASE", runtime / "predictions.sqlite3"
                )
            ),
            incident_path=Path(
                os.environ.get(
                    "RICE_DSM_MONITORING_INCIDENT", runtime / "incident.json"
                )
            ),
            log_path=Path(
                os.environ.get(
                    "RICE_DSM_MONITORING_LOG", runtime / "logs" / "api.jsonl"
                )
            ),
            model_version=os.environ.get(
                "RICE_DSM_MODEL_VERSION", "battery-risk-1.0.0"
            ),
            release_version=os.environ.get(
                "RICE_DSM_RELEASE_VERSION", "course-lab-1.0.0"
            ),
            slow_dependency_seconds=float(
                os.environ.get("RICE_DSM_SLOW_DEPENDENCY_SECONDS", "0.6")
            ),
        )


class IncidentController:
    """Read a bounded incident scenario from a small JSON control file."""

    def __init__(self, path: Path) -> None:
        self._path = Path(path)

    def current(self) -> IncidentScenario:
        """Return the configured scenario, failing safely to ``healthy``."""

        try:
            document = json.loads(self._path.read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, json.JSONDecodeError):
            return "healthy"

        candidate = document.get("scenario")
        if candidate not in INCIDENT_SCENARIOS:
            return "healthy"
        return cast(IncidentScenario, candidate)
