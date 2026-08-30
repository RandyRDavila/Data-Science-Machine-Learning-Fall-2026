"""Fail unless every public laboratory endpoint provides usable evidence."""

from __future__ import annotations

import argparse
import time

import httpx


def wait_until_ready(
    client: httpx.Client, *, name: str, url: str, attempts: int, delay: float
) -> None:
    """Retry a bounded readiness check while containers finish starting."""

    last_error: Exception | None = None
    for _ in range(attempts):
        try:
            response = client.get(url)
            response.raise_for_status()
        except httpx.HTTPError as error:
            last_error = error
            time.sleep(delay)
            continue
        print(f"ready: {name} ({url})")
        return
    raise RuntimeError(f"not ready after {attempts} attempts: {name}") from last_error


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--prometheus-url", default="http://localhost:9090")
    parser.add_argument("--grafana-url", default="http://localhost:3000")
    parser.add_argument("--attempts", type=int, default=12)
    parser.add_argument("--delay-seconds", type=float, default=1.0)
    args = parser.parse_args()

    checks = {
        "prediction API": f"{args.api_url}/health/ready",
        "Prometheus": f"{args.prometheus_url}/-/ready",
        "Grafana": f"{args.grafana_url}/api/health",
    }
    with httpx.Client(timeout=5.0) as client:
        for name, url in checks.items():
            wait_until_ready(
                client,
                name=name,
                url=url,
                attempts=args.attempts,
                delay=args.delay_seconds,
            )


if __name__ == "__main__":
    main()
