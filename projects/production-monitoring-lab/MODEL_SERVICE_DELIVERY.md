# From the local service to a governed model deployment

The repository performs real continuous deployment for its bounded static
course site. It does not publish this unauthenticated teaching API to the public
internet. This document maps the local laboratory to the additional controls a
team would require for continuous delivery of a model service.

## The artifact boundary

A deployable release would bind:

- an immutable container-image digest;
- the source commit and build provenance;
- model, feature-contract, and decision-policy versions;
- supported runtime architecture;
- dependency inventory and security review;
- training-data and evaluation references;
- schema-compatibility and migration requirements;
- resource requests and limits;
- test, model-card, and approval evidence; and
- rollback or safe-fallback compatibility.

A branch name, mutable image tag, model filename, or successful build alone is
not this release dossier.

## A production-shaped delivery path

```text
pull request
    -> locked tests, lint, contract tests, security checks
    -> build one container image
    -> record image digest, provenance, model identity, and evaluation evidence
    -> deploy that exact digest to staging
    -> run API, migration, synthetic-client, telemetry, and load checks
    -> human approval for the stated risk class
    -> promote the same digest to a limited production population
    -> compare SLIs, model evidence, and client outcomes by release
    -> expand, roll back, or route to a safe fallback
```

Build once and promote the same digest. Rebuilding after staging can change
dependencies or generated content and invalidates the evidence gathered there.
Configuration may vary by environment, but that variance must be explicit and
must not silently change feature meaning or model identity.

## Staging does not prove production validity

Staging can establish image startup, endpoint contracts, authentication flows,
database compatibility, telemetry, bounded load, and deployment mechanics. It
usually cannot reproduce production population, concurrency, dependency
behavior, or delayed outcomes. Promotion therefore remains an experiment with
limited initial exposure and explicit stopping conditions.

Common release strategies include:

- **rolling:** replace instances gradually while old and new versions overlap;
- **blue-green:** prepare a complete new environment before switching traffic;
- **canary:** expose a small eligible population to the candidate first;
- **shadow:** duplicate inputs to a candidate without using its decisions; and
- **champion-challenger:** compare an approved model with candidates under a
  governed evaluation policy.

These terms describe different traffic and decision boundaries. Shadow output
must not affect clients; a canary does. Neither strategy repairs a biased target
or invalid feature contract.

## Recovery boundaries

Rollback requires more than an old image. The earlier image must remain
compatible with database schema, feature producers, policy, and current
population. When that is false, safe recovery may require roll-forward,
abstention, reduced scope, or human review.

State-changing migrations use expand-contract design when possible: introduce
backward-compatible state, run overlapping versions safely, then remove the old
form only after rollback no longer depends on it. A model release should not
mutate historical prediction evidence in place.

## Capacity and resilience

Before promotion, specify concurrency, latency, memory, CPU, payload, and cost
budgets. Test timeouts and cancellation. Retries need a maximum, backoff, and
idempotency analysis; otherwise they amplify dependency failure. Queues need
depth limits and backpressure. Circuit breakers can protect a failing
dependency but require an explicit fallback and recovery condition.

The local `slow-dependency` scenario demonstrates latency evidence, not a full
load or saturation test. Its result must not be generalized to production
capacity.

## Security and governance

A real service needs authenticated clients, authorization by action and data,
TLS, private network boundaries where appropriate, secret management, artifact
integrity, vulnerability response, audit evidence, retention and deletion
policy, and least-privilege deployment identities.

Before release, classify logged and persisted fields. Identify who can view
features, predictions, outcomes, and traces. Define human override, contest,
and escalation paths for consequential decisions. Fairness and subgroup
monitoring require justified group definitions, lawful collection, denominators,
uncertainty, and owners who can act on the result.

## Release-observability contract

Every deployment should create observable identity at the release boundary.
This laboratory provides:

- a `service_started` event with model and application release;
- `rice_dsm_model_info` with the same controlled labels;
- a Grafana release-identity panel and service-start annotation; and
- request events that retain model and release identity.

In production, deployment automation would write an immutable deployment record
and dashboard annotation containing the image digest and change record. An
operator could then compare pre- and post-release evidence without guessing
from wall-clock time.

## Design exercise

Write a delivery plan for this service without creating cloud resources. Name:

1. the immutable artifact and registry identity;
2. checks before and after image construction;
3. staging configuration and smoke tests;
4. approval authority and evidence;
5. canary population and stopping conditions;
6. operational and model-quality signals by release;
7. database and feature compatibility requirements; and
8. rollback, roll-forward, abstention, and human-review options.

Conclude with three claims the proposed pipeline still cannot establish.
