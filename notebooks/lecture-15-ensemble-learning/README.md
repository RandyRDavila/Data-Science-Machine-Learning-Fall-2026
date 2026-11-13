# Lecture 15: Ensemble Learning

This unit develops ensemble methods as distinct mathematical mechanisms rather
than a catalog of library classes. Students study variance reduction through
bagging and randomized forests, stagewise optimization through boosting, and
leakage-safe combination through voting and stacking. Every laboratory uses
real, versioned data from the course database and ends at a professional
software boundary.

## Current student route

Before class, refresh a clean `main` from the repository root:

```bash
uv run --locked python scripts/refresh_course.py
```

Open the repository in VS Code, select the **Rice DSM** kernel, and run the
notebooks in order:

| Notebook | Central question | Professional artifact |
| --- | --- | --- |
| `00-random-forests.ipynb` | How do bootstrap perturbations, randomized features, and averaging convert tree instability into useful diversity? | Forest benchmark with OOB, probability, importance, stability, and resource evidence |
| `01-boosting.ipynb` | How does sequential residual fitting become gradient descent in function space? | Boosting benchmark with staged loss, early-stopping boundary, residual diagnostics, and dependency contract |
| `02-voting-stacking-and-selection.ipynb` | When can heterogeneous models be combined without leaking training performance into the meta-model? | Leakage-safe out-of-fold stack and champion–challenger promotion gate |

Read the [Part II student guide](../PART_II_STUDENT_GUIDE.md) and textbook
Chapter 16 alongside these laboratories. Notebook 00 is the essential route;
notebooks 01 and 02 complete the three-hour lecture and may continue into the
next class meeting. No notebook listed in this table remains planned: all three
files are released and tested.

## Durable code and real data

- `src/rice_dsm/ml/ensembles.py` contains reproducible bootstrap sampling, an
  inspectable random-forest classifier with OOB probabilities, and a
  from-scratch squared-error gradient-boosting regressor with staged outputs.
- `tests/test_ensembles.py` verifies mathematical behavior, reproducibility,
  probability contracts, OOB evidence, failure modes, and trusted-library
  agreement.
- `data/course_datasets.sqlite` supplies the Wisconsin Diagnostic Breast Cancer,
  diabetes-progression, and UCI Wine observations used by the three notebooks.

The course implementations expose mechanism and testable state. The notebooks
also use mature scikit-learn estimators to distinguish an instructional
implementation from a production dependency.

## Companion-project boundary

In the [student project template](https://github.com/RandyRDavila/Data-Science-Machine-Learning-Project-Template),
reusable ensemble code belongs under `src/dsm_project/algorithms/student/`,
behavior tests under `tests/`, small lawful CI data under `data/fixtures/`, and
full student-supplied data under ignored `data/local/`. Applied notebooks import
the package, answer a real scientific or operational question, and report the
cost of added model complexity.

## Focused verification

```bash
uv run ruff check src/rice_dsm/ml/ensembles.py tests/test_ensembles.py
uv run pytest tests/test_ensembles.py tests/test_ensemble_teaching.py -q
```
