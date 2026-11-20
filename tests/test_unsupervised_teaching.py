"""Instructional contracts for the Lecture 16 unsupervised-learning sequence."""

from pathlib import Path

import nbformat

PROJECT_ROOT = Path(__file__).parents[1]
LECTURE_ROOT = PROJECT_ROOT / "notebooks" / "lecture-16-unsupervised-learning"
NOTEBOOKS = [
    LECTURE_ROOT / "00-unsupervised-learning-landscape.ipynb",
    LECTURE_ROOT / "01-principal-component-analysis.ipynb",
]


def notebook_text(path: Path, cell_type: str | None = None) -> str:
    notebook = nbformat.read(path, as_version=4)
    return "\n".join(
        cell.source
        for cell in notebook.cells
        if cell_type is None or cell.cell_type == cell_type
    )


def test_released_sequence_contains_two_question_led_notebooks() -> None:
    assert all(path.is_file() for path in NOTEBOOKS)
    assert sorted(LECTURE_ROOT.glob("*.ipynb")) == NOTEBOOKS


def test_landscape_distinguishes_unsupervised_problem_families() -> None:
    narrative = notebook_text(NOTEBOOKS[0], "markdown").lower()
    code = notebook_text(NOTEBOOKS[0], "code")
    for concept in (
        "clustering",
        "dimensionality reduction",
        "graph and relational",
        "self-supervised",
        "standardization",
        "silhouette",
        "adjusted rand",
        "external audit",
        "arbitrary code",
        "not automatically a scientific discovery",
        "companion student repository",
    ):
        assert concept in narrative
    for implementation in (
        "wine_observations",
        "StandardScaler",
        "KMeans",
        "silhouette_score",
        "adjusted_rand_score",
        "kneighbors_graph",
        "course_database_path",
    ):
        assert implementation in code


def test_pca_notebook_derives_geometry_and_measures_supervised_tradeoffs() -> None:
    narrative = notebook_text(NOTEBOOKS[1], "markdown").lower()
    code = notebook_text(NOTEBOOKS[1], "code")
    for concept in (
        "maximum-variance",
        "minimum-reconstruction",
        "covariance",
        "eigenvector",
        "singular value decomposition",
        "eckart--young--mirsky",
        "whitening",
        "using training data only",
        "explained variance is not predictive value",
        "accuracy",
        "inference cost",
        "performance gain",
    ):
        assert concept in narrative
    for implementation in (
        "digits_observations",
        "PrincipalComponentProjector",
        "np.linalg.svd",
        "PCA",
        "Pipeline",
        "KNeighborsClassifier",
        "perf_counter",
        "cross_val_score",
    ):
        assert implementation in code


def test_notebooks_use_real_local_data_and_comment_nontrivial_code() -> None:
    combined = "\n".join(notebook_text(path, "code") for path in NOTEBOOKS)
    assert "course_datasets.sqlite" not in combined
    assert "course_database_path" in combined
    assert "make_classification" not in combined
    assert "make_blobs" not in combined

    for path in NOTEBOOKS:
        notebook = nbformat.read(path, as_version=4)
        for cell in notebook.cells:
            if cell.cell_type != "code":
                continue
            lines = [line for line in cell.source.splitlines() if line.strip()]
            if len(lines) >= 8:
                assert any(line.lstrip().startswith("#") for line in lines), (
                    f"{path.name}: nontrivial code needs an explanatory comment"
                )


def test_pca_lesson_keeps_fitted_transformations_inside_the_pipeline() -> None:
    code = notebook_text(NOTEBOOKS[1], "code")
    assert '("scale", StandardScaler())' in code
    assert '("pca", PCA(' in code
    assert "train_test_split" in code
    assert "pixels_train" in code
    assert "pixels_test" in code
