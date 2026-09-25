# Product contract

## Users and decisions

Identify the intended users, the decisions or investigations the product
supports, and decisions it must not automate.

## Dataset suite

For each dataset, record source, license, observational unit, sampling process,
time boundary, feature availability, target or unsupervised question, and
known representativeness limits.

## Task-algorithm matrix

Create a table mapping every course algorithm to the regression,
classification, clustering, or representation task where it is mathematically
applicable. Mark exclusions explicitly and justify them.

## Evaluation contract

Define train, validation, and final test roles; metrics; uncertainty evidence;
baselines; selection rules; and failure thresholds before inspecting final
test results.

## System interfaces

Define the database boundary, training command, experiment artifact, prediction
API, user interface, deployment environment, logs, metrics, alerts, and
rollback path.

## Responsible-use boundary

Describe privacy, security, fairness, misuse, uncertainty, and human-oversight
requirements. State what a successful technical demonstration does not prove.
