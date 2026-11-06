"""Instructional contracts for the Lecture 14 decision-tree sequence."""

from pathlib import Path

import nbformat

PROJECT_ROOT = Path(__file__).parents[1]
LECTURE_ROOT = PROJECT_ROOT / "notebooks" / "lecture-14-decision-trees"
NOTEBOOKS = [
    LECTURE_ROOT / "00-classification-trees.ipynb",
    LECTURE_ROOT / "01-regression-trees.ipynb",
]


def notebook_text(path: Path, cell_type: str | None = None) -> str:
    notebook = nbformat.read(path, as_version=4)
    return "\n".join(
        cell.source
        for cell in notebook.cells
        if cell_type is None or cell.cell_type == cell_type
    )


def test_released_sequence_contains_exactly_two_question_led_notebooks() -> None:
    assert all(path.is_file() for path in NOTEBOOKS)
    assert sorted(LECTURE_ROOT.glob("*.ipynb")) == NOTEBOOKS


def test_classification_notebook_derives_and_evaluates_tree_decisions() -> None:
    narrative = notebook_text(NOTEBOOKS[0], "markdown").lower()
    code = notebook_text(NOTEBOOKS[0], "code")

    for concept in (
        "gini impurity",
        "entropy",
        "weighted impurity reduction",
        "greedy",
        "training data",
        "validation data",
        "test data",
        "cost-complexity pruning",
        "balanced accuracy",
        "confusion matrix",
        "probability",
        "stability",
        "causal",
        "threshold",
        "data/fixtures",
        "pull request",
        "companion student template",
        "git switch -c",
        "uv run pytest -q",
        "student contribution test plan",
    ):
        assert concept in narrative
    for implementation in (
        "breast_cancer_observations",
        "DecisionTreeClassifier",
        "gini_impurity",
        "entropy_impurity",
        "DummyClassifier",
        "ConfusionMatrixDisplay",
        "cost_complexity_pruning_path",
        "np.nextafter",
        "plot_tree",
    ):
        assert implementation in code


def test_regression_notebook_derives_and_diagnoses_local_means() -> None:
    narrative = notebook_text(NOTEBOOKS[1], "markdown").lower()
    code = notebook_text(NOTEBOOKS[1], "code")

    for concept in (
        "squared-error reduction",
        "leaf mean",
        "piecewise-constant",
        "mae",
        "rmse",
        "residual",
        "pruning",
        "discontinuity",
        "instability",
        "extrapolate",
        "monitoring",
        "schema",
        "data/local",
        "tests/test_student_trees.py",
        "companion student template",
        "git switch -c",
        "uv run pytest -q",
        "student contribution test plan",
    ):
        assert concept in narrative
    for implementation in (
        "diabetes_observations",
        "DecisionTreeRegressor",
        "mean_squared_impurity",
        "DummyRegressor",
        "cost_complexity_pruning_path",
        "permutation_importance",
        "np.nextafter",
        "plot_tree",
    ):
        assert implementation in code


def test_notebooks_import_package_code_and_explain_nontrivial_code_cells() -> None:
    for path in NOTEBOOKS:
        notebook = nbformat.read(path, as_version=4)
        code = notebook_text(path, "code")
        assert "from rice_dsm.ml.trees import" in code
        instructional_cells = [
            cell
            for cell in notebook.cells
            if cell.cell_type == "code"
            and len([line for line in cell.source.splitlines() if line.strip()]) >= 8
        ]
        assert instructional_cells, path.name
        for cell in instructional_cells:
            comments = [
                line
                for line in cell.source.splitlines()
                if line.lstrip().startswith("#")
            ]
            assert comments, (
                f"{path.name}: nontrivial code needs an explanatory comment"
            )
            if len(cell.source.splitlines()) >= 20:
                assert len(comments) >= 2, (
                    f"{path.name}: long code should explain multiple stages"
                )
