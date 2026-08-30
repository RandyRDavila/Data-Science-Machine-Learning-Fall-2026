# Lecture 3: Packages, NumPy, and pandas

Lecture 3 opens the machinery that the first two lectures used: projects,
virtual environments, dependencies, versions, modules, packages, and tests. It
then connects Python's built-in containers and iteration model to NumPy arrays
and pandas tables.

## Planned notebook sequence

| Notebook | Topic | Status | Approximate time |
| --- | --- | --- | ---: |
| 00 | Reproducible projects, environments, packages, and versions | Upgraded reference | 60 minutes |
| 01 | From notebook exploration to a tested Python package | Upgraded reference | 60 minutes |
| 02 | Testing scientific software: from unit tests to CI/CD | Upgraded reference | 120 minutes |
| 03 | From Python containers to NumPy arrays and pandas tables | Upgraded reference | 135 minutes |
| 04 | Scientific visualization and simulation | Upgraded reference | 165 minutes |
| 05 | Databases and data systems: local, cloud, and larger than memory | Upgraded reference | 225 minutes |
| 06 | LLM tools and agents for scientific software | Upgraded reference | 225 minutes |
| 07 | End-to-end data products: database to device | Upgraded reference | 225 minutes |
| 08 | NumPy indexing, reshaping, broadcasting, and vectorization | Planned | 60 minutes |
| 09 | pandas selection, cleaning, grouping, joins, and reshaping | Planned | 75 minutes |
| 10 | From labeled tables to tested feature matrices | Planned | 60 minutes |
| 11 | Capstone: a package-backed tabular pipeline | Planned extension | 20 minutes |

The current reference sequence is already longer than one three-hour meeting.
The live itinerary should select a core route and assign remaining practice as
guided reading. We will reassess the lecture boundary as the NumPy and pandas
notebooks are upgraded rather than compress important foundations artificially.

## Learning outcomes

By the end of the lecture, students should be able to:

- explain what `uv sync`, `uv run`, and the course setup script do;
- distinguish Python, an interpreter, a virtual environment, VS Code's notebook
  editor, the Jupyter extension, and a notebook kernel;
- distinguish a distribution name, import package, module, and script;
- explain version constraints, resolved versions, and the role of a lockfile;
- move reusable definitions from a notebook into the `rice_dsm` package;
- design unit, integration, contract, system, regression, and data-quality
  tests from explicit risks and independent oracles;
- use pytest fixtures, parametrization, test doubles, doctests, properties, and
  metamorphic relations appropriately;
- distinguish CI, continuous delivery, and continuous deployment, and read the
  repository's cross-platform GitHub Actions workflow;
- reason about NumPy arrays using shape, axes, and dtype;
- use vectorized operations and broadcasting instead of unnecessary Python
  loops;
- create, select, clean, group, and summarize pandas objects;
- create honest, accessible, reproducible static and interactive scientific
  visualizations from deterministic simulations;
- design and query constrained local or remote databases using parameterized
  transactions, reproducible extracts, and least-privilege operations;
- estimate working-set size and use partitioned Parquet, bounded Arrow batches,
  Polars lazy plans, and DuckDB pushdown before reaching for a cluster;
- distinguish object storage, catalogs, query engines, transactional databases,
  and warehouses in AWS-style industry and laboratory workflows;
- distinguish models, assistants, workflows, agents, tool calls, retrieval, and
  durable schedulers, and place a probabilistic model inside deterministic
  software and policy boundaries;
- compare hosted APIs, free tiers, and local/open-weight models—including
  Claude, Grok, Kimi, Llama, Qwen, Gemma, and Mistral—without confusing access
  price, model license, privacy, or total operating cost;
- manage model credentials without committing or displaying secrets, validate
  structured model output, allowlist least-privilege tools, and require policy,
  approval, idempotency, evals, audit, and monitoring around consequential
  actions;
- use an LLM to propose documentation or a reproducible training request while
  keeping code verification and scheduling under ordinary software control;
- trace an end-to-end data product from validated database state through a
  service and HTTP API to a responsive client, deployment pipeline, hosted
  runtime, and correlated client/server monitoring;
- use tests and automation to describe and protect package behavior without
  confusing passing checks with scientific validity.

## Preparation and reference

Prepare the repository from VS Code's integrated terminal with the same command
used for Lectures 1 and 2:

```bash
uv run python scripts/setup_course.py
```

Read
[`How the course Python project works`](../../supplementary-materials/computing-foundations/06-how-the-course-python-project-works.md)
alongside notebook 00. It provides a slower, diagram-supported explanation of
the repository, `.venv`, `pyproject.toml`, `uv.lock`, editable installation, and
notebook kernel.
