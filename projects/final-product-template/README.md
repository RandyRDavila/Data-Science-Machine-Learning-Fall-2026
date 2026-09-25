# Final machine-learning product template

Final projects live in separate repositories and consume a reviewed, tagged
release of the class-built `rice-dsm` platform. This directory records the
contract that each solo student or team carries into its product repository;
it is not itself a submission repository.

## Product premise

Build one coherent domain product rather than a collection of unrelated model
notebooks. Examples include an energy-system model explorer, materials
discovery workbench, ecological decision service, transportation analysis
system, or public-health evidence tool.

The product uses a related dataset suite that supports:

- at least one regression task;
- at least one classification task;
- at least one unsupervised or representation-learning task; and
- every course algorithm applicable to those task contracts.

One underlying domain may supply all three tasks. Forcing an algorithm onto an
incompatible target does not satisfy breadth; the report must explain why each
comparison is mathematically appropriate.

## Required system path

```text
provenance-documented data
    -> database or durable data boundary
    -> validation and task definitions
    -> reproducible train/validation/test partitions
    -> rice_dsm experiment and algorithm interfaces
    -> comparison evidence and selected model
    -> backend API
    -> user-facing analytical interface
    -> deployment artifact
    -> logs, metrics, monitoring, and recovery evidence
```

Notebooks may investigate data and communicate experiments. Reusable behavior,
training pipelines, APIs, monitoring, and deployment belong in modules,
scripts, tests, services, and workflows.

## Exact shared-platform dependency

Record the `rice-dsm` course release tag and commit in
`COURSE_PACKAGE_PROVENANCE.md`. The final lockfile must resolve that exact
reviewed version. Do not copy algorithm source into the product or depend on a
moving branch.

The installation syntax will be finalized when the first class release is
published. Until then, do not invent a placeholder dependency that appears
reproducible but cannot be installed.

## Scope scales with team size

Every product, including a solo product, satisfies the common end-to-end path.
Each participant then owns one additional vertical slice with code, tests,
documentation, and oral-defense responsibility. Examples include:

- an additional dataset and task contract;
- a substantial ingestion or validation boundary;
- an experiment and model-comparison capability;
- an API and frontend interaction;
- deployment, observability, or model-monitoring behavior; or
- a rigorous fairness, uncertainty, or failure-analysis component.

A four-person team therefore presents four identifiable ownership slices in
addition to the shared core. `TEAM_OWNERSHIP.md` records responsibility without
turning commit counts into grades.

## Evidence expected at final review

- a fresh-clone setup and one-command verification route;
- dataset provenance, licenses, observational units, time boundaries, and
  target definitions;
- mathematical justification for task-algorithm compatibility;
- leakage-resistant preprocessing and model selection;
- complete experiment evidence, not only the winning model;
- package, integration, API, and system tests;
- CI for every product pull request;
- an immutable deployment artifact and documented rollback;
- structured logs, operational metrics, and delayed model-quality evidence;
- limitations, responsible-use boundaries, and incident response;
- a live or recorded demonstration using the deployed interface; and
- an oral defense in which every participant explains both shared and owned
  system behavior.

## Files to carry into the product repository

- `COURSE_PACKAGE_PROVENANCE.md`
- `TEAM_OWNERSHIP.md`
- `PRODUCT_CONTRACT.md`

The product repository will later receive a runnable Python/service scaffold
after the shared platform's first release fixes its installation and experiment
interfaces.
