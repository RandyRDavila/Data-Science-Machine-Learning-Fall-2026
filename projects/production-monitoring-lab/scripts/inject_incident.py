"""Select a controlled incident for the production monitoring laboratory."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

SCENARIOS = (
    "healthy",
    "unit-mismatch",
    "slow-dependency",
    "artifact-mismatch",
)
DEFAULT_INCIDENT_PATH = Path(
    "projects/production-monitoring-lab/runtime/incident.json"
)


def write_scenario(path: Path, scenario: str) -> None:
    """Atomically replace the incident control document."""

    path.parent.mkdir(parents=True, exist_ok=True)
    document = json.dumps({"scenario": scenario}, indent=2) + "\n"
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix="incident-", suffix=".json"
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(document)
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Select a controlled monitoring-lab incident."
    )
    parser.add_argument("scenario", choices=SCENARIOS)
    parser.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_INCIDENT_PATH,
        help="Incident control path shared with the service.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    write_scenario(args.path, args.scenario)
    print(f"incident scenario: {args.scenario}")
    print(f"control file: {args.path.resolve()}")


if __name__ == "__main__":
    main()
