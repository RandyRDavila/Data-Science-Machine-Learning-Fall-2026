"""Contracts for the native-file and scientific knowledge-graph lesson."""

import ast
import csv
import json
from pathlib import Path

import nbformat

PROJECT_ROOT = Path(__file__).parents[1]
LECTURE_DIRECTORY = (
    PROJECT_ROOT / "notebooks" / "lecture-02-python-foundations-ii"
)
NOTEBOOK_PATH = LECTURE_DIRECTORY / "03-native-data-files.ipynb"
DATA_DIRECTORY = LECTURE_DIRECTORY / "data"
CONCEPTS_PATH = DATA_DIRECTORY / "scientific_concepts.json"
RELATIONSHIPS_PATH = DATA_DIRECTORY / "scientific_relationships.csv"


def notebook() -> nbformat.NotebookNode:
    """Load the notebook as version 4."""

    return nbformat.read(NOTEBOOK_PATH, as_version=4)


def definitions() -> tuple[dict[str, ast.ClassDef], dict[str, ast.FunctionDef]]:
    """Collect top-level class and function definitions from all code cells."""

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


def test_course_data_has_expected_json_and_csv_contracts() -> None:
    document = json.loads(CONCEPTS_PATH.read_text(encoding="utf-8"))
    assert document["schema_version"] == 1
    assert len(document["concepts"]) == 20
    assert len({record["id"] for record in document["concepts"]}) == 20

    with RELATIONSHIPS_PATH.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    assert reader.fieldnames == [
        "source_id",
        "predicate",
        "target_id",
        "confidence",
        "evidence",
    ]
    assert len(rows) == 25
    node_ids = {record["id"] for record in document["concepts"]}
    assert all(row["source_id"] in node_ids for row in rows)
    assert all(row["target_id"] in node_ids for row in rows)
    assert all(0.0 <= float(row["confidence"]) <= 1.0 for row in rows)


def test_data_readme_states_provenance_and_scientific_limits() -> None:
    readme_text = (DATA_DIRECTORY / "README.md").read_text(encoding="utf-8").lower()
    readme = " ".join(readme_text.split())
    for phrase in (
        "course-authored",
        "not an authoritative ontology",
        "not an empirical probability",
        "durable source identifiers",
        "expert review",
    ):
        assert phrase in readme


def test_notebook_builds_domain_objects_and_a_queryable_graph() -> None:
    classes, functions = definitions()

    assert {
        "KnowledgeNode",
        "Relationship",
        "KnowledgeGraph",
        "QueryableKnowledgeGraph",
        "PathKnowledgeGraph",
    } <= classes.keys()
    assert {
        "find_project_root",
        "node_from_mapping",
        "relationship_from_mapping",
        "load_knowledge_graph",
        "graph_to_mapping",
    } <= functions.keys()


def test_public_adapters_are_documented_and_annotated() -> None:
    _, functions = definitions()

    for name in (
        "find_project_root",
        "node_from_mapping",
        "relationship_from_mapping",
        "load_knowledge_graph",
        "graph_to_mapping",
    ):
        function = functions[name]
        docstring = ast.get_docstring(function)
        parameters = [*function.args.posonlyargs, *function.args.args]
        parameters.extend(function.args.kwonlyargs)

        assert docstring is not None
        assert "Parameters\n----------" in docstring
        assert "Returns\n-------" in docstring
        assert all(parameter.annotation is not None for parameter in parameters)
        assert function.returns is not None


def test_notebook_teaches_file_boundaries_and_graph_invariants() -> None:
    narrative_text = "\n".join(
        cell.source for cell in notebook().cells if cell.cell_type == "markdown"
    ).lower()
    narrative = " ".join(narrative_text.split())

    for concept in (
        "syntax validation",
        "schema validation",
        "domain validation",
        "referential integrity",
        "breadth-first search",
        "context managers",
        "encoding",
        "newline=\"\"",
        "raw inputs",
        "not automatic truth",
    ):
        assert concept in narrative


def test_notebook_references_both_data_files_and_contains_no_outputs() -> None:
    lesson = notebook()
    code_text = "\n".join(
        cell.source for cell in lesson.cells if cell.cell_type == "code"
    )

    assert "scientific_concepts.json" in code_text
    assert "scientific_relationships.csv" in code_text
    assert all(
        not cell.get("outputs")
        for cell in lesson.cells
        if cell.cell_type == "code"
    )
