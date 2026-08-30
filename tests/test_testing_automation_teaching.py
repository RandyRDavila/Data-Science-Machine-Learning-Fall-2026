"""Contracts for Lecture 3's testing and automation lesson."""

import ast
from pathlib import Path

import nbformat

PROJECT_ROOT = Path(__file__).parents[1]
LECTURE_DIRECTORY = (
    PROJECT_ROOT / "notebooks" / "lecture-03-projects-packages-testing"
)
NOTEBOOK_PATH = LECTURE_DIRECTORY / "02-testing-and-automation.ipynb"
METRICS_PATH = PROJECT_ROOT / "src" / "rice_dsm" / "metrics.py"


def notebook() -> nbformat.NotebookNode:
    """Load the testing and automation notebook."""

    return nbformat.read(NOTEBOOK_PATH, as_version=4)


def notebook_trees() -> list[ast.Module]:
    """Parse each code cell independently, as Jupyter does."""

    return [
        ast.parse(cell.source)
        for cell in notebook().cells
        if cell.cell_type == "code"
    ]


def normalized_narrative() -> str:
    """Return normalized lowercase Markdown for conceptual assertions."""

    markdown = "\n".join(
        cell.source for cell in notebook().cells if cell.cell_type == "markdown"
    )
    return " ".join(markdown.lower().split())


def code_text() -> str:
    """Return all executable examples as one searchable string."""

    return "\n".join(
        cell.source for cell in notebook().cells if cell.cell_type == "code"
    )


def test_testing_lesson_is_promoted_to_notebook_02() -> None:
    assert NOTEBOOK_PATH.is_file()
    assert not (
        LECTURE_DIRECTORY / "06-testing-as-executable-specification.ipynb"
    ).exists()


def test_notebook_distinguishes_scope_purpose_and_oracle_strategies() -> None:
    narrative = normalized_narrative()

    for concept in (
        "verification",
        "validation",
        "test oracle",
        "unit test",
        "component",
        "integration test",
        "contract",
        "system/end-to-end",
        "smoke",
        "acceptance",
        "regression",
        "performance",
        "security",
        "property-based",
        "metamorphic",
        "differential testing",
        "fuzzing",
        "mutation testing",
        "snapshot",
        "golden-file",
        "doctest",
    ):
        assert concept in narrative


def test_notebook_teaches_pytest_through_executable_examples() -> None:
    source = code_text()

    for example in (
        "pytest.raises",
        "pytest.approx",
        "TemporaryDirectory",
        "Mock(",
        "doctest.testmod(metrics, verbose=False)",
        "RICE_DSM_RUNNING_NOTEBOOK_TESTS",
        '"-m",\n            "pytest"',
    ):
        assert example in source

    subprocess_calls = [
        node
        for tree in notebook_trees()
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
        and node.func.attr == "run"
    ]
    assert subprocess_calls
    assert all(isinstance(call.args[0], ast.List) for call in subprocess_calls)


def test_notebook_covers_data_and_ml_specific_failure_modes() -> None:
    narrative = normalized_narrative()

    for concept in (
        "schema validity is not scientific validity",
        "leakage",
        "stochastic",
        "calibration",
        "serialization",
        "model-quality thresholds",
        "data-drift",
        "slices",
    ):
        assert concept in narrative


def test_notebook_distinguishes_ci_delivery_and_deployment() -> None:
    narrative = normalized_narrative()
    source = code_text()

    for concept in (
        "continuous integration",
        "continuous delivery",
        "continuous deployment",
        "immutable artifact",
        "approval/policy gate",
        "monitoring",
        "rollback",
        "least-privilege permissions",
    ):
        assert concept in narrative

    assert 'project_root / ".github" / "workflows" / "course-ci.yml"' in source
    for platform in ("ubuntu-latest", "macos-latest", "windows-latest"):
        assert platform in source


def test_notebook_helpers_are_documented_and_annotated() -> None:
    functions = {
        node.name: node
        for tree in notebook_trees()
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }

    for name in (
        "find_project_root",
        "publish_alert_if_large_error",
        "assert_disjoint_identifiers",
    ):
        function = functions[name]
        docstring = ast.get_docstring(function)
        assert docstring is not None
        assert "Parameters\n----------" in docstring
        assert all(argument.annotation is not None for argument in function.args.args)
        assert function.returns is not None


def test_scientific_metrics_supply_real_doctestable_package_behavior() -> None:
    module = ast.parse(METRICS_PATH.read_text(encoding="utf-8"))
    public_functions = {
        node.name: node
        for node in module.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    }

    assert {
        "mean_absolute_error",
        "root_mean_squared_error",
    } <= public_functions.keys()
    for function in public_functions.values():
        docstring = ast.get_docstring(function)
        assert docstring is not None
        assert "Parameters\n----------" in docstring
        assert "Returns\n-------" in docstring
        assert "Examples\n--------" in docstring
        assert ">>>" in docstring
