"""Protect the course's zero-assumption explanation of APIs."""

from pathlib import Path

import nbformat

PROJECT_ROOT = Path(__file__).parents[1]
NOTEBOOKS = PROJECT_ROOT / "notebooks"
GUIDE = (
    PROJECT_ROOT
    / "supplementary-materials"
    / "computing-foundations"
    / "07-what-is-an-api.md"
)


def markdown(path: Path) -> str:
    """Return normalized Markdown from one notebook."""

    notebook = nbformat.read(path, as_version=4)
    text = "\n".join(
        cell.source for cell in notebook.cells if cell.cell_type == "markdown"
    )
    return " ".join(text.lower().split())


def guide_text() -> str:
    """Return normalized supplementary-guide prose."""

    return " ".join(GUIDE.read_text(encoding="utf-8").lower().split())


def test_supplement_starts_from_the_acronym_and_purpose() -> None:
    lesson = guide_text()

    for concept in (
        "api stands for **application programming interface**",
        "documented way for one piece of software",
        "agreed boundary between a caller and an implementation",
        "not necessarily a website",
        "reuse software",
        "automate work",
        "stable public request",
    ):
        assert concept in lesson

    assert lesson.count("```mermaid") >= 3


def test_supplement_distinguishes_python_and_web_apis() -> None:
    lesson = guide_text()

    for concept in (
        "a familiar python api",
        "package api",
        "a web api",
        "client",
        "server",
        "method",
        "path",
        "query parameter",
        "endpoint",
        "headers",
        "request **body**",
        "status code",
        "json is a data representation, not an api",
        "http is a communication protocol",
    ):
        assert concept in lesson


def test_supplement_explains_model_apis_sdks_and_credentials() -> None:
    lesson = guide_text()

    for concept in (
        "apis for hosted language models",
        "provider-operated computers run inference",
        "api key",
        "secret credential",
        "sdk",
        "client-side helper code",
        "does not make inference happen on your laptop",
        "local inference server",
    ):
        assert concept in lesson


def test_early_python_lessons_define_api_at_first_use() -> None:
    values = markdown(
        NOTEBOOKS
        / "lecture-01-python-foundations"
        / "01-values-types-and-objects.ipynb"
    )
    functions = markdown(
        NOTEBOOKS
        / "lecture-02-python-foundations-ii"
        / "00-functions-and-functional-patterns.ipynb"
    )

    assert "apis—application programming interfaces" in values
    assert "agreed way for one program to request data or behavior" in values
    assert "api stands for **application programming interface**" in functions
    assert "signature, parameter meanings, return behavior, exceptions" in functions


def test_package_lesson_distinguishes_library_and_http_apis() -> None:
    lesson = markdown(
        NOTEBOOKS
        / "lecture-03-projects-packages-testing"
        / "01-scripts-modules-and-packages.ipynb"
    )

    assert "supported names and behaviors that other python code may rely on" in lesson
    assert "in-process library api, not an http web service" in lesson
    assert "web api exchanges requests and responses" in lesson


def test_agent_lesson_explains_the_complete_hosted_api_journey() -> None:
    lesson = markdown(
        NOTEBOOKS
        / "lecture-07-llm-tools-agents"
        / "00-llm-tools-and-agents.ipynb"
    )

    for concept in (
        "**api** stands for **application programming interface**",
        "our python program request inference",
        "client helper code",
        "does not install the hosted model",
        "constructs an authenticated https request",
        "provider api validates it and runs the selected model",
        "our code validates the response",
        "the key authorizes the caller; it is not part of the prompt",
    ):
        assert concept in lesson


def test_end_to_end_lesson_teaches_request_anatomy_before_using_it() -> None:
    lesson = markdown(
        NOTEBOOKS
        / "lecture-08-end-to-end-data-products"
        / "00-end-to-end-data-products.ipynb"
    )

    for concept in (
        "api stands for **application programming interface**",
        "python functions and packages have in-process apis",
        "http web api",
        "not the database, not json alone",
        "`get` is the http method",
        "`limit=20` is a query parameter",
        "method plus path identify an endpoint",
        "status code, headers",
    ):
        assert concept in lesson


def test_dependency_notebook_does_not_repeat_the_llm_client_description() -> None:
    lesson = markdown(
        NOTEBOOKS
        / "lecture-03-projects-packages-testing"
        / "00-projects-environments-and-packaging.ipynb"
    )

    assert lesson.count("the openai client supports") == 1
