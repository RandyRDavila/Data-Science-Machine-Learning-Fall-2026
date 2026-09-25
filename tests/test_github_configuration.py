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
        ".github/ISSUE_TEMPLATE/student-contribution.yml",
        ".github/workflows/course-ci.yml",
        ".github/workflows/course-coordination.yml",
        ".github/workflows/course-coordination-digest.yml",
        ".github/workflows/course-pages.yml",
        ".github/workflows/course-release.yml",
        ".github/workflows/course-task-factory.yml",
        ".github/workflows/dependency-review.yml",
        ".github/workflows/pr-labeler.yml",
        ".github/workflows/textbook.yml",
        "CODE_OF_CONDUCT.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "site/index.html",
        "site/favicon.svg",
        "site/styles.css",
        "scripts/build_course_site.py",
        "scripts/build_release_bundle.py",
        "scripts/smoke_test_course_site.py",
        "scripts/scaffold_student_package.py",
        "scripts/course_coordination.py",
        "notes/student-contribution-program.md",
        "notes/shared-platform-launch-lecture.md",
        "notes/final-project-architecture.md",
        ".github/course/coordination.json",
        ".github/course/tasks.json",
        ".github/course/README.md",
        "src/rice_dsm/ml/base.py",
        "src/rice_dsm/ml/README.md",
        "projects/final-product-template/README.md",
        "projects/final-product-template/COURSE_PACKAGE_PROVENANCE.md",
        "projects/final-product-template/PRODUCT_CONTRACT.md",
        "projects/final-product-template/TEAM_OWNERSHIP.md",
        "supplementary-materials/computing-foundations/08-continuous-delivery-and-deployment.md",
        "supplementary-materials/computing-foundations/11-contributing-to-the-shared-course-package.md",
        "supplementary-materials/computing-foundations/12-contribution-quickstart.md",
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
        "## Student contribution evidence",
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
        "requested classmates reviewed",
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
        "uv run python scripts/course_coordination.py validate",
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


def test_privileged_coordination_executes_only_reviewed_default_branch_code() -> None:
    path = WORKFLOW_ROOT / "course-coordination.yml"
    workflow = load_workflow(path)
    workflow_text = read_utf8(path)

    assert "issue_comment" in workflow["on"]
    assert "pull_request_target" in workflow["on"]
    assert "ref: ${{ github.event.repository.default_branch }}" in workflow_text
    assert "persist-credentials: false" in workflow_text
    assert "github.event.pull_request.head" not in workflow_text
    assert "github.head_ref" not in workflow_text
    assert "merge_commit_sha" not in workflow_text
    assert "scripts/course_coordination.py handle-comment" in workflow_text
    assert "scripts/course_coordination.py assign-reviewers" in workflow_text

    assert "contents: read" in workflow_text
    assert "issues: write" in workflow_text
    assert "pull-requests: write" in workflow_text


def test_task_factory_is_dry_run_first_and_apply_is_protected() -> None:
    workflow_text = read_utf8(WORKFLOW_ROOT / "course-task-factory.yml")

    assert "default: false" in workflow_text
    assert "name: Preview task issues" in workflow_text
    assert "--apply" in workflow_text
    assert "environment: course-coordination" in workflow_text
    assert "github.ref == 'refs/heads/main'" in workflow_text
    assert workflow_text.count(
        "ref: ${{ github.event.repository.default_branch }}"
    ) == 2


def test_coordination_digest_is_a_bounded_non_grading_issue_update() -> None:
    workflow_text = read_utf8(WORKFLOW_ROOT / "course-coordination-digest.yml")
    governance = read_utf8(GITHUB_ROOT / "README.md")

    assert 'cron: "17 13 * * 1"' in workflow_text
    assert "scripts/course_coordination.py update-digest" in workflow_text
    assert "pull-requests: read" in workflow_text
    assert "Coordination Digest" in governance
    assert "not grades" in governance


def test_untrusted_pull_request_code_has_read_only_permissions() -> None:
    code_workflows = []

    for workflow_path in WORKFLOWS:
        workflow = load_workflow(workflow_path)
        if "pull_request" in workflow["on"]:
            code_workflows.append(workflow_path.name)
            assert workflow["permissions"] == {"contents": "read"}

    assert code_workflows == [
        "course-ci.yml",
        "dependency-review.yml",
        "textbook.yml",
    ]


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
    assert "/src/rice_dsm/contrib/ @RandyRDavila" in owners
    assert "/tests/contrib/ @RandyRDavila" in owners
    assert "Require the `CI gate` status check" in governance
    assert "Block force pushes and branch deletion" in governance
    assert "Do not require path-limited checks globally" in governance


def test_contribution_and_security_guides_protect_course_data() -> None:
    contributing = read_utf8(PROJECT_ROOT / "CONTRIBUTING.md")
    security = read_utf8(PROJECT_ROOT / "SECURITY.md")
    normalized_security = " ".join(security.split())

    for required_text in (
        "Windows, macOS, and Linux",
        "uv run pytest -q",
        "make -C textbook",
        "private student information",
        "stable `CI gate`",
        "scaffold_student_package.py",
        "CODE_OF_CONDUCT.md",
    ):
        assert required_text in contributing

    for required_text in (
        "Report a vulnerability privately",
        "GitHub private vulnerability reporting",
        "private student information",
        "untrusted serialized Python objects",
        "least-privilege token permissions",
        "revoke or rotate it first",
        "Student contributions arrive from forks",
        "Event titles, bodies, branch names, and comments are untrusted data",
    ):
        assert required_text in normalized_security

    conduct = read_utf8(PROJECT_ROOT / "CODE_OF_CONDUCT.md")
    for required_text in (
        "Critique code, evidence, interfaces, and claims rather than people",
        "Protect private student information",
        "Report conduct or course concerns privately",
    ):
        assert required_text in conduct


def test_student_contribution_guide_defines_the_complete_public_workflow() -> None:
    guide = read_utf8(
        PROJECT_ROOT
        / "supplementary-materials/computing-foundations"
        / "11-contributing-to-the-shared-course-package.md"
    )
    namespace = read_utf8(PROJECT_ROOT / "src/rice_dsm/contrib/README.md")

    for required_text in (
        "upstream repository",
        "git remote add upstream",
        "scaffold_student_package.py",
        "red-green-refactor",
        "peer reviewer",
        "git merge --abort",
        "privacy",
        "maintenance responsibility",
    ):
        assert required_text in guide

    for required_text in (
        "explicitly",
        "NumPy-style docstrings",
        "data provenance",
        "Importing a contribution must not",
    ):
        assert required_text in namespace


def test_shared_ml_platform_and_final_product_boundaries_are_explicit() -> None:
    platform = read_utf8(PROJECT_ROOT / "src/rice_dsm/ml/README.md")
    final_project = read_utf8(PROJECT_ROOT / "notes/final-project-architecture.md")
    normalized_final_project = " ".join(final_project.split())
    product_template = read_utf8(
        PROJECT_ROOT / "projects/final-product-template/README.md"
    )

    for required_text in (
        "tagged `rice-dsm` release",
        "structural protocols",
        "differential comparison",
        "From incubation to integration",
    ):
        assert required_text in platform

    for required_text in (
        "approximately forty students",
        "one to four participants",
        "process evidence",
        "Commit counts",
    ):
        assert required_text in normalized_final_project

    for required_text in (
        "at least one regression task",
        "at least one classification task",
        "unsupervised",
        "Exact shared-platform dependency",
        "Scope scales with team size",
    ):
        assert required_text in product_template
