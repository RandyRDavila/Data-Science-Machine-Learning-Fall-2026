# Professional Practices Spine

CMOR 438 / INDE 577 develops data scientists who can also contribute to a
professional software system. These practices are a semester-long spine, not a
single lecture on tools.

## Two forms of correctness

A result is not ready unless it satisfies both:

1. **Scientific correctness:** the data, assumptions, experiment, metric, and
   interpretation support the claim.
2. **Software correctness:** another person can reproduce, inspect, test,
   change, and operate the implementation safely.

Passing tests cannot rescue data leakage or an invalid metric. A sound analysis
that only works in one hidden notebook state is not a reliable deliverable.

## Practices that accumulate through the course

| Course phase | Data-science practice | Software-engineering practice | Evidence students produce |
| --- | --- | --- | --- |
| Python foundations | preserve raw data; distinguish missing states; state invariants | meaningful names; explicit boundaries; assertions; deterministic execution | a validated scientific knowledge graph |
| Packaging, NumPy, pandas | inspect dtype, shape, index, units, and schema | virtual environments; locked dependencies; modules; package APIs; unit tests | package code imported by notebooks |
| Data acquisition and cleaning | provenance; data dictionaries; missingness policy; validation reports | repeatable ingestion; immutable raw data; configuration; structured errors | raw-to-processed pipeline with checks |
| Visualization and EDA | question-driven plots; uncertainty; avoid misleading scales | reusable plotting functions; stable figure generation; reviewable artifacts | reproducible analytical report |
| Statistical learning | assumptions; baselines; sampling; uncertainty | numerical edge tests; seeded experiments; separation of calculation and presentation | tested estimators and diagnostics |
| Machine learning | split before fitting; prevent leakage; choose meaningful metrics | pipelines; configuration; typed interfaces; experiment metadata | reproducible training and evaluation run |
| Model selection | nested decisions; honest validation; sensitivity analysis | parameter validation; automated experiments; result schemas | comparison table with traceable configuration |
| Delivery and maintenance | distribution shift; calibration; monitoring; limits of use | serialization; logging; CI; documentation; backward-compatible change | versioned model artifact and model card |

## Definition of done: an analysis

Before presenting an analytical result, a student should be able to answer:

- Where did the data come from, and may we use it?
- What does one row or observation represent?
- Which fields are raw, derived, excluded, or targets?
- How are missing, invalid, duplicated, and out-of-range values handled?
- Which transformations learned from data, and on which split were they fit?
- What baseline and metric make the result meaningful?
- Which sources of randomness exist, and how can the run be reproduced?
- What uncertainty, limitations, and failure populations remain?
- Can the notebook restart and run from top to bottom?

## Definition of done: reusable code

Before merging a package change, verify that:

- the public behavior and non-goals are stated;
- inputs are validated at the owning boundary;
- functions and classes have focused responsibilities;
- names, type hints, and docstrings clarify the interface;
- normal, boundary, invalid, and regression cases are tested;
- exceptions communicate actionable information;
- logging is used for operational events rather than scattered debugging
  `print` calls;
- dependencies are declared and locked;
- lint, package build, tests, and notebooks pass in CI; and
- documentation changes with behavior.

## Notebook-to-package rule

Exploration belongs in a notebook while the question, representation, or
interface is still changing rapidly. Move code into `src/rice_dsm/` when it has
stable behavior, is reused, needs focused tests, or forms part of a shared
interface. The notebook should then import that code and retain the scientific
narrative, experiment, and interpretation.

Do not move every three-line calculation into a utility function. Abstraction
has a maintenance cost; reuse and a clear contract should justify it.

## Code-review questions

Review scientific and engineering risk together:

1. What claim does this change support?
2. Could any transformation use information unavailable at prediction time?
3. Are units, shapes, indexes, and missing-value meanings explicit?
4. Is the smallest sensible interface exposed?
5. Which test would fail if the most important assumption stopped holding?
6. Can a new teammate reproduce the result from the committed files?
7. What behavior would be expensive or dangerous to change later?

## Practices to avoid

- editing raw data by hand without preserving provenance;
- using the test set to choose preprocessing, features, thresholds, or models;
- treating a fixed random seed as proof of scientific robustness;
- swallowing exceptions or silently coercing invalid records;
- copying helper code across notebooks;
- depending on cell execution order that is not top to bottom;
- adding an undeclared package because it exists on one laptop;
- asserting implementation details instead of public behavior;
- merging when CI is red; and
- presenting a model score without defining its meaning and limitations.

## Authoritative references

- [scikit-learn: common pitfalls and recommended practices](https://scikit-learn.org/stable/common_pitfalls.html)
- [pytest: good integration practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
- [Python logging HOWTO](https://docs.python.org/3.12/howto/logging.html)
- [Python Packaging User Guide](https://packaging.python.org/en/latest/)
- [PEP 8: Style Guide for Python Code](https://peps.python.org/pep-0008/)
