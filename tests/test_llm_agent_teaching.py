"""Contracts for Lecture 3's LLM tools and agents lesson."""

import json
import tomllib
from pathlib import Path

import nbformat

PROJECT_ROOT = Path(__file__).parents[1]
LECTURE_DIR = PROJECT_ROOT / "notebooks" / "lecture-03-packages-numpy-pandas"
NOTEBOOK_PATH = LECTURE_DIR / "06-llm-tools-and-agents.ipynb"
DEMO_DIR = LECTURE_DIR / "06-llm-tools-and-agents"


def notebook() -> nbformat.NotebookNode:
    """Load the LLM agents notebook."""

    return nbformat.read(NOTEBOOK_PATH, as_version=4)


def narrative() -> str:
    """Return normalized lowercase notebook prose."""

    markdown = "\n".join(
        cell.source for cell in notebook().cells if cell.cell_type == "markdown"
    )
    return " ".join(markdown.lower().split())


def code_text() -> str:
    """Return all executable notebook code."""

    return "\n".join(
        cell.source for cell in notebook().cells if cell.cell_type == "code"
    )


def test_client_dependency_is_declared_and_locked() -> None:
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)

    assert any(
        requirement.startswith("openai>=")
        for requirement in project["project"]["dependencies"]
    )
    assert 'name = "openai"' in (PROJECT_ROOT / "uv.lock").read_text(
        encoding="utf-8"
    )


def test_notebook_is_a_long_form_offline_reference() -> None:
    lesson = notebook()

    assert len(lesson.cells) >= 105
    assert sum(cell.cell_type == "markdown" for cell in lesson.cells) >= 85
    assert sum(cell.cell_type == "code" for cell in lesson.cells) >= 20
    assert lesson.metadata.rice_dsm.estimated_core_minutes >= 200
    assert lesson.metadata.rice_dsm.practice_minutes >= 150
    assert lesson.metadata.rice_dsm.requires_network is False


def test_notebook_defines_the_agent_system_precisely() -> None:
    lesson = narrative()

    for concept in (
        "tokens",
        "context window",
        "inference",
        "structured output",
        "assistant, workflow, and agent are not synonyms",
        "model gateway",
        "tool registry",
        "durable orchestrator",
        "the model proposes",
        "an orchestrator schedules",
        "retrieval-augmented generation",
        "model context protocol",
    ):
        assert concept in lesson


def test_notebook_is_provider_neutral_and_precise_about_free_models() -> None:
    lesson = narrative()

    for concept in (
        "openai",
        "claude",
        "grok",
        "kimi",
        "gemini",
        "llama",
        "qwen",
        "gemma",
        "mistral",
        "free chat access",
        "api free tier",
        "free-to-download weights",
        "open weight",
        "hardware, memory, electricity",
        "task-specific evaluations",
        "an agent architecture should not be a brand architecture",
    ):
        assert concept in lesson


def test_core_never_calls_a_provider_or_reads_a_real_secret() -> None:
    source = code_text()

    for forbidden in (
        "OpenAI(",
        "responses.create(",
        "requests.",
        "httpx.",
        'os.environ["OPENAI_API_KEY"]',
        "subprocess.",
    ):
        assert forbidden not in source

    assert "SecretStr" in source
    assert "requires_network" not in source


def test_secret_handling_is_cross_platform_and_fail_closed() -> None:
    lesson = narrative()

    for concept in (
        "never put a real key",
        ".env",
        "windows powershell",
        "macos/linux",
        "secret manager",
        "short-lived workload identity",
        "rotate",
        "redaction is defense in depth",
        "do not pass a secret object into a prompt",
    ):
        assert concept in lesson

    gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".env" in gitignore
    assert "!.env.example" in gitignore


def test_tools_outputs_and_loops_have_deterministic_boundaries() -> None:
    lesson = narrative()
    source = code_text()

    for concept in (
        "syntax control, not truth",
        "unknown, overprivileged, and malformed calls fail closed",
        "least privilege",
        "maximum steps",
        "maximum tool calls",
        "prompt injection",
        "instructions and untrusted data",
    ):
        assert concept in lesson

    for implementation in (
        "TrainingRunProposal.model_json_schema()",
        "teaching_tool_registry()",
        "maximum_steps",
        "allowed_risks=frozenset",
    ):
        assert implementation in source


def test_docstring_and_training_workflows_are_independently_verified() -> None:
    lesson = narrative()
    source = code_text()

    for concept in (
        "numpy-style docstring",
        "source digest",
        "ast",
        "compile",
        "human review",
        "deterministic policy",
        "accountable approval",
        "idempotent",
        "dataset version",
        "code revision",
        "gpu execution is not approved",
    ):
        assert concept in lesson

    for implementation in (
        "audit_python_docstrings(",
        "validate_docstring_proposal(",
        "approve_training_run(",
        "InMemoryTrainingScheduler()",
    ):
        assert implementation in source


def test_notebook_teaches_evals_operations_and_production_governance() -> None:
    lesson = narrative()

    for concept in (
        "evals are tests for a probabilistic component",
        "golden cases",
        "adversarial",
        "latency",
        "token",
        "trace",
        "request id",
        "ci/cd for agent systems",
        "canary",
        "rollback",
        "incident",
        "data retention",
        "license",
    ):
        assert concept in lesson


def test_companion_artifacts_are_present_and_machine_readable() -> None:
    expected = (
        "README.md",
        ".env.example",
        "prompts/docstring-review.md",
        "schemas/training-run-proposal.schema.json",
        "policies/tool-policy.yaml",
        "evals/cases.jsonl",
        "orchestration/training_workflow.py",
    )
    for relative_path in expected:
        assert (DEMO_DIR / relative_path).is_file()

    schema = json.loads(
        (DEMO_DIR / "schemas" / "training-run-proposal.schema.json").read_text(
            encoding="utf-8"
        )
    )
    assert schema["additionalProperties"] is False
    assert schema["properties"]["maximum_runtime_minutes"]["maximum"] == 1440

    eval_cases = [
        json.loads(line)
        for line in (DEMO_DIR / "evals" / "cases.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert len(eval_cases) >= 5
    assert len({case["case_id"] for case in eval_cases}) == len(eval_cases)


def test_no_credentials_or_personal_paths_are_embedded() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in DEMO_DIR.rglob("*")
        if path.is_file()
    )
    notebook_source = "\n".join(cell.source for cell in notebook().cells)

    for forbidden in (
        "/Users/",
        "C:\\Users\\",
        "sk-proj-",
        "sk-ant-",
        "xai-",
    ):
        assert forbidden not in text
        assert forbidden not in notebook_source
