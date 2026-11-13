"""Instructional contracts for the Lecture 15 ensemble-learning sequence."""

from pathlib import Path

import nbformat

PROJECT_ROOT = Path(__file__).parents[1]
LECTURE_ROOT = PROJECT_ROOT / "notebooks" / "lecture-15-ensemble-learning"
NOTEBOOKS = [
    LECTURE_ROOT / "00-random-forests.ipynb",
    LECTURE_ROOT / "01-boosting.ipynb",
    LECTURE_ROOT / "02-voting-stacking-and-selection.ipynb",
]


def notebook_text(path: Path, cell_type: str | None = None) -> str:
    notebook = nbformat.read(path, as_version=4)
    return "\n".join(
        cell.source
        for cell in notebook.cells
        if cell_type is None or cell.cell_type == cell_type
    )


def test_released_sequence_contains_three_question_led_notebooks() -> None:
    assert all(path.is_file() for path in NOTEBOOKS)
    assert sorted(LECTURE_ROOT.glob("*.ipynb")) == NOTEBOOKS


def test_forest_notebook_derives_and_evaluates_randomized_averaging() -> None:
    narrative = notebook_text(NOTEBOOKS[0], "markdown").lower()
    code = notebook_text(NOTEBOOKS[0], "code")
    for concept in (
        "bagging", "random forest", "extra trees", "bootstrap", "63.2",
        "out of bag", "correlation", "variance", "calibration",
        "permutation importance", "causal", "companion student template",
        "student contribution test plan",
    ):
        assert concept in narrative
    for implementation in (
        "breast_cancer_observations", "RandomForestClassifier",
        "BaggingClassifier", "ExtraTreesClassifier", "bootstrap_indices",
        "oob_decision_function_", "permutation_importance", "CalibrationDisplay",
    ):
        assert implementation in code


def test_boosting_notebook_derives_stagewise_loss_optimization() -> None:
    narrative = notebook_text(NOTEBOOKS[1], "markdown").lower()
    code = notebook_text(NOTEBOOKS[1], "code")
    for concept in (
        "additive model", "negative gradient", "residual", "shrinkage",
        "adaboost", "logistic loss", "early stopping", "histogram",
        "xgboost", "lightgbm", "catboost", "student contribution test plan",
    ):
        assert concept in narrative
    for implementation in (
        "diabetes_observations", "SquaredErrorGradientBoostingRegressor",
        "AdaBoostClassifier", "HistGradientBoostingRegressor", "staged_predict",
        "training_loss_", "mean_squared_error",
    ):
        assert implementation in code


def test_stacking_notebook_constructs_leakage_safe_oof_features() -> None:
    narrative = notebook_text(NOTEBOOKS[2], "markdown").lower()
    code = notebook_text(NOTEBOOKS[2], "code")
    for concept in (
        "hard voting", "soft voting", "out-of-fold", "leakage", "class order",
        "calibration", "champion", "challenger", "promotion gate",
        "operational cost", "student contribution test plan",
    ):
        assert concept in narrative
    for implementation in (
        "wine_observations", "VotingClassifier", "cross_val_predict",
        'method="predict_proba"', "X_meta_train", "LogisticRegression",
        "classification_report",
    ):
        assert implementation in code


def test_notebooks_import_package_code_and_explain_long_code_cells() -> None:
    combined_code = "\n".join(notebook_text(path, "code") for path in NOTEBOOKS)
    assert "from rice_dsm.ml.ensembles import" in combined_code
    for path in NOTEBOOKS:
        notebook = nbformat.read(path, as_version=4)
        for cell in notebook.cells:
            if cell.cell_type != "code":
                continue
            lines = [line for line in cell.source.splitlines() if line.strip()]
            if len(lines) < 8:
                continue
            comments = [line for line in lines if line.lstrip().startswith("#")]
            assert comments, f"{path.name}: nontrivial code needs a comment"
            if len(lines) >= 20:
                assert len(comments) >= 2, (
                    f"{path.name}: long code should explain multiple stages"
                )
