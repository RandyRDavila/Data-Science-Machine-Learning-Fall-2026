"""Instructional contracts for the opening supervised-learning sequence."""

from pathlib import Path

import nbformat

PROJECT_ROOT = Path(__file__).parents[1]
LECTURE_09 = PROJECT_ROOT / "notebooks" / "lecture-09-supervised-learning-systems"
LECTURE_10 = (
    PROJECT_ROOT / "notebooks" / "lecture-10-linear-regression-regularization"
)
LANDSCAPE = LECTURE_09 / "00-machine-learning-landscape.ipynb"
PIPELINE = LECTURE_09 / "01-supervised-learning-linear-regression.ipynb"
GRADIENT = LECTURE_10 / "00-gradient-descent-from-functions-to-neuron.ipynb"
TEXTBOOK_CHAPTERS = PROJECT_ROOT / "textbook" / "chapters"


def notebook_text(path: Path, *, cell_type: str | None = None) -> str:
    """Return normalized source text from selected notebook cells."""

    notebook = nbformat.read(path, as_version=4)
    return "\n".join(
        cell.source
        for cell in notebook.cells
        if cell_type is None or cell.cell_type == cell_type
    )


def test_released_notebook_sequence_replaces_placeholder_files() -> None:
    assert LANDSCAPE.is_file()
    assert PIPELINE.is_file()
    assert GRADIENT.is_file()
    assert not (LECTURE_09 / "00-supervised-learning-contract.ipynb").exists()
    assert not (LECTURE_10 / "00-affine-model-and-least-squares.ipynb").exists()


def test_machine_learning_landscape_distinguishes_feedback_signals() -> None:
    narrative = notebook_text(LANDSCAPE, cell_type="markdown").lower()
    code = notebook_text(LANDSCAPE, cell_type="code")

    for concept in (
        "supervised learning",
        "unsupervised learning",
        "reinforcement learning",
        "semi-supervised learning",
        "self-supervised learning",
        "generative modeling",
        "active learning",
        "deep learning",
        "regression",
        "classification",
        "clustering",
        "dimensionality reduction",
        "causal",
        "inductive bias",
        "hypothesis class",
        "empirical risk",
        "turing",
        "samuel",
        "rosenblatt",
    ):
        assert concept in narrative
    for interface in (
        "LinearRegression",
        "LogisticRegression",
        "KMeans",
        "PCA",
        "fit_predict",
        "fit_transform",
    ):
        assert interface in code


def test_opening_sequence_uses_real_documented_datasets() -> None:
    landscape = notebook_text(LANDSCAPE)
    regression = notebook_text(PIPELINE)
    gradient = notebook_text(GRADIENT)
    builder = (PROJECT_ROOT / "scripts" / "build_course_database.py").read_text(
        encoding="utf-8"
    )

    for loader in (
        "load_diabetes",
        "load_breast_cancer",
        "load_wine",
        "load_digits",
    ):
        assert loader in builder
    for source in (
        "UCI Machine Learning Repository",
        "OpenML",
        "Data.gov",
        "NASA Science Data",
        "World Bank Open Data",
    ):
        assert source in landscape
    for notebook_path, notebook_source in zip(
        (LANDSCAPE, PIPELINE, GRADIENT),
        (landscape, regression, gradient),
        strict=True,
    ):
        notebook_code = notebook_text(notebook_path, cell_type="code")
        assert "course_database_path" in notebook_source
        assert 'Path("data/course_datasets.sqlite")' not in notebook_code
        assert ".as_uri()" in notebook_source
        assert "sqlite3.connect" in notebook_source
        assert "mode=ro" in notebook_source
        assert "load_diabetes" not in notebook_source
        assert "INSERT INTO" not in notebook_source
    assert "SELECT * FROM dataset_catalog" in regression
    assert "FROM diabetes_observations" in gradient
    assert "simulation" in landscape.lower()


def test_linear_regression_notebook_teaches_the_complete_pipeline() -> None:
    narrative = notebook_text(PIPELINE, cell_type="markdown").lower()
    code = notebook_text(PIPELINE, cell_type="code")

    for concept in (
        "ordinary least squares",
        "sum of squared errors",
        "normal equations",
        "design matrix",
        "full column rank",
        "prediction time",
        "training data",
        "validation data",
        "test data",
        "baseline",
        "scaling",
        "leakage",
        "mae",
        "rmse",
        "r^2",
        "residual",
        "causal",
        "release evidence",
        "legendre",
        "gauss",
        "conditional mean",
        "pythagorean identity",
        "projection",
    ):
        assert concept in narrative
    for implementation in (
        "np.linalg.lstsq",
        "objective_grid",
        "design_board",
        "train_test_split",
        "DummyRegressor",
        "ColumnTransformer",
        "StandardScaler",
        "Pipeline",
        "LinearRegression",
        "evaluate_regression",
        "raw_condition_number",
        "test_evidence",
    ):
        assert implementation in code


def test_gradient_notebook_builds_from_calculus_to_linear_neuron() -> None:
    narrative = notebook_text(GRADIENT, cell_type="markdown").lower()
    code = notebook_text(GRADIENT, cell_type="code")

    for concept in (
        "function of one variable",
        "functions of multiple variables",
        "local linear approximation",
        "directional derivative",
        "steepest local descent",
        "local sensitivity",
        "learning rate",
        "identity activation",
        "mean squared error",
        "batch gradient descent",
        "stochastic gradient descent",
        "mini-batch gradient descent",
        "automatic differentiation",
        "linear regression",
        "cauchy",
        "robbins",
        "eigenvector",
        "condition number",
    ):
        assert concept in narrative
    for implementation in (
        "scalar_gradient",
        "gradient_descent_1d",
        "vector_gradient",
        "finite_difference_gradient",
        "loss_surface",
        "parameter_history",
        "fit_linear_neuron",
        "weight_gradient",
        "bias_gradient",
        "LinearRegression",
        "raw_hessian",
        "scaled_hessian",
    ):
        assert implementation in code


def test_textbook_separates_the_four_opening_mathematical_arguments() -> None:
    chapters = {
        "foundations": TEXTBOOK_CHAPTERS / "09-machine-learning-foundations.tex",
        "supervised": TEXTBOOK_CHAPTERS / "10-supervised-learning-systems.tex",
        "regression": TEXTBOOK_CHAPTERS / "11-linear-regression.tex",
        "gradient": TEXTBOOK_CHAPTERS / "12-gradient-descent.tex",
    }
    sources = {
        name: path.read_text(encoding="utf-8").lower()
        for name, path in chapters.items()
    }

    for required in (
        "inductive bias",
        "hypothesis class",
        "samuel",
        "application",
    ):
        assert required in sources["foundations"]
    for required in (
        "conditional mean",
        "bias-variance",
        "approximation",
        "target-generation process",
    ):
        assert required in sources["supervised"]
    for required in (
        "legendre",
        "gauss",
        "pythagorean",
        "gauss-markov",
        "moore-penrose",
    ):
        assert required in sources["regression"]
    for required in (
        "cauchy",
        "robbins",
        "directional derivative",
        "condition number",
        "stochastic",
    ):
        assert required in sources["gradient"]


def test_unit_guides_name_the_released_route() -> None:
    lecture_09 = (LECTURE_09 / "README.md").read_text(encoding="utf-8")
    lecture_10 = (LECTURE_10 / "README.md").read_text(encoding="utf-8")
    project = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert LANDSCAPE.name in lecture_09
    assert PIPELINE.name in lecture_09
    assert GRADIENT.name in lecture_10
    assert '"scikit-learn>=1.9.1"' in project


def test_public_course_map_describes_the_released_sequence() -> None:
    course_map = (PROJECT_ROOT / "site" / "course-map.html").read_text(
        encoding="utf-8"
    )

    assert "ML landscape and supervised learning" in course_map
    assert "complete first regression pipeline" in course_map
    assert "Gradient descent and the linear neuron" in course_map
    assert "single-neuron bridge" in course_map
