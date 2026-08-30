# Observability and model monitoring

Running code creates questions that cannot be answered from source code alone.
A function can be correct in a unit test while a deployed process receives a
different schema, loads the wrong model artifact, waits on a slow dependency,
or makes increasingly poor predictions for a changing population. Operational
evidence is how a team learns what the running system actually did.

## Begin with four different ideas

**Telemetry** is evidence emitted by a running system. Logs, metrics, and traces
are common telemetry signals.

**Monitoring** repeatedly checks selected signals and conditions. A dashboard,
scheduled query, or alert can be part of monitoring.

**Observability** is the system property that lets an investigator infer useful
internal behavior from available evidence. Buying a monitoring product does not
make a poorly instrumented system observable.

**Model monitoring** examines evidence specific to a learned component: feature
validity, input distribution, prediction distribution, decisions, slices,
delayed outcomes, and the identity of the data, code, model, and policy.

These ideas overlap, but they are not synonyms.

## Logs, metrics, and traces

### A log records an event

A useful application log is a structured record rather than an improvised
sentence:

```json
{
  "event": "prediction_completed",
  "level": "INFO",
  "model_version": "battery-risk-1.0.0",
  "request_id": "traffic-438-17-a9c31f20",
  "risk_band": "medium",
  "status_code": 200,
  "timestamp": "2026-08-30T19:04:31Z"
}
```

The record identifies the event and the version that produced it. It does not
contain the complete request body. Logs can accidentally become a second,
poorly governed database containing personal data, credentials, proprietary
measurements, or model inputs. Decide which fields are permitted before logging
them, and define retention and access policy.

### A metric summarizes repeated measurements

A metric is a numeric time series such as request count, error count, queue
depth, or request duration. Labels define bounded groups:

```text
rice_dsm_http_requests_total{
  method="POST",
  route="/api/v1/predictions",
  status_code="200"
}
```

Do not attach a unique request ID, prediction ID, raw timestamp, user ID, or
unbounded error message as a metric label. Each distinct label combination can
create another time series. This **high-cardinality** mistake consumes storage
and memory and can make the monitoring system fail during the incident when it
is most needed.

Histograms preserve counts across numeric buckets. They allow a system such as
Prometheus to estimate latency quantiles across many processes. Averaging
already-computed percentiles does not produce a valid global percentile.

### A trace follows one unit of work

A trace consists of nested **spans**. A prediction request might contain spans
for HTTP handling, feature lookup, schema transformation, model execution, and
database recording. The trace shows causal order and where time was spent.
Sampling means that not every request must be retained. Traces are detailed
examples, while metrics describe aggregate scope.

A request ID is an application correlation identifier. A trace ID belongs to a
distributed tracing system. They can be recorded together, but they have
different ownership and semantics.

## Alerts describe symptoms

An alert should identify a user-relevant symptom requiring action: sustained
unavailability, latency beyond an objective, rejected inputs from an important
producer, or confirmed model-quality degradation. An isolated error log is not
automatically an alert.

Every actionable alert needs:

- a precise condition and evaluation window;
- an owner and urgency;
- links to relevant dashboard evidence;
- a runbook with safe first actions;
- a method for suppressing duplicates; and
- a recovery condition.

An alert says, “investigate this symptom.” It rarely proves the cause.

## A model adds new failure layers

A prediction endpoint returning HTTP 200 establishes only that the server
accepted the request and produced a response. It does not establish that:

- the feature units match training;
- categorical meanings or time windows are unchanged;
- the intended model and decision policy were loaded;
- the current population resembles the validation population;
- probabilities remain calibrated;
- important subgroups receive acceptable performance; or
- the prediction improves a real decision.

Operational monitoring covers traffic, errors, latency, saturation, and
dependencies. Data monitoring covers schema, ranges, missingness, categories,
freshness, and lineage. Prediction monitoring covers score and decision
distributions. Performance monitoring requires trustworthy outcomes joined to
the original predictions after the target horizon.

Unlabeled input drift cannot by itself measure predictive error. Drift is a
reason to investigate, not an automatic instruction to retrain.

## The investigation sequence

When a client reports a failure:

1. Define the exact symptom and affected time interval.
2. Preserve the current release, model, data, and configuration identities.
3. Form competing hypotheses.
4. Use metrics to establish scope.
5. Use a trace to localize a representative request.
6. Use structured logs to inspect relevant events.
7. Check feature, prediction, slice, and outcome evidence.
8. Apply the safest reversible mitigation within your authority.
9. Repeat the original client action and verify recovery.
10. Record what happened and improve code, tests, telemetry, or policy.

Restarting first can destroy the state needed to diagnose the problem. Adding
more logs after an unexplained incident may help next time, but only if the new
fields are safe, specific, tested, and retained.

## Practice in this repository

The [`production-monitoring-lab`](../../projects/production-monitoring-lab/)
contains a real FastAPI process, model and persistence modules, traffic and
incident scripts, Prometheus metrics, structured logs collected by Loki, traces
stored in Tempo, and a provisioned Grafana dashboard. It runs locally with
Docker Compose and requires no monitoring-service account.

Use the lab to compare:

- an artifact failure that produces 503 responses;
- a slow dependency visible in latency metrics and a trace span;
- a producer schema change that produces explicit 422 responses;
- a unit mismatch that changes predictions while requests remain successful;
- a population change that is not a code failure; and
- delayed outcome degradation that cannot be inferred from uptime.

The service is implemented with modules and started as a process. Notebooks are
not the runtime. A notebook may later analyze exported evidence or demonstrate
the mathematics of calibration and drift.

## Check your understanding

1. Why should a request ID appear in logs but not as a Prometheus label?
2. A latency alert fires. What can a metric establish that one trace cannot?
3. Every request returns 200, but the proportion of high-risk decisions halves.
   Give three competing causes and the evidence that would distinguish them.
4. Feature drift is detected before outcomes arrive. Which actions are justified
   immediately, and which claims remain unsupported?
5. What evidence would demonstrate recovery after rolling back a model?
