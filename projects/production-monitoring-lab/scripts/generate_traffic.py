"""Generate reproducible requests and optional delayed outcomes for the lab."""

from __future__ import annotations

import argparse
import json
import math
import random
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal
from uuid import uuid4

import httpx

TrafficProfile = Literal["baseline", "hot-population", "schema-drift"]
OutcomeProfile = Literal["none", "calibrated", "degraded"]
DEFAULT_OUTPUT_PATH = Path(
    "projects/production-monitoring-lab/runtime/client-evidence.jsonl"
)


@dataclass(slots=True)
class TrafficSummary:
    """Counts and latency observations from one traffic run."""

    attempted: int = 0
    succeeded: int = 0
    rejected: int = 0
    unavailable: int = 0
    outcomes_created: int = 0
    total_latency_seconds: float = 0.0


def _bounded_normal(
    generator: random.Random, mean: float, std: float, low: float, high: float
) -> float:
    return min(max(generator.gauss(mean, std), low), high)


def build_payload(
    generator: random.Random, profile: TrafficProfile
) -> dict[str, float | int]:
    """Create one synthetic feature vector without personal or proprietary data."""

    mean_temperature = 52.0 if profile == "hot-population" else 27.0
    payload: dict[str, float | int] = {
        "ambient_temperature_c": round(
            _bounded_normal(generator, mean_temperature, 8.0, -40.0, 85.0), 3
        ),
        "charge_rate_c": round(
            _bounded_normal(generator, 1.4, 0.45, 0.1, 5.0), 3
        ),
        "state_of_charge_pct": round(
            _bounded_normal(generator, 78.0, 13.0, 0.0, 100.0), 3
        ),
        "cycle_count": generator.randint(50, 2_500),
        "internal_resistance_mohm": round(
            _bounded_normal(generator, 58.0, 18.0, 0.0, 500.0), 3
        ),
    }
    if profile == "schema-drift":
        celsius = float(payload.pop("ambient_temperature_c"))
        payload["ambient_temperature_f"] = round(celsius * 9.0 / 5.0 + 32.0, 3)
    return payload


def outcome_probability(score: float, profile: OutcomeProfile) -> float:
    """Return the synthetic event probability used after a prediction."""

    if profile == "degraded":
        return min(0.98, 0.25 + 0.75 * math.sqrt(score))
    return score


def run_traffic(
    *,
    base_url: str,
    requests: int,
    traffic_profile: TrafficProfile,
    outcome_profile: OutcomeProfile,
    seed: int,
    delay_seconds: float,
    timeout_seconds: float,
    output_path: Path,
) -> TrafficSummary:
    """Exercise the HTTP contract and persist a client-side evidence record."""

    generator = random.Random(seed)
    summary = TrafficSummary()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with (
        httpx.Client(base_url=base_url, timeout=timeout_seconds) as client,
        output_path.open("a", encoding="utf-8") as evidence,
    ):
        for sequence in range(requests):
            request_id = f"traffic-{seed}-{sequence}-{uuid4().hex[:8]}"
            payload = build_payload(generator, traffic_profile)
            started = time.perf_counter()
            summary.attempted += 1
            try:
                response = client.post(
                    "/api/v1/predictions",
                    json=payload,
                    headers={"x-request-id": request_id},
                )
                duration = time.perf_counter() - started
                summary.total_latency_seconds += duration
                if response.status_code == 200:
                    summary.succeeded += 1
                    prediction = response.json()
                    if outcome_profile != "none":
                        probability = outcome_probability(
                            float(prediction["failure_probability"]), outcome_profile
                        )
                        failed = generator.random() < probability
                        outcome = client.post(
                            "/api/v1/outcomes",
                            json={
                                "prediction_id": prediction["prediction_id"],
                                "failed": failed,
                                "observed_at": datetime.now(UTC).isoformat(),
                            },
                            headers={"x-request-id": f"outcome-{request_id}"},
                        )
                        outcome.raise_for_status()
                        summary.outcomes_created += int(outcome.json()["created"])
                elif response.status_code == 422:
                    summary.rejected += 1
                    prediction = None
                else:
                    summary.unavailable += 1
                    prediction = None
                record = {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "request_id": request_id,
                    "traffic_profile": traffic_profile,
                    "outcome_profile": outcome_profile,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1_000, 3),
                    "prediction": prediction,
                }
            except httpx.HTTPError as error:
                summary.unavailable += 1
                record = {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "request_id": request_id,
                    "traffic_profile": traffic_profile,
                    "outcome_profile": outcome_profile,
                    "client_error": type(error).__name__,
                }
            evidence.write(json.dumps(record, sort_keys=True) + "\n")
            evidence.flush()
            if delay_seconds:
                time.sleep(delay_seconds)

    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--requests", type=int, default=40)
    parser.add_argument(
        "--traffic-profile",
        choices=("baseline", "hot-population", "schema-drift"),
        default="baseline",
    )
    parser.add_argument(
        "--outcome-profile",
        choices=("none", "calibrated", "degraded"),
        default="none",
    )
    parser.add_argument("--seed", type=int, default=438)
    parser.add_argument("--delay-seconds", type=float, default=0.05)
    parser.add_argument("--timeout-seconds", type=float, default=5.0)
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT_PATH
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.requests < 1:
        raise SystemExit("--requests must be positive")
    summary = run_traffic(
        base_url=args.base_url,
        requests=args.requests,
        traffic_profile=args.traffic_profile,
        outcome_profile=args.outcome_profile,
        seed=args.seed,
        delay_seconds=args.delay_seconds,
        timeout_seconds=args.timeout_seconds,
        output_path=args.output,
    )
    mean_latency_ms = (
        1_000 * summary.total_latency_seconds / summary.attempted
        if summary.attempted
        else 0.0
    )
    print(f"attempted: {summary.attempted}")
    print(f"succeeded: {summary.succeeded}")
    print(f"rejected: {summary.rejected}")
    print(f"unavailable: {summary.unavailable}")
    print(f"outcomes created: {summary.outcomes_created}")
    print(f"mean client latency: {mean_latency_ms:.1f} ms")
    print(f"client evidence: {args.output.resolve()}")


if __name__ == "__main__":
    main()
