# Lecture 13: Nearest Neighbors from Mathematics to Product Evidence

This unit develops one algorithm family across three tasks and two repository
contexts. Students first derive and test nearest-neighbor search, then apply it
to real classification and regression data, and finally build an item-item
MovieLens recommender while mapping each artifact into the companion final
project template.

## Current student route

Before class, refresh a clean `main` from the repository root:

```bash
uv run --locked python scripts/refresh_course.py
```

Open the repository folder in VS Code, select the **Rice DSM** kernel, and run
the notebooks in order. The core route is designed for one long meeting; the
practice and extension cells can become laboratory or project work.
The [Part II student guide](../PART_II_STUDENT_GUIDE.md) explains how this
released unit fits the broader supervised-learning route; later units remain
planned until their directories and completion evidence are published.

| Notebook | Central question | Professional artifact |
| --- | --- | --- |
| `00-nearest-neighbor-mathematics-and-api.ipynb` | How do representation, distance, voting, and local averaging become a trustworthy estimator? | Typed package API and analytic/failure test plan |
| `01-knn-classification-and-regression.ipynb` | How should $k$ and preprocessing be selected on real chemistry and clinical data? | Leakage-safe selection and held-out evidence report |
| `02-knn-recommendation-and-project-handoff.ipynb` | How does behavioral similarity become recommendation, and where does each artifact live in a student project? | MovieLens evaluation plus template implementation map |

## Durable code and data

- `src/rice_dsm/ml/neighbors.py` contains the inspectable classifier,
  regressor, and collaborative-filtering implementation.
- `tests/test_nearest_neighbors.py` specifies hand-computable mathematics,
  fitted-state behavior, invalid inputs, exact matches, and recommendation
  invariants.
- `data/course_datasets.sqlite` supplies the versioned wine and diabetes
  observations.
- `data/lecture_13_movielens/` is a deterministic authentic subset of the
  GroupLens MovieLens development data; provenance and license conditions are
  recorded in `data/README.md`.

The notebook is the experimental narrative, not the implementation's only
home. Students reproduce this boundary in their own repositories under
`src/dsm_project/algorithms/student/`, `tests/`, `data/local/`,
`data/fixtures/`, and a question-led applied notebook.

## Focused verification

```bash
uv run ruff check src/rice_dsm/ml/neighbors.py tests/test_nearest_neighbors.py
uv run pytest tests/test_nearest_neighbors.py -q
```
