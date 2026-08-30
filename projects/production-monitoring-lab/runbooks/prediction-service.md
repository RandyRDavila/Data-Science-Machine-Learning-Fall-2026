# Prediction service incident runbook

## Scope

Use this runbook when clients report unavailable, slow, rejected, or suspicious
battery-risk predictions. This laboratory has no real users or safety authority;
the workflow models professional incident reasoning with synthetic data.

## First five minutes

1. Record UTC start time, reporter, and exact client symptom.
2. Do not restart services or retrain the model before preserving evidence.
3. Check `/health/ready`, request rate, 5xx ratio, and prediction latency.
4. Compare the current model/release identity with the expected release.
5. If decisions may be unsafe, stop automated use and route requests to the
   documented fallback. Availability is not more important than correctness.

## Classify the symptom

| Symptom | First evidence | Next question |
| --- | --- | --- |
| connection failure | client error and readiness | Is the API reachable and ready? |
| 5xx increase | status-labelled request metric | Which error event and release are involved? |
| p95 latency increase | duration histogram | Which trace span accounts for the delay? |
| 422 increase | rejection counter | Did the producer violate the feature contract? |
| score/decision shift | prediction metrics | Did inputs, transformation, model, or policy change? |
| outcome degradation | joined count and Brier score | Is the change supported across time and slices? |

## Alert contract

| Alert | Condition | Required duration | Meaning |
| --- | --- | --- | --- |
| `PredictionErrorBudgetBurn` | availability-budget burn rate above 10 with traffic | 30 seconds | prediction failures are sustained enough to investigate urgently |
| `PredictionLatencyHigh` | p95 prediction latency above 500 ms with traffic | 30 seconds | clients are experiencing sustained slow responses |
| `PredictionInputsRejected` | more than five rejected inputs in five minutes | 30 seconds | a producer or data contract requires investigation |

Inspect the recording expression, traffic denominator, and pending duration
before responding. These local rules have no notification destination. In a
real service, routing, duplicate suppression, escalation, and ownership are
part of the alert contract.

## Correlation procedure

1. Select one affected request ID from client evidence or a structured log.
2. Find the `http_request_completed` and `prediction_completed` events.
3. Copy the trace ID and inspect the request trace in Tempo.
4. Check model version, release version, scenario, status, and duration.
5. Record only evidence needed for the diagnosis. Never paste secrets or raw
   governed payloads into an incident document.

## Safe mitigations

- restore the healthy incident control only for an instructor-injected fault;
- roll back to a known compatible release or model artifact;
- reject incompatible producers explicitly;
- narrow automated use or abstain while quality is uncertain;
- reduce traffic or disable a nonessential dependency when saturation is causal.

Retraining is not an availability repair and does not correct unit mismatch,
schema drift, unavailable storage, or an incompatible artifact.

## Verification

Repeat the original client action. Confirm readiness, status, latency, decision
behavior, and newly joined outcomes as applicable. Absence of new error logs is
not sufficient verification.

## Escalation

In a real organization, name the service owner, model owner, data owner,
security contact, and decision authority here. Escalate immediately when impact,
privacy, security, or safety exceeds the responder's authority.
