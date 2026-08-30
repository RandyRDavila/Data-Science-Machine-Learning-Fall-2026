"""Contracts for Lecture 3's scripts, modules, and packages lesson."""

import ast
import tomllib
from pathlib import Path

import nbformat

PROJECT_ROOT = Path(__file__).parents[1]
NOTEBOOK_PATH = (
    PROJECT_ROOT
    / "notebooks"
    / "lecture-03-projects-packages-testing"
    / "01-scripts-modules-and-packages.ipynb"
)
PACKAGE_DIRECTORY = PROJECT_ROOT / "src" / "rice_dsm"


def notebook() -> nbformat.NotebookNode:
    """Load the scripts, modules, and packages notebook."""

    return nbformat.read(NOTEBOOK_PATH, as_version=4)


def notebook_trees() -> list[ast.Module]:
    """Parse every notebook code cell independently."""

    return [
        ast.parse(cell.source)
        for cell in notebook().cells
        if cell.cell_type == "code"
    ]


def test_refactoring_case_exists_as_real_package_code() -> None:
    expected_files = {
        "__init__.py",
        "__main__.py",
        "cli.py",
        "knowledge_graph.py",
        "records.py",
    }

    assert expected_files <= {path.name for path in PACKAGE_DIRECTORY.glob("*.py")}

    with (PROJECT_ROOT / "pyproject.toml").open(mode="rb") as handle:
        project = tomllib.load(handle)
    assert project["project"]["scripts"]["rice-dsm"] == "rice_dsm.cli:main"


def test_notebook_imports_promoted_graph_instead_of_redefining_it() -> None:
    defined_classes = {
        node.name
        for tree in notebook_trees()
        for node in tree.body
        if isinstance(node, ast.ClassDef)
    }
    imported_names = {
        alias.name
        for tree in notebook_trees()
        for node in tree.body
        if isinstance(node, ast.ImportFrom)
        and node.module == "rice_dsm.knowledge_graph"
        for alias in node.names
    }

    assert "KnowledgeGraph" not in defined_classes
    assert "KnowledgeGraph" in imported_names
    assert "load_knowledge_graph" in imported_names


def test_notebook_teaches_import_mechanics_and_api_boundaries() -> None:
    narrative_text = "\n".join(
        cell.source for cell in notebook().cells if cell.cell_type == "markdown"
    ).lower()
    narrative = " ".join(narrative_text.split())

    for phrase in (
        "first-import execution",
        "sys.modules",
        "top-level side effects",
        "circular imports",
        "partially initialized module",
        "public package interface",
        "conventions, not security",
        "library versus cli contract",
        "exit status",
        "src layout",
    ):
        assert phrase in narrative


def test_notebook_preserves_scientific_and_engineering_roles() -> None:
    narrative_text = "\n".join(
        cell.source for cell in notebook().cells if cell.cell_type == "markdown"
    ).lower()
    narrative = " ".join(narrative_text.split())

    for concept in (
        "scientific question",
        "interpretation",
        "uncertainty",
        "provenance",
        "breadth-first search",
        "domain logic",
        "unit tests",
        "windows, macos, and linux",
    ):
        assert concept in narrative


def test_notebook_exercises_module_cache_main_and_entry_points() -> None:
    code_text = "\n".join(
        cell.source for cell in notebook().cells if cell.cell_type == "code"
    )

    assert 'sys.modules["rice_dsm.knowledge_graph"]' in code_text
    assert 'if __name__ == "__main__"' in code_text
    assert '"-m",\n    "rice_dsm"' in code_text
    assert "distribution.entry_points" in code_text
    assert "pkgutil.iter_modules" in code_text


def test_subprocess_examples_use_argument_lists_without_shell_true() -> None:
    subprocess_calls = []
    for tree in notebook_trees():
        subprocess_calls.extend(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "subprocess"
            and node.func.attr == "run"
        )

    assert len(subprocess_calls) >= 5
    for call in subprocess_calls:
        first_argument = call.args[0]
        assert isinstance(first_argument, (ast.List, ast.Name))
        assert not any(
            keyword.arg == "shell"
            and isinstance(keyword.value, ast.Constant)
            and keyword.value.value is True
            for keyword in call.keywords
        )


def test_notebook_helpers_are_documented_and_annotated() -> None:
    functions = {
        node.name: node
        for tree in notebook_trees()
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }

    for name in ("find_project_root", "module_inventory"):
        function = functions[name]
        docstring = ast.get_docstring(function)
        assert docstring is not None
        assert "Parameters\n----------" in docstring
        assert "Returns\n-------" in docstring
        assert all(argument.annotation is not None for argument in function.args.args)
        assert function.returns is not None
