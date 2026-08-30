"""Contracts for Lecture 3's end-to-end data-product lesson."""

import tomllib
from pathlib import Path

import nbformat

PROJECT_ROOT = Path(__file__).parents[1]
LECTURE_DIR = PROJECT_ROOT / "notebooks" / "lecture-03-packages-numpy-pandas"
NOTEBOOK_PATH = LECTURE_DIR / "07-end-to-end-data-products.ipynb"
DEMO_DIR = LECTURE_DIR / "07-end-to-end-data-products"


def notebook() -> nbformat.NotebookNode:
    """Load the end-to-end notebook."""

    return nbformat.read(NOTEBOOK_PATH, as_version=4)


def narrative() -> str:
    """Return normalized notebook prose."""

    markdown = "\n".join(
        cell.source for cell in notebook().cells if cell.cell_type == "markdown"
    )
    return " ".join(markdown.lower().split())


def code_text() -> str:
    """Return all executable notebook code."""

    return "\n".join(
        cell.source for cell in notebook().cells if cell.cell_type == "code"
    )


def test_web_runtime_dependencies_are_declared_and_locked() -> None:
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)

    declared = project["project"]["dependencies"]
    for prefix in ("fastapi>=", "httpx2>=", "uvicorn>="):
        assert any(requirement.startswith(prefix) for requirement in declared)

    lock_text = (PROJECT_ROOT / "uv.lock").read_text(encoding="utf-8")
    for package in ("fastapi", "httpx2", "uvicorn", "pydantic", "starlette"):
        assert f'name = "{package}"' in lock_text


def test_notebook_is_a_long_form_executable_reference() -> None:
    lesson = notebook()

    assert len(lesson.cells) >= 140
    assert sum(cell.cell_type == "markdown" for cell in lesson.cells) >= 100
    assert sum(cell.cell_type == "code" for cell in lesson.cells) >= 30
    assert lesson.metadata.rice_dsm.estimated_core_minutes >= 200
    assert lesson.metadata.rice_dsm.practice_minutes >= 150
    assert lesson.metadata.rice_dsm.requires_network is False


def test_notebook_defines_end_to_end_and_the_system_pieces() -> None:
    lesson = narrative()

    for concept in (
        "what does end-to-end mean?",
        "data pipeline",
        "request path",
        "training pipeline",
        "serving pipeline",
        "deployment pipeline",
        "system glossary",
        "database",
        "dbms",
        "repository",
        "domain service",
        "backend",
        "api gateway",
        "asgi server",
        "frontend",
        "client",
        "reverse proxy/load balancer",
        "secret manager",
        "rum",
    ):
        assert concept in lesson


def test_notebook_has_multiple_purpose_specific_diagrams() -> None:
    markdown = "\n".join(
        cell.source for cell in notebook().cells if cell.cell_type == "markdown"
    )

    assert markdown.count("```mermaid") >= 5
    for diagram in (
        "system context diagram",
        "component and request-sequence diagrams",
        "deployment diagram",
        "ci/cd production flow",
        "correlation diagram",
    ):
        assert diagram in markdown.lower()


def test_notebook_executes_a_real_package_backed_vertical_slice() -> None:
    source = code_text()

    for example in (
        "create_app(application_database_path)",
        "TestClient(application)",
        "MeasurementInput(",
        "repository.save(valid_command)",
        'client.post("/api/v1/measurements"',
        'client.get("/api/v1/measurements/latest',
        'client.get("/openapi.json")',
        'client.get("/health/live")',
        'client.get("/health/ready")',
        'client.get("/")',
        "application_workspace.cleanup()",
    ):
        assert example in source

    assert "uvicorn.run(" not in source


def test_notebook_teaches_hosting_release_and_production_cicd() -> None:
    lesson = narrative()

    for concept in (
        "common implementation options",
        "dns",
        "tls",
        "cdn",
        "waf",
        "managed database",
        "container",
        "immutable artifact",
        "expand–migrate–contract",
        "continuous delivery is not continuous deployment",
        "blue/green",
        "canary",
        "feature flag",
        "same digest",
        "sbom",
        "rollback",
    ):
        assert concept in lesson


def test_notebook_teaches_client_and_server_observability() -> None:
    lesson = narrative()
    source = code_text()

    for concept in (
        "monitor clients, not only servers",
        "browser devtools",
        "error tracking",
        "real-user monitoring",
        "cloudwatch rum",
        "grafana faro",
        "opentelemetry",
        "synthetic monitoring",
        "session replay",
        "privacy and cardinality contract",
        "logs alone are not a monitoring strategy",
        "service-level objectives",
    ):
        assert concept in lesson

    assert "client_event =" in source
    assert "forbidden_client_fields" in source
    assert "safe_request_event(" in source


def test_notebook_distinguishes_device_browser_and_os_testing() -> None:
    lesson = narrative()
    source = code_text()

    for concept in (
        "phone and os “emulation” has several meanings",
        "playwright browser context",
        "android emulator",
        "ios simulator",
        "cloud device farm",
        "physical device",
        "user-agent header is not a phone emulator",
        "operating-system compatibility is a different matrix",
        "responsive",
        "accessibility",
    ):
        assert concept in lesson

    for runner in ("ubuntu-latest", "macos-latest", "windows-latest"):
        assert runner in source


def test_companion_project_maps_all_major_artifacts() -> None:
    expected_paths = (
        "README.md",
        "backend/app.py",
        "browser/playwright.config.ts",
        "browser/critical-journey.spec.ts",
        "deployment/Containerfile",
        "deployment/compose.yaml",
        "deployment/production-cicd.example.yml",
        "monitoring/client-event.schema.json",
        "monitoring/dashboards-and-alerts.md",
        "monitoring/otel-collector.example.yaml",
    )
    for relative_path in expected_paths:
        assert (DEMO_DIR / relative_path).is_file()

    overview = (DEMO_DIR / "README.md").read_text(encoding="utf-8")
    assert "Canonical application code" in overview
    assert "teaching reference" in overview


def test_companion_assets_encode_production_safety_boundaries() -> None:
    containerfile = (DEMO_DIR / "deployment" / "Containerfile").read_text(
        encoding="utf-8"
    )
    workflow = (
        DEMO_DIR / "deployment" / "production-cicd.example.yml"
    ).read_text(encoding="utf-8")
    monitoring = (
        DEMO_DIR / "monitoring" / "dashboards-and-alerts.md"
    ).read_text(encoding="utf-8")

    assert "Pin this base by reviewed digest for production" in containerfile
    assert "uv sync --locked --no-dev" in containerfile
    assert "USER 10001" in containerfile
    assert "--reload" not in containerfile
    assert "same digest" in workflow
    assert "client RUM" in workflow
    assert "request/trace ID" in monitoring
    assert "Do not page on every log line" in monitoring


def test_notebook_and_demo_contain_no_credentials_or_personal_paths() -> None:
    sources = [cell.source for cell in notebook().cells]
    for path in DEMO_DIR.rglob("*"):
        if path.is_file():
            sources.append(path.read_text(encoding="utf-8"))
    complete_text = "\n".join(sources)

    assert "/Users/" not in complete_text
    assert "C:\\Users\\" not in complete_text
    assert "AKIA" not in complete_text
    assert "BEGIN PRIVATE KEY" not in complete_text
    assert "example.invalid" in complete_text
