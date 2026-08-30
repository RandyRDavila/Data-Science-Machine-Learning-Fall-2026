"""Contracts for Lecture 3's projects, environments, and versions lesson."""

import ast
from pathlib import Path

import nbformat

PROJECT_ROOT = Path(__file__).parents[1]
NOTEBOOK_PATH = (
    PROJECT_ROOT
    / "notebooks"
    / "lecture-03-packages-numpy-pandas"
    / "00-projects-environments-and-packaging.ipynb"
)

PUBLIC_FUNCTIONS = {
    "find_project_root",
    "observe_versions",
    "sha256_file",
    "collect_environment_manifest",
    "environment_health",
    "partition_version_observations",
}


def notebook() -> nbformat.NotebookNode:
    """Load the project-environment notebook."""

    return nbformat.read(NOTEBOOK_PATH, as_version=4)


def definitions() -> tuple[dict[str, ast.ClassDef], dict[str, ast.FunctionDef]]:
    """Collect top-level classes and functions from notebook code cells."""

    classes: dict[str, ast.ClassDef] = {}
    functions: dict[str, ast.FunctionDef] = {}
    for cell in notebook().cells:
        if cell.cell_type != "code":
            continue
        tree = ast.parse(cell.source)
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                classes[node.name] = node
            elif isinstance(node, ast.FunctionDef):
                functions[node.name] = node
    return classes, functions


def test_notebook_builds_version_and_environment_evidence_models() -> None:
    classes, functions = definitions()

    assert {"VersionObservation", "EnvironmentManifest"} <= classes.keys()
    assert functions.keys() >= PUBLIC_FUNCTIONS


def test_public_functions_have_numpy_style_docs_and_annotations() -> None:
    _, functions = definitions()

    for name in PUBLIC_FUNCTIONS:
        function = functions[name]
        parameters = [*function.args.posonlyargs, *function.args.args]
        parameters.extend(function.args.kwonlyargs)
        docstring = ast.get_docstring(function)

        assert docstring is not None
        assert "Parameters\n----------" in docstring
        assert "Returns\n-------" in docstring
        assert all(parameter.annotation is not None for parameter in parameters)
        assert function.returns is not None


def test_notebook_distinguishes_all_version_and_packaging_layers() -> None:
    narrative_text = "\n".join(
        cell.source for cell in notebook().cells if cell.cell_type == "markdown"
    ).lower()
    narrative = " ".join(narrative_text.split())

    for phrase in (
        "declared, locked, installed, imported, and running",
        "distribution package",
        "import package",
        "transitive dependency",
        "universal lockfile",
        "editable installation",
        "selected jupyter kernel",
        "sys.prefix",
    ):
        assert phrase in narrative


def test_notebook_teaches_current_uv_sync_boundaries() -> None:
    narrative_text = "\n".join(
        cell.source for cell in notebook().cells if cell.cell_type == "markdown"
    ).lower()
    narrative = " ".join(narrative_text.split())

    for phrase in (
        "uv sync` is **exact** by default",
        "uv run` is **inexact** by default",
        "uv sync --locked",
        "uv lock --check",
        "do not hand-edit",
        "adding is a design change",
        "supply-chain risk",
    ):
        assert phrase in narrative


def test_manifest_scope_names_major_reproducibility_limits() -> None:
    narrative_text = "\n".join(
        cell.source for cell in notebook().cells if cell.cell_type == "markdown"
    ).lower()
    narrative = " ".join(narrative_text.split())

    for concept in (
        "git commit",
        "uncommitted changes",
        "input-data",
        "random seeds",
        "cpu",
        "gpu",
        "scientific question",
    ):
        assert concept in narrative


def test_subprocess_example_is_cross_platform_and_avoids_shell() -> None:
    for cell in notebook().cells:
        if cell.cell_type != "code":
            continue
        tree = ast.parse(cell.source)
        for call in (
            node for node in ast.walk(tree) if isinstance(node, ast.Call)
        ):
            if not (
                isinstance(call.func, ast.Attribute)
                and isinstance(call.func.value, ast.Name)
                and call.func.value.id == "subprocess"
                and call.func.attr == "run"
            ):
                continue
            assert isinstance(call.args[0], ast.List)
            assert not any(
                keyword.arg == "shell"
                and isinstance(keyword.value, ast.Constant)
                and keyword.value.value is True
                for keyword in call.keywords
            )


def test_notebook_contains_no_personal_absolute_paths() -> None:
    complete_text = "\n".join(cell.source for cell in notebook().cells)

    assert "/Users/" not in complete_text
    assert "C:\\Users\\" not in complete_text
