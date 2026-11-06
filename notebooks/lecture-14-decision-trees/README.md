# Lecture 14: Classification and Regression Trees

This unit develops decision trees from impurity calculations to operated model
evidence. Students first study classification trees and probability leaves,
then regression trees and local conditional means. Both notebooks use real,
versioned data and import the same inspectable implementation from the course
package.

## Current student route

Before class, refresh a clean `main` from the repository root:

```bash
uv run --locked python scripts/refresh_course.py
```

Open the repository in VS Code, select the **Rice DSM** kernel, and run these
notebooks in order:

| Notebook | Central question | Professional artifact |
| --- | --- | --- |
| `00-classification-trees.ipynb` | How do binary questions, impurity reduction, and probability leaves produce a classification decision? | Leakage-safe clinical classification report, pruning evidence, and threshold tests |
| `01-regression-trees.ipynb` | How does squared-error reduction produce a piecewise-constant regression rule, and where does it fail? | Residual, stability, extrapolation, and monitoring report |

The [Part II student guide](../PART_II_STUDENT_GUIDE.md) explains the shared
supervised-learning route. Later ensemble and model-selection units remain
planned until their notebooks and completion evidence are published.

## Durable code and data

- `src/rice_dsm/ml/trees.py` contains the inspectable classifier, regressor,
  impurity functions, pruning logic, rule export, tree visualization, and
  threshold semantics.
- `tests/test_decision_trees.py` contains hand-computable mathematical tests,
  failure contracts, boundary cases, and trusted-library differential tests.
- `data/course_datasets.sqlite` supplies the versioned Wisconsin Diagnostic
  Breast Cancer classification data and diabetes-progression regression data.

In the [companion project template](https://github.com/RandyRDavila/Data-Science-Machine-Learning-Project-Template),
students reproduce this boundary under
`src/dsm_project/algorithms/student/`, `tests/`, `data/local/`,
`data/fixtures/`, and a question-led applied notebook. The notebook imports the
package; it is not a second implementation. Both notebooks include the exact
branch, quality-check, commit, and push workflow plus an algorithm-specific
test plan.

## Focused verification

```bash
uv run ruff check src/rice_dsm/ml/trees.py tests/test_decision_trees.py
uv run pytest tests/test_decision_trees.py -q
```
