"""Validate and summarize the committed offline incident evidence."""

from __future__ import annotations

import json
from pathlib import Path

EVIDENCE_ROOT = Path(__file__).resolve().parents[1] / "offline-evidence"


def load_json(name: str) -> dict[str, object]:
    """Load one JSON object from the offline evidence directory."""

    document = json.loads((EVIDENCE_ROOT / name).read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise TypeError(f"{name} must contain one JSON object")
    return document


def load_events() -> list[dict[str, object]]:
    """Load structured events and require one JSON object per nonempty line."""

    events: list[dict[str, object]] = []
    path = EVIDENCE_ROOT / "application-events.jsonl"
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        event = json.loads(line)
        if not isinstance(event, dict):
            raise TypeError(f"{path.name}:{line_number} must contain a JSON object")
        events.append(event)
    return events


def main() -> int:
    """Print bounded comparisons without claiming an incident cause."""

    manifest = load_json("case-manifest.json")
    clients = load_json("client-summary.json")
    quality = load_json("quality-summary.json")
    trace = load_json("trace.json")
    events = load_events()

    reference = clients["reference"]
    comparison = clients["comparison"]
    reference_quality = quality["reference"]
    comparison_quality = quality["comparison"]
    if not all(
        isinstance(value, dict)
        for value in (reference, comparison, reference_quality, comparison_quality)
    ):
        raise TypeError("client and quality windows must be JSON objects")

    print(f"Case: {manifest['case_id']}")
    print(
        "HTTP 200 responses: "
        f"{reference['http_200']}/{reference['requests']} -> "
        f"{comparison['http_200']}/{comparison['requests']}"
    )
    print(
        "p95 latency (seconds): "
        f"{reference['p95_latency_seconds']} -> "
        f"{comparison['p95_latency_seconds']}"
    )
    print(
        "high-risk decisions: "
        f"{reference['risk_bands']['high']} -> "
        f"{comparison['risk_bands']['high']}"
    )
    print(
        "Brier score (joined outcomes): "
        f"{reference_quality['brier_score']} "
        f"({reference_quality['joined_outcomes']}) -> "
        f"{comparison_quality['brier_score']} "
        f"({comparison_quality['joined_outcomes']})"
    )
    print(
        f"Representative trace: {trace['trace_id']}; "
        f"structured events: {len(events)}"
    )
    print(
        "Interpretation requires the trace and events; "
        "this summary does not name a cause."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
