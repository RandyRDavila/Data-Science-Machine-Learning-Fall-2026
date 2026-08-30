# Production monitoring laboratory

This is an executable application, not a notebook simulation. It gives students
a small supervised-learning service to operate, observe, break in controlled
ways, diagnose, and recover. The Python implementation lives in package modules;
command-line scripts create traffic and incidents; configuration files define
the monitoring infrastructure; tests preserve the contracts.

The model is deliberately simple and deterministic. The intellectual work is
not maximizing an accuracy score. It is deciding what evidence a team needs
after a model leaves the development environment and begins affecting clients.

## Learning objectives

After completing the laboratory, you should be able to:

1. distinguish monitoring, telemetry, observability, and model evaluation;
2. use metrics to determine the scope of a symptom;
3. correlate one request across a trace and structured log events;
4. distinguish software failure, data-contract failure, population shift, and
   delayed model-quality degradation;
5. design bounded-cardinality metrics and privacy-conscious logs;
6. write an alert, runbook, mitigation, and verification step; and
7. explain why retraining is not the default response to every anomaly.

## The operated system

```text
synthetic client ──HTTP──> prediction API ──> feature transform ──> model
      │                       │                         │              │
      │                       ├── prediction lineage ──> SQLite       │
      │                       ├── metrics ─────────────> Prometheus   │
      │                       ├── JSON events ─────────> Loki         │
      │                       └── trace spans ─────────> Tempo        │
      │                                                        │
      └── delayed outcome ──HTTP──> feedback path              │
                                                               v
                                                            Grafana
```

The prediction contract describes synthetic battery operating conditions. The
service returns a failure probability, a risk band, a prediction identifier,
and the model version. A separate feedback endpoint joins delayed outcomes to
predictions. Grafana is provisioned with the same dashboard on every machine.

The stack is account-free and runs locally:

- **Prometheus** stores numeric time series and supports PromQL queries.
- **Loki** stores structured application log events and supports LogQL queries.
- **Tempo** stores traces that connect operations within one request.
- **Grafana** presents the three evidence types together.
- **Grafana Alloy** collects the JSON Lines log and receives OpenTelemetry
  traces from the Python process.

These are teaching-scale single-node configurations. They intentionally omit
authentication, TLS, replication, long retention, backups, and multi-tenant
isolation. Never expose this stack to an untrusted network.

## Before class

Install the repository environment as described in the root README. The full
dashboard stack additionally requires Docker with Compose support. Docker
Desktop supplies Compose on Windows, macOS, and Linux; a compatible Docker
Engine and Compose plugin also work.

Read the beginner-oriented
[`Containers and local services`](../../supplementary-materials/computing-foundations/10-containers-and-local-services.md)
guide before using Compose. The graded route, timing, evidence requirements, and
rubric live in [`STUDENT_WORKSHEET.md`](STUDENT_WORKSHEET.md). If Docker is
unavailable or prohibited, use the documented
[`offline-evidence`](offline-evidence/) route rather than skipping the incident
reasoning exercise.

From the repository root, verify both tools:

```bash
uv --version
docker compose version
```

No account, API key, cloud resource, or `.env` secret is required.

## Start and verify the stack

All commands below run from the repository root. Create the initial healthy
control file before starting the services:

```bash
uv run python projects/production-monitoring-lab/scripts/inject_incident.py healthy
docker compose -f projects/production-monitoring-lab/compose.yaml up --build -d
uv run python projects/production-monitoring-lab/scripts/check_stack.py
```

Open these local addresses:

- Prediction API documentation: <http://localhost:8000/docs>
- Grafana dashboard: <http://localhost:3000/d/rice-dsm-battery-risk>
- Prometheus query interface: <http://localhost:9090>
- Prometheus alert state: <http://localhost:9090/alerts>
- Alloy component status: <http://localhost:12345>

Generate a healthy reference window:

```bash
uv run python projects/production-monitoring-lab/scripts/generate_traffic.py \
  --requests 80 \
  --traffic-profile baseline \
  --outcome-profile calibrated
```

Windows PowerShell accepts the command on one line. The scripts use
`pathlib.Path`, and the services communicate by Compose service names rather
than host-specific paths.

## Evidence has different jobs

| Evidence | Question it answers | Deliberate limitation |
| --- | --- | --- |
| alert | Should someone investigate now? | does not establish the cause |
| metric | How large, frequent, or widespread is the symptom? | loses individual-event detail |
| trace | Where did one request spend time or fail? | sampling may omit requests |
| structured log | What discrete event occurred with this request or artifact? | expensive and unsafe if payloads are logged carelessly |
| model monitor | Did inputs, scores, decisions, or outcomes change? | outcomes can be delayed or biased |
| experiment/evaluation | Does a controlled comparison support a claim? | may not represent live conditions |

Start with a user-visible symptom. Use metrics to determine scope, traces to
localize work, and logs to explain reviewed events. Do not begin by scrolling
through every log line.

## Incident exercise

Work in pairs. One person acts as incident commander and maintains the timeline;
the other investigates. Change roles for the second incident.

1. Record the start time and the client-visible symptom.
2. State at least two competing hypotheses before opening application logs.
3. Use the dashboard to decide whether the symptom concerns availability,
   latency, input validity, decision behavior, or delayed quality.
4. Select a representative request and correlate its request ID and trace.
5. Record evidence that rejects one hypothesis.
6. Apply a reversible mitigation.
7. Generate new traffic and verify recovery against the original symptom.
8. Write a short post-incident review using the template in `runbooks/`.

The instructor can activate a controlled scenario without changing source code:

```bash
uv run python projects/production-monitoring-lab/scripts/inject_incident.py slow-dependency
```

Available service scenarios are `healthy`, `slow-dependency`,
`artifact-mismatch`, and `unit-mismatch`. Traffic can independently introduce a
`schema-drift` or `hot-population` profile, and delayed outcomes can be generated
with a `calibrated` or `degraded` profile. Service scenario, traffic profile, and
outcome profile describe different causal layers; do not collapse them into one
generic notion of drift.

Return the service to its healthy state with:

```bash
uv run python projects/production-monitoring-lab/scripts/inject_incident.py healthy
```

## The silent-failure exercise

The most important exercise begins with an API that remains fast and returns
HTTP 200. Establish a baseline, activate `unit-mismatch`, and send the same
traffic distribution again:

```bash
uv run python projects/production-monitoring-lab/scripts/inject_incident.py healthy
uv run python projects/production-monitoring-lab/scripts/generate_traffic.py \
  --requests 100 --seed 577 --outcome-profile none

uv run python projects/production-monitoring-lab/scripts/inject_incident.py unit-mismatch
uv run python projects/production-monitoring-lab/scripts/generate_traffic.py \
  --requests 100 --seed 577 --outcome-profile none
```

The request rate, error ratio, and latency can all look acceptable while the
score and risk-band distributions change. Investigate a `prediction_completed`
event and its `feature_contract.apply` trace span. Explain why uptime monitoring
cannot validate model semantics.

Then return to `healthy` and compare calibrated with degraded delayed outcomes:

```bash
uv run python projects/production-monitoring-lab/scripts/generate_traffic.py \
  --requests 150 --seed 438 --outcome-profile degraded
```

Prometheus refreshes the Brier score when it scrapes `/metrics`. Interpret that
score only together with `rice_dsm_joined_outcomes`; an estimate without its
sample size is incomplete evidence.

## Queries students should write

PromQL examples:

```promql
sum(rate(rice_dsm_http_requests_total{route="/api/v1/predictions"}[1m]))
```

```promql
histogram_quantile(
  0.95,
  sum by (le) (
    rate(rice_dsm_http_request_duration_seconds_bucket{
      route="/api/v1/predictions"
    }[1m])
  )
)
```

LogQL examples:

```logql
{service_name="battery-prediction-api"} | json | event="input_rejected"
```

```logql
{service_name="battery-prediction-api"} | json
  | request_id="traffic-438-0-..."
```

Request and prediction identifiers belong in logs and traces, not Prometheus
labels. An identifier has unbounded cardinality: turning every identifier into
a time-series label can exhaust a monitoring system.

## SLI, SLO, error budget, and alert state

Prometheus loads reviewed recording and alert rules from
`monitoring/alerts.yml`. The teaching availability objective is a 99.5 percent
prediction success ratio. Its remaining 0.5 percent is the error budget. A burn
rate of 10 means the current failure ratio is consuming that budget ten times
as fast as the objective permits.

The alert exercise intentionally exposes three distinct states:

- **inactive:** the expression is false;
- **pending:** the expression is true but has not remained true for the complete
  `for` duration; and
- **firing:** the expression remained true for the declared duration.

Prometheus displays these states but this local stack does not page a person.
Real alert routing requires an owned destination, duplicate suppression,
escalation policy, and access controls. An alert is a symptom requiring action,
not an automated causal diagnosis.

The dashboard also presents the model and application release identity. A
`service_started` structured event records the same values. Compare evidence by
release before attributing a change to deployment; the mutable branch name or
the fact that a container is running is not sufficient identity.

## Test the evidence contract

The ordinary repository suite validates the model, API, persistence, logs,
metrics, and configuration without opening network ports:

```bash
uv run pytest tests/test_production_monitoring_lab.py -v
```

The tests assert, among other properties, that logs do not contain raw request
features and metrics do not use request or prediction IDs as labels. Monitoring
code is production code; it requires tests and review.

## Stop and reset

Stop the containers without removing their named volumes:

```bash
docker compose -f projects/production-monitoring-lab/compose.yaml down
```

To begin a new classroom incident, stop the stack, remove files under the
ignored `projects/production-monitoring-lab/runtime/` directory except
`.gitkeep`, and remove the named Compose volumes deliberately:

```bash
docker compose -f projects/production-monitoring-lab/compose.yaml down --volumes
```

That last command destroys only this Compose project's local monitoring data.
Do not teach or run broad recursive deletion commands as a substitute.

For startup errors, missing panels, delayed traces, port conflicts, and pending
alerts, follow [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

## What would change in production?

A production design would add authenticated and encrypted endpoints,
least-privilege identities, secret management, durable replicated storage,
retention and deletion policy, sampling and cost budgets, deploy annotations,
alert routing, on-call ownership, backup and restore, regional failure planning,
and review of every field that may contain sensitive or governed data.

The local lab teaches transferable interfaces. OpenTelemetry allows the Python
service to export trace evidence without coupling application code to one
commercial backend. Prometheus metric names and Grafana dashboards likewise
make the evidence inspectable without requiring students to purchase a service.

The application remains local deliberately. The companion
[`MODEL_SERVICE_DELIVERY.md`](MODEL_SERVICE_DELIVERY.md) maps this stack to a
production-shaped image, staging, approval, canary, release-observability, and
recovery workflow without asking students to purchase or expose cloud services.
