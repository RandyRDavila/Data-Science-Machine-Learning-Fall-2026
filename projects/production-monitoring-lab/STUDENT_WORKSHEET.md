# Student worksheet: operate and diagnose a model service

Allow approximately 30 minutes for setup and orientation, 60 minutes for two
incidents, and 30 minutes for the post-incident review. Work in pairs when
possible. One student is the incident commander and owns the timeline; the
other is the investigator and owns evidence collection. Exchange roles after
the first incident.

## Required preparation

- Complete `STUDENT_START_HERE.md`.
- Read Computing Foundations 09, *Observability and model monitoring*.
- Read Computing Foundations 10, *Containers and local services*.
- Read this laboratory's `README.md` through “Evidence has different jobs.”
- Read `MODEL_SERVICE_DELIVERY.md` before the final design question.

Choose one route:

- **Live route:** Docker is available and the complete Compose stack passes
  `scripts/check_stack.py`.
- **Offline route:** Docker is unavailable or prohibited. Use
  `offline-evidence/README.md` and state this limitation in the report.

## Success criteria

Before diagnosing an incident, the live route must show:

- API readiness at `http://localhost:8000/health/ready`;
- Prometheus, Grafana, Loki, Tempo, and Alloy reported ready by
  `check_stack.py`;
- a visible `service_started` event naming the model and release;
- at least 30 successful baseline predictions; and
- joined outcomes greater than zero before interpreting the Brier score.

The offline route must pass:

```text
uv run python projects/production-monitoring-lab/scripts/summarize_offline_evidence.py
```

## Guided Grafana orientation

Open `http://localhost:3000/d/rice-dsm-battery-risk` and set the time range to
**Last 15 minutes** with automatic refresh enabled.

1. Confirm that **Release identity** names the expected model and application
   release. Record both values.
2. Use request rate, success SLI, error-budget burn, and p95 latency to describe
   service behavior. A metric establishes scope; it does not prove a cause.
3. Use decision and joined-outcome panels to describe model behavior. Record
   the denominator beside every quality estimate.
4. Open **Explore**, choose **Tempo**, search for service
   `battery-prediction-api`, and inspect one trace. Record its trace ID and the
   longest relevant span.
5. Choose **Loki** and query the same trace ID in structured application events.
   Record the event, model version, release version, and approved diagnostic
   fields. Do not copy an entire log stream into the report.
6. Open Prometheus at `http://localhost:9090/alerts`. Distinguish an inactive,
   pending, and firing alert. Record the condition, `for` duration, and runbook
   reference for one rule.

## Incident record

Complete this table for each incident before applying a mitigation.

| Field | Incident 1 | Incident 2 |
| --- | --- | --- |
| client-visible symptom and interval | | |
| affected population or route | | |
| release and model identity | | |
| hypothesis A | | |
| hypothesis B | | |
| metric evidence establishing scope | | |
| representative trace and relevant span | | |
| correlated structured event | | |
| model/data/outcome evidence | | |
| hypothesis rejected and why | | |
| reversible mitigation | | |
| evidence that the original symptom recovered | | |

Do not write “the dashboard proved the cause.” Name the observation and explain
which hypothesis it supports or rejects.

## Required incidents

### Incident A: visible service degradation

Use `slow-dependency` or `artifact-mismatch`. Determine whether the client sees
latency or unavailability, establish scope with metrics, localize one request
with a trace, and verify recovery after returning the control to `healthy`.

For the sustained-latency route, keep requests active long enough to observe
the rule's temporal states:

```text
uv run python projects/production-monitoring-lab/scripts/inject_incident.py slow-dependency
uv run python projects/production-monitoring-lab/scripts/generate_traffic.py --requests 60 --outcome-profile none
```

The traffic command takes roughly 40 seconds because the injected operation is
deliberately slow. Watch the Prometheus rule move from inactive to pending and
then firing. Return the scenario to `healthy`, generate new traffic, and verify
the original latency symptom rather than merely waiting for an indicator to
turn green.

If an alert fires, explain why it was initially pending. If it does not fire,
state whether the traffic duration, evaluation interval, `for` duration, or
threshold explains the result. Do not weaken a threshold merely to obtain a
green or red indicator.

### Incident B: successful responses with invalid semantics

Use the silent-failure exercise in the lab manual. Compare a healthy baseline
with `unit-mismatch` under the same seed and traffic profile. Explain why the
success SLI can remain acceptable while the score and decision distributions
change. Identify the evidence that reveals the feature-unit assumption.

Then inspect delayed outcomes. Explain why drift without outcomes cannot prove
predictive degradation and why a Brier score without its joined count is
incomplete.

## Deliverables

Submit one compact incident dossier containing:

1. the completed incident record above;
2. three narrowly cropped evidence captures: one metric panel, one trace, and
   one correlated structured event;
3. the completed `runbooks/post-incident-template.md` for one incident;
4. one proposed SLI/SLO or model-quality objective with population, window,
   threshold, and delayed-information limitations;
5. one monitoring-code improvement, expressed as a test before implementation;
   and
6. a short limitations statement identifying what this local single-node lab
   does not establish about a real production system.

Do not include credentials, personal data, full raw request bodies, or an
unfiltered log export.

## Evaluation rubric (20 points)

| Criterion | Points | Full-credit evidence |
| --- | ---: | --- |
| symptom and identity | 3 | precise interval, client symptom, model and release |
| competing hypotheses | 3 | at least two plausible causes at different layers |
| evidence correlation | 5 | metric scope, representative trace, and matching log event |
| model-quality reasoning | 3 | distinguishes drift, delayed outcomes, denominator, and error |
| mitigation and verification | 3 | reversible action followed by the original client check |
| communication and safety | 3 | concise timeline, limitations, safe evidence, no causal overclaim |

## Completion check

Stop the live stack, preserve the report, and answer:

1. Which incident could an ordinary uptime monitor detect?
2. Which incident returned HTTP 200 while violating the model's semantic
   contract?
3. Which evidence was aggregate, and which evidence represented one request?
4. Which conclusions required delayed outcomes?
5. What would need authentication, retention policy, and an owner before this
   design could be exposed beyond one laptop?
