"""Contracts for the package-quality function-interface lesson."""

import ast
from pathlib import Path

import nbformat

PROJECT_ROOT = Path(__file__).parents[1]
NOTEBOOK_PATH = (
    PROJECT_ROOT
    / "notebooks"
    / "lecture-02-python-foundations-ii"
    / "00-functions-and-functional-patterns.ipynb"
)

NUMPY_DOCUMENTED_FUNCTIONS = {
    "bernoulli_pmf",
    "make_bernoulli_pmf",
    "event_probability",
    "expected_value",
    "validate_finite_pmf",
    "parse_probability",
    "binary_log_loss",
}


def function_definitions() -> dict[str, ast.FunctionDef]:
    """Return every top-level function definition in notebook code cells."""

    notebook = nbformat.read(NOTEBOOK_PATH, as_version=4)
    definitions = {}
    for cell in notebook.cells:
        if cell.cell_type != "code":
            continue
        tree = ast.parse(cell.source)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                definitions[node.name] = node
    return definitions


def test_public_examples_use_numpy_style_docstrings() -> None:
    definitions = function_definitions()

    for function_name in NUMPY_DOCUMENTED_FUNCTIONS:
        docstring = ast.get_docstring(definitions[function_name])
        assert docstring is not None
        assert "Parameters\n----------" in docstring
        assert "Returns\n-------" in docstring


def test_fallible_public_examples_document_raises() -> None:
    definitions = function_definitions()

    for function_name in (
        "bernoulli_pmf",
        "make_bernoulli_pmf",
        "validate_finite_pmf",
        "parse_probability",
        "binary_log_loss",
    ):
        docstring = ast.get_docstring(definitions[function_name])
        assert docstring is not None
        assert "Raises\n------" in docstring


def test_public_examples_have_complete_type_annotations() -> None:
    definitions = function_definitions()

    for function_name in NUMPY_DOCUMENTED_FUNCTIONS:
        function = definitions[function_name]
        parameters = [*function.args.posonlyargs, *function.args.args]
        parameters.extend(function.args.kwonlyargs)

        assert parameters
        assert all(parameter.annotation is not None for parameter in parameters)
        assert function.returns is not None


def test_notebook_teaches_style_typing_and_exceptions_as_one_contract() -> None:
    notebook = nbformat.read(NOTEBOOK_PATH, as_version=4)
    narrative = "\n".join(
        cell.source for cell in notebook.cells if cell.cell_type == "markdown"
    )

    for required_concept in (
        "NumPy/numpydoc",
        "Google",
        "reStructuredText/Sphinx",
        "PEP 257",
        "keyword-only",
        "static type",
        "runtime validation",
        "exception chaining",
        "CI",
    ):
        assert required_concept in narrative
