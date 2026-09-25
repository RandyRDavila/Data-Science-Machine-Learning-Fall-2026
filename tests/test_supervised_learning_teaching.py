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


def test_landscape_teaches_data_inspection_before_modeling() -> None:
    narrative = notebook_text(LANDSCAPE, cell_type="markdown").lower()
    code = notebook_text(LANDSCAPE, cell_type="code")

    for purpose in (
        "data discovery",
        "what relations exist",
        "what does one row look like",
        "missingness",
        "why visualize before fitting",
        "target leakage",
        "every plot must answer a named question",
    ):
        assert purpose in narrative
    for diagnostic in (
        "sqlite_master",
        "dataset_columns",
        ".head()",
        ".describe()",
        ".isna()",
        ".nunique()",
        ".is_unique",
        ".hist(",
    ):
        assert diagnostic in code


def test_landscape_long_code_cells_explain_their_stages() -> None:
    notebook = nbformat.read(LANDSCAPE, as_version=4)
    long_code_cells = [
        cell
        for cell in notebook.cells
        if cell.cell_type == "code"
        and len([line for line in cell.source.splitlines() if line.strip()]) >= 20
    ]

    assert len(long_code_cells) >= 6
    for cell in long_code_cells:
        explanatory_comments = [
            line
            for line in cell.source.splitlines()
            if line.lstrip().startswith("#")
        ]
        assert len(explanatory_comments) >= 3, cell.id


def test_landscape_defines_notation_before_using_it() -> None:
    narrative = notebook_text(LANDSCAPE, cell_type="markdown")

    for mathematical_object in (
        r"x_i\in\mathcal X",
        r"y_i\in\mathcal Y",
        r"D=\{(x_i,y_i)\}_{i=1}^n",
        r"\widehat\beta_0",
        r"\operatorname{MAE}",
        r"J(z,\mu)",
        r"v_1=\arg\max",
        r"\widehat Q_t(a)",
    ):
        assert mathematical_object in narrative


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


def test_regression_notebook_inspects_data_before_modeling() -> None:
    narrative = notebook_text(PIPELINE, cell_type="markdown").lower()
    code = notebook_text(PIPELINE, cell_type="code")

    for purpose in (
        "five-row preview",
        "structural checks",
        "target-guided exploration",
        "test envelope",
        "coefficient plot",
        "not a universal feature-importance ranking",
        "every plot",
    ):
        assert purpose in narrative
    for diagnostic in (
        "sqlite_master",
        "dataset_columns",
        ".head()",
        ".describe()",
        ".isna()",
        ".nunique()",
        ".is_unique",
        "coefficient_table",
        "metric_examples",
        "normal_equation_error",
    ):
        assert diagnostic in code


def test_regression_notebook_defines_split_and_metric_examples() -> None:
    narrative = notebook_text(PIPELINE, cell_type="markdown")
    code = notebook_text(PIPELINE, cell_type="code")

    for mathematical_object in (
        r"\mathcal D_{\mathrm{train}}",
        r"\mathcal D_{\mathrm{validation}}",
        r"\mathcal D_{\mathrm{test}}",
        r"\widehat f_0(x)",
        r"X^T\bigl(\boldsymbol y-X\widehat{\boldsymbol\beta}\bigr)",
    ):
        assert mathematical_object in narrative
    for visual_example in (
        "ax.vlines",
        "metric_examples.plot.bar",
        "coefficient_table[\"standardized_coefficient\"]",
    ):
        assert visual_example in code


def test_regression_long_code_cells_explain_their_stages() -> None:
    notebook = nbformat.read(PIPELINE, as_version=4)
    long_code_cells = [
        cell
        for cell in notebook.cells
        if cell.cell_type == "code"
        and len([line for line in cell.source.splitlines() if line.strip()]) >= 20
    ]

    assert len(long_code_cells) >= 10
    for cell in long_code_cells:
        explanatory_comments = [
            line
            for line in cell.source.splitlines()
            if line.lstrip().startswith("#")
        ]
        assert len(explanatory_comments) >= 3, cell.id


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
        "first-order method",
        "second-order method",
        "representation equivalence",
        "training equivalence",
        "polyak",
        "heavy-ball",
        "nesterov",
        "look-ahead",
        "adagrad",
        "adam",
        "back-propagation",
        "gradient noise",
        "updates per epoch",
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
        "linear_neuron_mse",
        "fit_linear_neuron_with_batches",
        "sampling_traces",
        "run_first_order_method",
        "narrow_valley_objective",
        "accelerated_histories",
    ):
        assert implementation in code


def test_gradient_notebook_inspects_data_and_proves_neuron_equivalence() -> None:
    narrative = notebook_text(GRADIENT, cell_type="markdown").lower()
    code = notebook_text(GRADIENT, cell_type="code")

    for explanation in (
        "inspect the course data dictionary",
        "preview the two queried columns",
        "identity activation",
        "same function class",
        "same squared-error objective",
        "optimizer is not part of the model definition",
        "differentiation procedure, not a particular optimizer",
    ):
        assert explanation in narrative
    for implementation in (
        "dataset_columns",
        ".head()",
        ".describe()",
        ".isna()",
        "np.linalg.lstsq",
        "LinearRegression",
        "neuron_test_prediction",
        "reference_test_prediction",
    ):
        assert implementation in code


def test_gradient_notebook_compares_sampling_and_acceleration_methods() -> None:
    narrative = notebook_text(GRADIENT, cell_type="markdown")
    code = notebook_text(GRADIENT, cell_type="code")

    for mathematical_object in (
        r"g_{B_t}(\theta_t)",
        r"v_{t+1}=\gamma v_t-\eta\nabla J(\theta_t)",
        r"\nabla J(\theta_t+\gamma v_t)",
        r"\widehat y=\boldsymbol\theta^T\widetilde{\boldsymbol x}",
    ):
        assert mathematical_object in narrative
    for comparison in (
        '"batch (331 rows)"',
        '"mini-batch (32 rows)"',
        '"stochastic (1 row)"',
        '"gradient descent"',
        '"heavy-ball"',
        '"look-ahead"',
    ):
        assert comparison in code


def test_gradient_notebook_cites_primary_optimizer_sources() -> None:
    narrative = notebook_text(GRADIENT, cell_type="markdown")

    for source in (
        "10.1214/aoms/1177729586",
        "10.1016/0041-5553(64)90137-5",
        "mathnet.ru/eng/dan46009",
        "10.1038/323533a0",
        "jmlr.org/papers/v12/duchi11a.html",
        "arxiv.org/abs/1412.6980",
    ):
        assert source in narrative


def test_gradient_long_code_cells_explain_their_stages() -> None:
    notebook = nbformat.read(GRADIENT, as_version=4)
    long_code_cells = [
        cell
        for cell in notebook.cells
        if cell.cell_type == "code"
        and len([line for line in cell.source.splitlines() if line.strip()]) >= 20
    ]

    assert len(long_code_cells) >= 10
    for cell in long_code_cells:
        explanatory_comments = [
            line
            for line in cell.source.splitlines()
            if line.lstrip().startswith("#")
        ]
        assert len(explanatory_comments) >= 3, cell.id


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
