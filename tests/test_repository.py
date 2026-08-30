"""Structural tests that keep the teaching repository reproducible."""

import json
from pathlib import Path

import nbformat
import pytest

PROJECT_ROOT = Path(__file__).parents[1]
LECTURE_DIRECTORIES = sorted((PROJECT_ROOT / "notebooks").glob("lecture-*"))
NOTEBOOKS = sorted(
    notebook
    for lecture_directory in LECTURE_DIRECTORIES
    for notebook in lecture_directory.glob("*.ipynb")
)


@pytest.mark.parametrize(
    "relative_path",
    [
        "README.md",
        "pyproject.toml",
        "uv.lock",
        ".github/workflows/course-ci.yml",
        ".vscode/extensions.json",
        "src/rice_dsm/__init__.py",
        "notebooks/TEACHING_NOTEBOOK_STANDARD.md",
        "notebooks/PROFESSIONAL_PRACTICES.md",
        "notebooks/lecture-01-python-foundations/README.md",
        "notebooks/lecture-02-python-foundations-ii/README.md",
        "notebooks/lecture-03-projects-packages-testing/README.md",
        "notebooks/lecture-04-numpy-pandas/README.md",
        "notebooks/lecture-05-visualization-simulation/README.md",
        "notebooks/lecture-06-databases-data-systems/README.md",
        "notebooks/lecture-07-llm-tools-agents/README.md",
        "notebooks/lecture-08-end-to-end-data-products/README.md",
        "notebooks/lecture-09-supervised-learning-systems/README.md",
        "notebooks/lecture-10-linear-regression-regularization/README.md",
        "notebooks/lecture-11-classification-decisions/README.md",
        "notebooks/lecture-12-geometric-learning/README.md",
        "notebooks/lecture-13-decision-trees/README.md",
        "notebooks/lecture-14-ensemble-learning/README.md",
        "notebooks/lecture-15-model-selection-evaluation/README.md",
        "notebooks/lecture-16-neural-networks-autodiff/README.md",
        "notebooks/lecture-17-reliable-supervised-systems/README.md",
        "notes/part-ii-roadmap.md",
        "supplementary-materials/computing-foundations/README.md",
    ],
)
def test_required_course_resource_exists(relative_path: str) -> None:
    """Important entry points should not disappear during reorganization."""

    assert (PROJECT_ROOT / relative_path).is_file()


def test_notebook_guidance_defines_the_artifact_boundary() -> None:
    """Course guidance must distinguish experiments from operated systems."""

    standard = (PROJECT_ROOT / "notebooks/TEACHING_NOTEBOOK_STANDARD.md").read_text()

    for required_idea in (
        "## The notebook boundary",
        "experimental laboratory",
        "**Graduation rule:**",
        "For sustained academic research",
        "Schedule, deploy, monitor, or roll back work",
    ):
        assert required_idea in standard


def test_readme_distinguishes_lecture_units_from_class_meetings() -> None:
    """Numbered content units must not imply a one-unit-per-meeting schedule."""

    readme = (PROJECT_ROOT / "README.md").read_text()
    normalized = " ".join(readme.split())

    assert "### Lecture units and class meetings" in readme
    assert (
        "not a promise that the unit occupies one complete class meeting" in normalized
    )
    assert (
        "The syllabus and weekly announcement determine the live itinerary"
        in normalized
    )


@pytest.mark.parametrize(
    "lecture_directory", LECTURE_DIRECTORIES, ids=lambda path: path.name
)
def test_each_lecture_contains_an_ordered_notebook_sequence(
    lecture_directory: Path,
) -> None:
    names = [path.name for path in sorted(lecture_directory.glob("*.ipynb"))]

    assert names
    assert names == sorted(names)
    assert names[0].startswith("00-")


def test_ci_reproduces_the_course_on_all_supported_platforms() -> None:
    workflow = (PROJECT_ROOT / ".github/workflows/course-ci.yml").read_text()

    for operating_system in ("ubuntu-latest", "macos-latest", "windows-latest"):
        assert operating_system in workflow

    for required_command in (
        "uv sync --locked",
        "uv run python scripts/setup_course.py",
        "uv run ruff check src tests scripts",
        "uv build",
        "uv run pytest -q",
    ):
        assert required_command in workflow


def test_vscode_recommends_required_notebook_extensions() -> None:
    recommendations_file = PROJECT_ROOT / ".vscode/extensions.json"
    recommendations = json.loads(recommendations_file.read_text())["recommendations"]

    assert "ms-python.python" in recommendations
    assert "ms-toolsai.jupyter" in recommendations


@pytest.mark.parametrize("notebook_path", NOTEBOOKS, ids=lambda path: path.name)
def test_notebook_is_valid_and_uses_course_kernel(notebook_path: Path) -> None:
    """Every notebook must be valid JSON and request the reproducible kernel."""

    notebook = nbformat.read(notebook_path, as_version=4)
    nbformat.validate(notebook)

    assert notebook.metadata.kernelspec.name == "rice-dsm"
    assert any(cell.cell_type == "markdown" for cell in notebook.cells)
    assert any(cell.cell_type == "code" for cell in notebook.cells)


@pytest.mark.parametrize("notebook_path", NOTEBOOKS, ids=lambda path: path.name)
def test_notebook_starts_with_a_level_one_title(notebook_path: Path) -> None:
    notebook = nbformat.read(notebook_path, as_version=4)

    first_cell = notebook.cells[0]
    assert first_cell.cell_type == "markdown"
    assert first_cell.source.startswith("# ")
