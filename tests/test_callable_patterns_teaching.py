"""Contracts for the lambda, argument-unpacking, and variadic-interface lesson."""

import ast
from pathlib import Path

import nbformat

PROJECT_ROOT = Path(__file__).parents[1]
NOTEBOOK_PATH = (
    PROJECT_ROOT
    / "notebooks"
    / "lecture-02-python-foundations-ii"
    / "02-lambdas-args-and-kwargs.ipynb"
)

DOCUMENTED_FUNCTIONS = {
    "calibrate_reading",
    "root_mean_square",
    "mean_ensemble_prediction",
    "record_run",
    "audited_call",
    "evaluate_model",
    "rank_evaluations",
    "make_polynomial",
}

DOCUMENTED_CLASSES = {
    "Observation",
    "CandidateModel",
    "ModelEvaluation",
}


def notebook_trees() -> list[ast.Module]:
    """Parse every code cell independently, as a notebook kernel does."""

    notebook = nbformat.read(NOTEBOOK_PATH, as_version=4)
    return [
        ast.parse(cell.source)
        for cell in notebook.cells
        if cell.cell_type == "code"
    ]


def function_definitions() -> dict[str, ast.FunctionDef]:
    """Return top-level function definitions from the notebook."""

    definitions = {}
    for tree in notebook_trees():
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                definitions[node.name] = node
    return definitions


def class_definitions() -> dict[str, ast.ClassDef]:
    """Return top-level class definitions from the notebook."""

    definitions = {}
    for tree in notebook_trees():
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                definitions[node.name] = node
    return definitions


def test_notebook_demonstrates_local_lambda_use_and_late_binding() -> None:
    lambdas = [
        node
        for tree in notebook_trees()
        for node in ast.walk(tree)
        if isinstance(node, ast.Lambda)
    ]

    assert len(lambdas) >= 10


def test_notebook_defines_both_variadic_parameter_kinds() -> None:
    definitions = function_definitions()

    assert definitions["root_mean_square"].args.vararg.arg == "residuals"
    assert definitions["record_run"].args.kwarg.arg == "tags"
    assert definitions["rank_evaluations"].args.vararg.arg == "evaluations"
    assert definitions["audited_call"].args.vararg.arg == "args"
    assert definitions["audited_call"].args.kwarg.arg == "kwargs"


def test_reusable_functions_use_numpy_style_docstrings() -> None:
    definitions = function_definitions()

    for function_name in DOCUMENTED_FUNCTIONS:
        docstring = ast.get_docstring(definitions[function_name])
        assert docstring is not None
        assert "Parameters\n----------" in docstring
        assert "Returns\n-------" in docstring


def test_worked_example_models_use_numpy_style_docstrings() -> None:
    definitions = class_definitions()

    for class_name in DOCUMENTED_CLASSES:
        docstring = ast.get_docstring(definitions[class_name])
        assert docstring is not None
        assert "Parameters\n----------" in docstring
        assert "Raises\n------" in docstring


def test_variadic_parameters_and_returns_are_annotated() -> None:
    definitions = function_definitions()

    for function_name in DOCUMENTED_FUNCTIONS:
        function = definitions[function_name]
        parameters = [*function.args.posonlyargs, *function.args.args]
        parameters.extend(function.args.kwonlyargs)
        if function.args.vararg is not None:
            parameters.append(function.args.vararg)
        if function.args.kwarg is not None:
            parameters.append(function.args.kwarg)

        assert all(parameter.annotation is not None for parameter in parameters)
        assert function.returns is not None


def test_narrative_distinguishes_syntax_roles_and_design_tradeoffs() -> None:
    notebook = nbformat.read(NOTEBOOK_PATH, as_version=4)
    narrative = "\n".join(
        cell.source for cell in notebook.cells if cell.cell_type == "markdown"
    ).lower()

    for concept in (
        "call-site unpacking",
        "variadic",
        "positional-only",
        "keyword-only",
        "late binding",
        "tuple",
        "dictionary",
        "misspelled",
        "smallest honest interface",
        "paramspec",
        "typedDict",
        "functools.wraps",
    ):
        assert concept.lower() in narrative


def test_worked_example_combines_unpacking_kwargs_and_a_lambda_key() -> None:
    notebook = nbformat.read(NOTEBOOK_PATH, as_version=4)
    worked_code = "\n".join(
        cell.source
        for cell in notebook.cells
        if cell.cell_type == "code" and "ranking = rank_evaluations" in cell.source
    )

    assert "**evaluation_config" in worked_code
    assert "*evaluations" in worked_code
    assert "key=lambda" in worked_code
