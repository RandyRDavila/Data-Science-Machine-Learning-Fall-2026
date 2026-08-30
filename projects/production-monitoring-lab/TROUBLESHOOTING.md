# Production monitoring lab troubleshooting

Preserve the first failure message. Diagnose one layer at a time instead of
reinstalling every tool or repeatedly restarting all services.

## Docker cannot be reached

Run `docker version`. If the client appears but server information does not,
start Docker Desktop or the Docker daemon. On a managed machine, container use
may be prohibited; use the offline route in `STUDENT_WORKSHEET.md`.

## Compose configuration does not parse

From the repository root, run:

```text
docker compose -f projects/production-monitoring-lab/compose.yaml config -q
```

An empty successful result means the merged Compose configuration parses. A
path error usually means the terminal is not at the repository root.

## An image will not download

Record the image name and first registry error. Check network connectivity,
VPN or proxy policy, registry access, and free disk space. Do not replace a
pinned image with `latest` to hide an unavailable or incompatible version.

## A host port is already in use

The lab publishes ports 8000, 3000, 9090, 3100, 3200, and 12345. Stop the
conflicting local application or use an instructor-provided override. Changing
only one URL can leave health checks and client scripts pointing at a different
port.

## The API is unhealthy

Run:

```text
docker compose -f projects/production-monitoring-lab/compose.yaml ps
docker compose -f projects/production-monitoring-lab/compose.yaml logs api
```

Distinguish an image-build failure, Python import failure, database permission
failure, and readiness failure. The last relevant traceback is usually more
useful than the final “container exited” summary.

## Grafana opens but panels show no data

1. Run the traffic generator.
2. Set the dashboard to **Last 15 minutes**.
3. Confirm Prometheus reports the API target as `UP` at
   `http://localhost:9090/targets`.
4. Query `rice_dsm_model_info` directly in Prometheus.
5. Wait for at least one five-second scrape interval.

Zero and no data are different states. Zero can be valid evidence; no data can
mean no scrape, no matching series, or an incorrect query.

## Logs do not appear

Confirm that `runtime/logs/api.jsonl` exists after a request, Alloy is healthy,
and Loki is ready. Inspect Alloy component status at `http://localhost:12345`.
Do not change application logging and collector configuration simultaneously.

## Traces do not appear immediately

Confirm that the API exports to `http://alloy:4318`, then generate new traffic.
Tempo may need time to complete an in-memory block before a search returns the
trace. Preserve a trace ID from an application event and retry the targeted
search rather than generating unbounded traffic.

## An alert remains pending

Prometheus evaluates rules every five seconds. A condition must remain true for
the rule's complete `for` duration before it fires. Check the expression in the
Prometheus query interface, the current traffic rate, and the rule page. Pending
is evidence that the threshold is true but its required duration has not yet
elapsed.

## Model quality does not update

The Brier score requires outcomes joined to earlier prediction IDs. Generate
traffic with a non-`none` outcome profile and confirm `joined outcomes` is
positive. A missing outcome is an information-delay condition, not a server
availability failure.

## Reset only this lab

Use the commands in the lab README. `down` retains named volumes;
`down --volumes` deliberately removes this Compose project's monitoring data.
Never use a broad recursive deletion command as a generic Docker repair.
