"""Contracts for the classes and scientific-domain-modeling lesson."""

import ast
from pathlib import Path

import nbformat

PROJECT_ROOT = Path(__file__).parents[1]
NOTEBOOK_PATH = (
    PROJECT_ROOT
    / "notebooks"
    / "lecture-02-python-foundations-ii"
    / "01-classes-and-data-modeling.ipynb"
)

DOCUMENTED_CLASSES = {
    "Vector2D",
    "ParticleState",
    "ChemicalSpecies",
    "ServiceStation",
    "QueueMetrics",
    "RunningMean",
    "ClosedInterval",
    "SolutionSample",
}

DOCUMENTED_FUNCTIONS = {
    "dot_product",
    "magnitude",
    "kinetic_energy",
    "momentum",
    "moles_from_mass",
    "utilization",
    "analyze_mm1",
    "molar_concentration",
}


def definitions() -> tuple[dict[str, ast.ClassDef], dict[str, ast.FunctionDef]]:
    """Return top-level class and function definitions from notebook code cells."""

    notebook = nbformat.read(NOTEBOOK_PATH, as_version=4)
    classes = {}
    functions = {}
    for cell in notebook.cells:
        if cell.cell_type != "code":
            continue
        tree = ast.parse(cell.source)
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                classes[node.name] = node
            elif isinstance(node, ast.FunctionDef):
                functions[node.name] = node
    return classes, functions


def function_is_fully_annotated(function: ast.FunctionDef) -> bool:
    """Check parameter and return annotations, excluding `self` and `cls`."""

    parameters = [*function.args.posonlyargs, *function.args.args]
    parameters.extend(function.args.kwonlyargs)
    public_parameters = [
        parameter for parameter in parameters if parameter.arg not in {"self", "cls"}
    ]
    return (
        all(parameter.annotation is not None for parameter in public_parameters)
        and function.returns is not None
    )


def test_domain_examples_span_the_promised_disciplines() -> None:
    notebook = nbformat.read(NOTEBOOK_PATH, as_version=4)
    narrative = "\n".join(
        cell.source for cell in notebook.cells if cell.cell_type == "markdown"
    ).lower()

    for discipline in ("mathematics", "physics", "chemistry", "industrial"):
        assert discipline in narrative


def test_public_models_use_numpy_style_class_docstrings() -> None:
    classes, _ = definitions()

    for class_name in DOCUMENTED_CLASSES:
        docstring = ast.get_docstring(classes[class_name])
        assert docstring is not None
        assert "Parameters\n----------" in docstring or class_name == "RunningMean"


def test_public_computations_are_documented_and_fully_annotated() -> None:
    _, functions = definitions()

    for function_name in DOCUMENTED_FUNCTIONS:
        function = functions[function_name]
        docstring = ast.get_docstring(function)
        assert docstring is not None
        assert "Parameters\n----------" in docstring
        assert "Returns\n-------" in docstring
        assert function_is_fully_annotated(function)


def test_fallible_interfaces_document_raises() -> None:
    classes, functions = definitions()

    for class_name in (
        "Vector2D",
        "ParticleState",
        "ChemicalSpecies",
        "ServiceStation",
        "QueueMetrics",
        "ClosedInterval",
        "SolutionSample",
    ):
        assert "Raises\n------" in ast.get_docstring(classes[class_name])

    for function_name in ("moles_from_mass", "utilization", "analyze_mm1"):
        assert "Raises\n------" in ast.get_docstring(functions[function_name])


def test_notebook_teaches_the_core_modeling_decisions() -> None:
    notebook = nbformat.read(NOTEBOOK_PATH, as_version=4)
    narrative = "\n".join(
        cell.source for cell in notebook.cells if cell.cell_type == "markdown"
    ).lower()

    for concept in (
        "invariant",
        "type hints",
        "runtime validation",
        "value equality",
        "object identity",
        "composition",
        "method or function",
        "default_factory",
        "frozen is shallow",
        "slots",
        "units",
        "model validity",
    ):
        assert concept.lower() in narrative


def test_worked_example_uses_an_object_in_object_out_function() -> None:
    _, functions = definitions()
    analysis = functions["analyze_mm1"]

    station_parameter = analysis.args.args[0]
    assert ast.unparse(station_parameter.annotation) == "ServiceStation"
    assert ast.unparse(analysis.returns) == "QueueMetrics"
