"""Contracts for Lecture 4's NumPy and pandas introduction."""

import ast
import tomllib
from pathlib import Path

import nbformat

PROJECT_ROOT = Path(__file__).parents[1]
NOTEBOOK_PATH = (
    PROJECT_ROOT
    / "notebooks"
    / "lecture-04-numpy-pandas"
    / "00-introducing-numpy-and-pandas.ipynb"
)


def notebook() -> nbformat.NotebookNode:
    """Load the NumPy and pandas introduction."""

    return nbformat.read(NOTEBOOK_PATH, as_version=4)


def notebook_trees() -> list[ast.Module]:
    """Parse each code cell independently."""

    return [
        ast.parse(cell.source)
        for cell in notebook().cells
        if cell.cell_type == "code"
    ]


def narrative() -> str:
    """Return normalized lowercase instructional prose."""

    markdown = "\n".join(
        cell.source for cell in notebook().cells if cell.cell_type == "markdown"
    )
    return " ".join(markdown.lower().split())


def code_text() -> str:
    """Return all notebook code for executable-contract checks."""

    return "\n".join(
        cell.source for cell in notebook().cells if cell.cell_type == "code"
    )


def test_numpy_and_pandas_are_locked_project_dependencies() -> None:
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)

    declared = project["project"]["dependencies"]
    assert any(requirement.startswith("numpy>=") for requirement in declared)
    assert any(requirement.startswith("pandas>=") for requirement in declared)

    lock_text = (PROJECT_ROOT / "uv.lock").read_text(encoding="utf-8")
    assert 'name = "numpy"' in lock_text
    assert 'name = "pandas"' in lock_text


def test_notebook_teaches_the_array_mental_model_and_failure_modes() -> None:
    lesson = narrative()

    for concept in (
        "data buffer plus metadata",
        "axis number is not inherently",
        "dtype is a storage and numerical contract",
        "ragged",
        "boolean mask",
        "advanced indexing",
        "views, copies, and mutation",
        "universal function",
        "broadcasting aligns shapes from the trailing axes",
        "reduce along axis 0",
        "floating-point comparisons",
        "missing numerical values are policy",
    ):
        assert concept in lesson


def test_notebook_teaches_labels_as_semantics_not_decoration() -> None:
    lesson = narrative()

    for concept in (
        "series",
        "dataframe",
        "index",
        ".loc` uses labels",
        ".iloc` uses integer positions",
        "aligns by labels",
        "equal-length pandas `series`",
        "valid count",
        "split–apply–combine",
        "long and wide forms",
        "joining tables must state cardinality",
        "resulting array does not retain column or row labels",
        "copy-on-write",
    ):
        assert concept in lesson


def test_notebook_uses_real_numpy_and_pandas_mechanics() -> None:
    source = code_text()

    for example in (
        "np.array(",
        "np.arange(",
        "np.linspace(",
        "np.shares_memory(",
        "np.allclose(",
        "np.newaxis",
        ".loc[",
        ".iloc[",
        ".groupby(",
        ".pivot(",
        'validate="many_to_one"',
        ".to_numpy(",
        "pd.util.hash_pandas_object(",
    ):
        assert example in source


def test_worked_example_preserves_scientific_meaning_and_missingness() -> None:
    lesson = narrative()
    source = code_text()

    for concept in (
        "heat-diffusion experiment",
        "deterministic and synthetic",
        "not evidence about real copper or aluminum",
        "physical unit",
        "quality flag",
        "sensor dropout",
        "scientific validity",
        "leaks information",
    ):
        assert concept in lesson

    assert 'measurements.shape == (24, 6)' in source
    assert '"sensor_dropout"' in source
    assert 'measurements["temperature_c"].isna().sum() == 1' in source


def test_standardization_interface_is_documented_annotated_and_validated() -> None:
    functions = {
        node.name: node
        for tree in notebook_trees()
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }
    function = functions["standardize_feature_matrix"]
    docstring = ast.get_docstring(function)

    assert docstring is not None
    for section in (
        "Parameters\n----------",
        "Returns\n-------",
        "Raises\n------",
        "Notes\n-----",
    ):
        assert section in docstring
    assert all(argument.annotation is not None for argument in function.args.args)
    assert function.returns is not None

    raises = [
        node
        for node in ast.walk(function)
        if isinstance(node, ast.Raise)
    ]
    assert len(raises) >= 5


def test_random_example_uses_a_local_seeded_generator() -> None:
    source = code_text()

    assert "np.random.default_rng(seed=577)" in source
    assert "np.random.seed(" not in source


def test_notebook_contains_no_personal_paths_or_hidden_file_dependency() -> None:
    complete_text = "\n".join(cell.source for cell in notebook().cells)

    assert "/Users/" not in complete_text
    assert "C:\\Users\\" not in complete_text
    assert "read_csv(" not in code_text()
