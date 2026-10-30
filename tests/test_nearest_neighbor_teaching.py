"""Instructional contracts for the Lecture 13 nearest-neighbor sequence."""

from pathlib import Path

import nbformat

PROJECT_ROOT = Path(__file__).parents[1]
LECTURE_ROOT = PROJECT_ROOT / "notebooks" / "lecture-13-nearest-neighbors"
NOTEBOOKS = [
    LECTURE_ROOT / "00-nearest-neighbor-mathematics-and-api.ipynb",
    LECTURE_ROOT / "01-knn-classification-and-regression.ipynb",
    LECTURE_ROOT / "02-knn-recommendation-and-project-handoff.ipynb",
]


def notebook_text(path: Path, cell_type: str | None = None) -> str:
    notebook = nbformat.read(path, as_version=4)
    return "\n".join(
        cell.source
        for cell in notebook.cells
        if cell_type is None or cell.cell_type == cell_type
    )


def test_released_sequence_replaces_geometric_placeholder() -> None:
    assert all(path.is_file() for path in NOTEBOOKS)
    assert not (PROJECT_ROOT / "notebooks" / "lecture-13-geometric-learning").exists()


def test_mathematics_notebook_defines_and_tests_the_algorithm() -> None:
    narrative = notebook_text(NOTEBOOKS[0], "markdown").lower()
    code = notebook_text(NOTEBOOKS[0], "code")

    for concept in (
        "minkowski",
        "manhattan",
        "euclidean",
        "classification",
        "regression",
        "inverse-distance",
        "exact matches",
        "bias",
        "variance",
        "curse of dimensionality",
        "tie policy",
        "cover and hart",
        "fix and hodges",
    ):
        assert concept in narrative
    for interface in (
        "euclidean_distances",
        "KNearestNeighborsClassifier",
        "KNearestNeighborsRegressor",
        ".kneighbors(",
        ".predict_proba(",
    ):
        assert interface in code


def test_real_data_notebook_owns_split_scaling_and_evaluation_boundaries() -> None:
    narrative = notebook_text(NOTEBOOKS[1], "markdown").lower()
    code = notebook_text(NOTEBOOKS[1], "code")

    for concept in (
        "training",
        "validation",
        "test",
        "leak",
        "majority-class baseline",
        "confusion matrix",
        "mae",
        "rmse",
        "latency",
        "support",
        "trusted-library",
    ):
        assert concept in narrative
    for implementation in (
        "course_database_path",
        "wine_observations",
        "diabetes_observations",
        "StandardScaler().fit(X_train)",
        "DummyClassifier",
        "ConfusionMatrixDisplay",
        "SklearnKNNClassifier",
        "perf_counter",
    ):
        assert implementation in code


def test_recommender_notebook_uses_real_events_and_teaches_project_handoff() -> None:
    narrative = notebook_text(NOTEBOOKS[2], "markdown").lower()
    code = notebook_text(NOTEBOOKS[2], "code")

    for concept in (
        "authentic anonymized movielens",
        "collaborative filtering",
        "missing does not mean negative",
        "temporal holdout",
        "recall@",
        "catalog coverage",
        "popularity baseline",
        "feedback loops",
        "data/local",
        "data/fixtures",
        "src/dsm_project/algorithms/student/neighbors.py",
        "tests/test_student_neighbors.py",
        "dataset_card",
        "pull request",
    ):
        assert concept in narrative
    for implementation in (
        "movielens_teaching_directory",
        "ItemKNNRecommender",
        "13_817",
        "recommended_ids.isdisjoint(seen_ids)",
        "popularity_hits",
    ):
        assert implementation in code


def test_long_code_cells_explain_their_stages() -> None:
    for path in NOTEBOOKS:
        notebook = nbformat.read(path, as_version=4)
        long_cells = [
            cell
            for cell in notebook.cells
            if cell.cell_type == "code"
            and len([line for line in cell.source.splitlines() if line.strip()]) >= 24
        ]
        assert long_cells, path.name
        for cell in long_cells:
            comments = [
                line
                for line in cell.source.splitlines()
                if line.lstrip().startswith("#")
            ]
            assert len(comments) >= 1, f"{path.name}: {cell.id} needs a stage comment"
