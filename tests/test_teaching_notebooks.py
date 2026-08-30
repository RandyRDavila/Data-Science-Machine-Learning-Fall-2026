"""Pedagogical contracts for notebooks adopting the teaching standard."""

from pathlib import Path

import nbformat
import pytest

PROJECT_ROOT = Path(__file__).parents[1]
NOTEBOOKS = sorted((PROJECT_ROOT / "notebooks").glob("lecture-*/*.ipynb"))


def standardized_notebooks() -> list[Path]:
    selected = []
    for path in NOTEBOOKS:
        notebook = nbformat.read(path, as_version=4)
        metadata = notebook.metadata.get("rice_dsm", {})
        if metadata.get("teaching_standard") == 1:
            selected.append(path)
    return selected


STANDARDIZED_NOTEBOOKS = standardized_notebooks()


def test_at_least_one_notebook_adopts_the_teaching_standard() -> None:
    assert STANDARDIZED_NOTEBOOKS


@pytest.mark.parametrize(
    "notebook_path", STANDARDIZED_NOTEBOOKS, ids=lambda path: path.name
)
def test_standardized_notebook_has_complete_instructional_arc(
    notebook_path: Path,
) -> None:
    notebook = nbformat.read(notebook_path, as_version=4)
    narrative = "\n".join(
        cell.source.lower()
        for cell in notebook.cells
        if cell.cell_type == "markdown"
    )

    required_sections = (
        "how to use this notebook",
        "learning objectives",
        "why this matters",
        "professional practice",
        "worked example",
        "debugging",
        "guided",
        "independent",
        "extension",
        "common failure",
        "retrieval practice",
        "takeaway",
        "further reading",
    )
    for section in required_sections:
        assert section in narrative, f"missing instructional section: {section}"


@pytest.mark.parametrize(
    "notebook_path", STANDARDIZED_NOTEBOOKS, ids=lambda path: path.name
)
def test_standardized_notebook_is_tagged_and_output_free(
    notebook_path: Path,
) -> None:
    notebook = nbformat.read(notebook_path, as_version=4)
    allowed_tags = {"core", "practice", "extension"}

    for cell in notebook.cells:
        tags = set(cell.metadata.get("tags", []))
        assert len(tags & allowed_tags) == 1
        if cell.cell_type == "code":
            assert cell.execution_count is None
            assert cell.outputs == []


@pytest.mark.parametrize(
    "notebook_path", STANDARDIZED_NOTEBOOKS, ids=lambda path: path.name
)
def test_standardized_notebook_makes_expectations_executable(
    notebook_path: Path,
) -> None:
    notebook = nbformat.read(notebook_path, as_version=4)
    code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    assertion_count = sum(cell.source.count("assert ") for cell in code_cells)
    practice_code = [
        cell for cell in code_cells if "practice" in cell.metadata.get("tags", [])
    ]

    assert assertion_count >= 5
    assert practice_code


@pytest.mark.parametrize(
    "notebook_path", STANDARDIZED_NOTEBOOKS, ids=lambda path: path.name
)
def test_standardized_notebook_has_timing_and_authoritative_references(
    notebook_path: Path,
) -> None:
    notebook = nbformat.read(notebook_path, as_version=4)
    course_metadata = notebook.metadata.rice_dsm
    narrative = "\n".join(
        cell.source for cell in notebook.cells if cell.cell_type == "markdown"
    )

    assert course_metadata.estimated_core_minutes > 0
    assert course_metadata.practice_minutes > 0
    has_python_docs = "https://docs.python.org/" in narrative
    has_python_pep = "https://peps.python.org/" in narrative
    assert has_python_docs or has_python_pep
