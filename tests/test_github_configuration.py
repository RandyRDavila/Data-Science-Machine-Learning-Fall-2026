"""Contract tests for repository governance and GitHub automation."""

import re
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).parents[1]
GITHUB_ROOT = PROJECT_ROOT / ".github"
WORKFLOW_ROOT = GITHUB_ROOT / "workflows"
ISSUE_TEMPLATE_ROOT = GITHUB_ROOT / "ISSUE_TEMPLATE"

WORKFLOWS = sorted(WORKFLOW_ROOT.glob("*.yml"))
ISSUE_FORMS = sorted(
    path for path in ISSUE_TEMPLATE_ROOT.glob("*.yml") if path.name != "config.yml"
)


def read_utf8(path: Path) -> str:
    """Read repository configuration independently of the operating-system locale."""

    return path.read_text(encoding="utf-8")


def load_yaml(path: Path) -> object:
    """Load ordinary repository YAML."""

    return yaml.safe_load(read_utf8(path))


def load_workflow(path: Path) -> dict[str, object]:
    """Load workflow YAML without YAML 1.1 treating the key ``on`` as Boolean."""

    document = yaml.load(read_utf8(path), Loader=yaml.BaseLoader)
    assert isinstance(document, dict)
    return document


@pytest.mark.parametrize(
    "relative_path",
    [
        ".github/CODEOWNERS",
        ".github/README.md",
        ".github/dependabot.yml",
        ".github/labeler.yml",
        ".github/pull_request_template.md",
        ".github/ISSUE_TEMPLATE/config.yml",
        ".github/ISSUE_TEMPLATE/bug.yml",
        ".github/ISSUE_TEMPLATE/content.yml",
        ".github/ISSUE_TEMPLATE/feature.yml",
        ".github/ISSUE_TEMPLATE/question.yml",
        ".github/workflows/course-ci.yml",
        ".github/workflows/course-pages.yml",
        ".github/workflows/course-release.yml",
        ".github/workflows/dependency-review.yml",
        ".github/workflows/pr-labeler.yml",
        ".github/workflows/textbook.yml",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "site/index.html",
        "site/favicon.svg",
        "site/styles.css",
        "scripts/build_course_site.py",
        "scripts/build_release_bundle.py",
        "scripts/smoke_test_course_site.py",
        "supplementary-materials/computing-foundations/08-continuous-delivery-and-deployment.md",
    ],
)
def test_governance_resource_exists(relative_path: str) -> None:
    assert (PROJECT_ROOT / relative_path).is_file()


@pytest.mark.parametrize("form_path", ISSUE_FORMS, ids=lambda path: path.stem)
def test_issue_forms_request_actionable_safe_reports(form_path: Path) -> None:
    form = load_yaml(form_path)

    assert isinstance(form, dict)
    assert len(form["name"]) > 3
    assert form["description"]
    assert form["title"].startswith("[")
    assert isinstance(form["body"], list)

    fields = [element for element in form["body"] if element["type"] != "markdown"]
    identifiers = [field["id"] for field in fields]

    assert len(identifiers) == len(set(identifiers))
    assert all(field["attributes"].get("label") for field in fields)
    assert any(
        field.get("validations", {}).get("required") is True for field in fields
    )

    normalized = read_utf8(form_path).lower()
    assert "private" in normalized
    assert "secret" in normalized or "credential" in normalized


def test_issue_template_chooser_requires_structured_reports() -> None:
    config = load_yaml(ISSUE_TEMPLATE_ROOT / "config.yml")

    assert config == {"blank_issues_enabled": False, "contact_links": []}


def test_pull_request_template_prompts_for_evidence_and_boundaries() -> None:
    template = read_utf8(GITHUB_ROOT / "pull_request_template.md")

    for required_heading in (
        "## Purpose",
        "## What changed",
        "## Evidence",
        "## Contract and teaching impact",
        "## Reviewer notes",
        "## Related issue",
    ):
        assert required_heading in template

    for required_evidence in (
        "uv run pytest -q",
        "Windows, macOS, and Linux",
        "Rice DSM kernel",
        "visually inspected",
        "No secrets",
    ):
        assert required_evidence in template


def test_workflows_pin_actions_and_use_explicit_permissions() -> None:
    action_reference = re.compile(r"^\s*uses:\s*[^@\s]+@([^\s#]+)", re.MULTILINE)

    for workflow_path in WORKFLOWS:
        workflow_text = read_utf8(workflow_path)
        workflow = load_workflow(workflow_path)
        references = action_reference.findall(workflow_text)

        assert workflow.get("permissions")
        assert references
        assert all(re.fullmatch(r"[0-9a-f]{40}", ref) for ref in references)


def test_course_ci_avoids_duplicate_pr_runs_and_preserves_stable_gate() -> None:
    path = WORKFLOW_ROOT / "course-ci.yml"
    workflow = load_workflow(path)
    workflow_text = read_utf8(path)
    triggers = workflow["on"]

    assert triggers["push"]["branches"] == ["main"]
    assert "pull_request" in triggers
    assert "workflow_dispatch" in triggers
    assert workflow["env"]["PYTHONUTF8"] == "1"

    for operating_system in ("ubuntu-latest", "macos-latest", "windows-latest"):
        assert operating_system in workflow_text

    for command in (
        "uv sync --locked",
        "uv run python scripts/setup_course.py",
        "uv run ruff check src tests scripts",
        "uv build",
        "uv run pytest -q",
    ):
        assert command in workflow_text

    assert "name: CI gate" in workflow_text
    assert "needs: course-quality" in workflow_text


def test_privileged_labeler_never_executes_pull_request_code() -> None:
    path = WORKFLOW_ROOT / "pr-labeler.yml"
    workflow = load_workflow(path)
    workflow_text = read_utf8(path)

    assert "pull_request_target" in workflow["on"]
    assert workflow["permissions"] == {
        "contents": "read",
        "pull-requests": "write",
    }
    assert "actions/checkout" not in workflow_text
    assert re.search(r"^\s*run:", workflow_text, re.MULTILINE) is None
    assert "actions/labeler@" in workflow_text


def test_textbook_workflow_builds_and_publishes_a_review_artifact() -> None:
    workflow_text = read_utf8(WORKFLOW_ROOT / "textbook.yml")

    for required_text in (
        '"textbook/**"',
        "root_file: textbook.tex",
        "working_directory: textbook",
        "LaTeX Warning",
        "Overfull",
        "textbook/textbook.pdf",
        "actions/upload-artifact@",
    ):
        assert required_text in workflow_text


def test_dependency_automation_covers_uv_actions_and_new_vulnerabilities() -> None:
    dependabot = load_yaml(GITHUB_ROOT / "dependabot.yml")
    ecosystems = {update["package-ecosystem"] for update in dependabot["updates"]}
    review_text = read_utf8(WORKFLOW_ROOT / "dependency-review.yml")

    assert dependabot["version"] == 2
    assert ecosystems == {"uv", "github-actions"}
    assert all(update["directory"] == "/" for update in dependabot["updates"])
    assert "actions/dependency-review-action@" in review_text
    assert "fail-on-severity: high" in review_text


def test_pages_workflow_builds_promotes_and_verifies_one_artifact() -> None:
    workflow_text = read_utf8(WORKFLOW_ROOT / "course-pages.yml")

    for required_text in (
        "github.ref == 'refs/heads/main'",
        "scripts/build_course_site.py",
        "actions/upload-pages-artifact@",
        "actions/deploy-pages@",
        "name: github-pages",
        "pages: write",
        "id-token: write",
        "scripts/smoke_test_course_site.py",
        "needs.deploy.outputs.page_url",
    ):
        assert required_text in workflow_text

    deploy_section = workflow_text.split("  deploy:", maxsplit=1)[1]
    assert "actions/checkout@" not in deploy_section.split("  verify:", maxsplit=1)[0]


def test_release_workflow_has_approval_provenance_and_no_rebuild() -> None:
    workflow_text = read_utf8(WORKFLOW_ROOT / "course-release.yml")
    publish_section = workflow_text.split("  publish:", maxsplit=1)[1]

    for required_text in (
        '"course-v*"',
        "uv sync --locked",
        "uv run pytest -q",
        "uv build",
        "git cat-file -t",
        "scripts/build_release_bundle.py",
        "actions/attest-build-provenance@",
        "name: course-release",
        "actions/download-artifact@",
        "gh release create",
    ):
        assert required_text in workflow_text

    assert "actions/checkout@" not in publish_section
    assert "uv build" not in publish_section


def test_delivery_documentation_defines_operations_and_rollback() -> None:
    governance = read_utf8(GITHUB_ROOT / "README.md")
    student_guide = read_utf8(
        PROJECT_ROOT
        / "supplementary-materials/computing-foundations"
        / "08-continuous-delivery-and-deployment.md"
    )

    for required_text in (
        "continuous deployment",
        "continuous delivery",
        "course-release",
        "course-v0.1.0",
        "Do not move a published tag",
    ):
        assert required_text in governance

    for required_text in (
        "**artifact**",
        "**Environment",
        "**Smoke test",
        "build once, promote the same artifact",
        "A bad public deployment",
        "A bad tagged release",
    ):
        assert required_text in student_guide


def test_ownership_and_branch_policy_are_explicit() -> None:
    owners = read_utf8(GITHUB_ROOT / "CODEOWNERS")
    governance = read_utf8(GITHUB_ROOT / "README.md")

    assert "* @RandyRDavila" in owners
    assert "/.github/ @RandyRDavila" in owners
    assert "Require the `CI gate` status check" in governance
    assert "Block force pushes and branch deletion" in governance
    assert "Do not require path-limited checks globally" in governance


def test_contribution_and_security_guides_protect_course_data() -> None:
    contributing = read_utf8(PROJECT_ROOT / "CONTRIBUTING.md")
    security = read_utf8(PROJECT_ROOT / "SECURITY.md")

    for required_text in (
        "Windows, macOS, and Linux",
        "uv run pytest -q",
        "make -C textbook",
        "private student information",
        "stable `CI gate`",
    ):
        assert required_text in contributing

    for required_text in (
        "Report a vulnerability privately",
        "GitHub private vulnerability reporting",
        "private student information",
        "untrusted serialized Python objects",
        "least-privilege token permissions",
        "revoke or rotate it first",
    ):
        assert required_text in security
