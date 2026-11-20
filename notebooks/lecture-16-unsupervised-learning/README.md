# Lecture 16: Unsupervised Learning and PCA

Lecture 16 opens Part III by asking how useful structure can be learned when a
target is unavailable or deliberately withheld. The unit treats clustering,
dimensionality reduction, and graph/relational data as different objectives,
not interchangeable plotting techniques. Its extended case uses real,
versioned wine-chemistry and handwritten-digit observations from the course
database.

## Current student route

Before class, fully close VS Code notebooks and refresh a clean `main` from the
repository root:

```bash
uv run --no-project --python 3.12.13 python scripts/refresh_course.py
```

Open the repository in VS Code, select the **Rice DSM** kernel, and run:

| Notebook | Central question | Professional artifact |
| --- | --- | --- |
| `00-unsupervised-learning-landscape.ipynb` | What can clustering, dimensionality reduction, and relational representations claim without a supplied target? | Assumption and sensitivity report separating internal geometry from external label audits |
| `01-principal-component-analysis.ipynb` | When does an optimal linear low-rank representation preserve scientific or predictive value? | Leakage-safe PCA + KNN benchmark reporting accuracy, dimension, reconstruction, and prediction cost |

Both notebooks are released, executable without network access, and tested in
CI. Read textbook Chapters 26 and 27 alongside the laboratories. Notebook 00 is
the conceptual opening; notebook 01 supplies the derivation and full supervised
application.
The shared [Part III student guide](../PART_III_STUDENT_GUIDE.md) defines the
evidence checklist and artifact boundary used throughout the new part.

## Durable code and real data

- `src/rice_dsm/ml/decomposition.py` implements an inspectable, SVD-based
  principal-component projector with validation and reconstruction contracts.
- `tests/test_decomposition.py` verifies orthogonality, centered scores,
  reconstruction behavior, deterministic display signs, and failure modes.
- `data/course_datasets.sqlite` provides the UCI Wine measurements and the real
  handwritten digits observations used by the notebooks.

The notebooks use labels only for scientific audit or downstream supervised
evaluation. Clustering and PCA are fitted without those labels.

## Companion-project boundary

In the student project template, reusable decomposition or clustering code
belongs under `src/dsm_project/algorithms/student/`, mathematical and interface
contracts belong under `tests/`, lawful small fixtures belong under
`data/fixtures/`, and full student data belong under ignored `data/local/`.
Applied notebooks import the package and tell the evidence story; they do not
become the only copy of the algorithm.

## Focused verification

```bash
uv run ruff check src/rice_dsm/ml/decomposition.py tests/test_decomposition.py
uv run pytest tests/test_decomposition.py tests/test_unsupervised_teaching.py -q
```
