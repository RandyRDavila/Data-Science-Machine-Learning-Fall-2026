"""Tests for task, reviewer, and digest coordination without GitHub access."""

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from scripts.course_coordination import (
    assign_peer_reviewers,
    contribution_files_changed,
    create_tasks,
    handle_issue_comment,
    linked_issue_numbers,
    load_json_object,
    parse_requested_ids,
    render_digest,
    render_task_issue,
    select_reviewers,
    task_id_from_body,
    validate_configuration,
)

PROJECT_ROOT = Path(__file__).parents[1]
CONFIG_PATH = PROJECT_ROOT / ".github/course/coordination.json"
TASK_PATH = PROJECT_ROOT / ".github/course/tasks.json"


class FakeAPI:
    """Record coordination calls while returning explicit fixture pages."""

    def __init__(self, pages: dict[tuple[str, str], object] | None = None) -> None:
        self.pages = pages or {}
        self.calls: list[tuple[str, str, object]] = []

    def request(
        self,
        method: str,
        path: str,
        *,
        payload: object = None,
        query: object = None,
    ) -> object:
        self.calls.append((method, path, payload))
        return self.pages.get((method, path), {})

    def paginate(self, path: str, *, query: object = None) -> list[object]:
        self.calls.append(("PAGINATE", path, query))
        result = self.pages.get(("PAGINATE", path), [])
        assert isinstance(result, list)
        return result


def participant(
    login: str,
    *,
    guild: str,
    product_team: str | None = None,
    reviewer: bool = True,
) -> dict[str, object]:
    """Build one public-roster fixture."""

    return {
        "login": login,
        "active": True,
        "reviewer": reviewer,
        "guild": guild,
        "product_team": product_team,
    }


def test_committed_coordination_inputs_are_valid_and_disabled_by_default() -> None:
    config = load_json_object(CONFIG_PATH)
    manifest = load_json_object(TASK_PATH)

    assert validate_configuration(config, manifest) == ()
    assert config["enabled"] is False
    assert config["participants"] == []
    assert len(manifest["tasks"]) >= 16


def test_enabled_automation_requires_an_opt_in_roster() -> None:
    config = load_json_object(CONFIG_PATH)
    config["enabled"] = True

    errors = validate_configuration(config, load_json_object(TASK_PATH))

    assert "enabled coordination requires at least one participant" in errors


def test_disabled_comment_automation_makes_no_api_calls() -> None:
    config = load_json_object(CONFIG_PATH)
    manifest = load_json_object(TASK_PATH)
    event = {
        "comment": {"body": "/claim", "user": {"login": "student"}},
        "issue": {"number": 1, "labels": [], "assignees": [], "body": ""},
    }
    api = FakeAPI()

    result = handle_issue_comment(api, config, manifest, event)  # type: ignore[arg-type]

    assert result == "ignored: course coordination is disabled"
    assert api.calls == []


def test_only_exact_claim_and_release_commands_are_interpreted() -> None:
    config = load_json_object(CONFIG_PATH)
    config["enabled"] = True
    config["participants"] = [participant("student", guild="linear")]
    manifest = load_json_object(TASK_PATH)
    event = {
        "comment": {
            "body": "/claim && publish-a-secret",
            "user": {"login": "student"},
        },
        "issue": {"number": 1, "labels": [], "assignees": [], "body": ""},
    }
    api = FakeAPI()

    result = handle_issue_comment(api, config, manifest, event)  # type: ignore[arg-type]

    assert result == "ignored: not a coordination command"
    assert api.calls == []


def test_active_participant_can_claim_one_ready_generated_task() -> None:
    config = load_json_object(CONFIG_PATH)
    config["enabled"] = True
    config["participants"] = [participant("student", guild="linear")]
    manifest = load_json_object(TASK_PATH)
    task = manifest["tasks"][0]
    event = {
        "comment": {"body": "/claim", "user": {"login": "student"}},
        "issue": {
            "number": 42,
            "labels": [{"name": "course: task"}, {"name": "status: ready"}],
            "assignees": [],
            "body": render_task_issue(task),
        },
    }
    api = FakeAPI()

    result = handle_issue_comment(api, config, manifest, event)  # type: ignore[arg-type]

    assert result == "claimed"
    assert (
        "POST",
        "/issues/42/assignees",
        {"assignees": ["student"]},
    ) in api.calls
    assert (
        "POST",
        "/issues/42/labels",
        {"labels": ["status: claimed"]},
    ) in api.calls


def test_task_manifest_rejects_unknown_dependencies_and_cycles() -> None:
    config = load_json_object(CONFIG_PATH)
    manifest = {
        "version": 1,
        "tasks": [
            {
                "id": "task-a",
                "title": "Task A",
                "family": "test",
                "complexity": 1,
                "max_team_size": 1,
                "dependencies": ["task-b", "missing-task"],
                "summary": "A valid summary.",
                "acceptance": ["First criterion.", "Second criterion."],
            },
            {
                "id": "task-b",
                "title": "Task B",
                "family": "test",
                "complexity": 1,
                "max_team_size": 1,
                "dependencies": ["task-a"],
                "summary": "Another valid summary.",
                "acceptance": ["First criterion.", "Second criterion."],
            },
        ],
    }

    errors = validate_configuration(config, manifest)

    assert "task task-a has unknown dependency missing-task" in errors
    assert any(error.startswith("task dependency cycle:") for error in errors)


def test_linked_issues_are_unique_and_require_closing_language() -> None:
    body = "Closes #12, fixes #9, and closes #12. Related to #44."

    assert linked_issue_numbers(body) == (12, 9)
    assert linked_issue_numbers(None) == ()


def test_task_issue_round_trip_preserves_machine_marker_and_human_contract() -> None:
    task = load_json_object(TASK_PATH)["tasks"][0]

    body = render_task_issue(task)

    assert task_id_from_body(body) == task["id"]
    assert "## Acceptance evidence" in body
    assert "/claim" in body
    assert "not a grade" in body


def test_dry_run_previews_tasks_without_api_or_enabled_roster() -> None:
    config = load_json_object(CONFIG_PATH)
    manifest = load_json_object(TASK_PATH)

    preview = create_tasks(
        None,
        config,
        manifest,
        requested_ids=[manifest["tasks"][0]["id"]],
        apply=False,
    )

    assert preview == [
        f"{manifest['tasks'][0]['id']}: {manifest['tasks'][0]['title']}"
    ]


@pytest.mark.parametrize(
    ("value", "expected"),
    [("all", ["all"]), ("linear-regression, knn", ["linear-regression", "knn"])],
)
def test_task_selection_parses_explicit_ids(value: str, expected: list[str]) -> None:
    assert parse_requested_ids(value) == expected


@pytest.mark.parametrize("value", ["", "all,knn"])
def test_task_selection_rejects_ambiguous_values(value: str) -> None:
    with pytest.raises(ValueError):
        parse_requested_ids(value)


def test_contribution_paths_are_repository_relative_prefixes() -> None:
    prefixes = load_json_object(CONFIG_PATH)["contribution_paths"]

    assert contribution_files_changed(["src/rice_dsm/ml/linear.py"], prefixes)
    assert contribution_files_changed(["tests/test_ml_linear.py"], prefixes)
    assert not contribution_files_changed(
        ["textbook/chapters/introduction.tex"], prefixes
    )


def test_reviewer_selection_excludes_authors_collaborators_and_product_team() -> None:
    roster = [
        participant("author", guild="linear", product_team="product-a"),
        participant("teammate", guild="trees", product_team="product-a"),
        participant("issue-partner", guild="neighbors"),
        participant("cross-guild", guild="trees"),
        participant("same-guild", guild="linear"),
    ]

    selected = select_reviewers(
        roster,
        author="author",
        excluded_logins={"issue-partner"},
        workload={},
        count=2,
        pull_request_number=17,
    )

    assert selected == ("cross-guild", "same-guild")
    assert "teammate" not in selected


def test_reviewer_selection_balances_load_before_stable_tie_breaking() -> None:
    roster = [
        participant("author", guild="linear"),
        participant("busy", guild="trees"),
        participant("available", guild="trees"),
        participant("not-reviewing", guild="neighbors", reviewer=False),
    ]

    selected = select_reviewers(
        roster,
        author="author",
        excluded_logins=(),
        workload={"busy": 3, "available": 0},
        count=1,
        pull_request_number=18,
    )

    assert selected == ("available",)


def test_peer_review_automation_requests_review_without_reading_fork_code() -> None:
    config = load_json_object(CONFIG_PATH)
    config["enabled"] = True
    config["participants"] = [
        participant("author", guild="linear"),
        participant("reviewer-a", guild="trees"),
        participant("reviewer-b", guild="neighbors"),
    ]
    event = {
        "pull_request": {
            "number": 21,
            "draft": False,
            "body": "No closing issue yet.",
            "user": {"login": "author"},
            "labels": [],
            "requested_reviewers": [],
        }
    }
    api = FakeAPI(
        {
            ("PAGINATE", "/pulls/21/files"): [
                {"filename": "src/rice_dsm/ml/linear_models/regression.py"}
            ],
            ("PAGINATE", "/pulls/21/reviews"): [],
            ("PAGINATE", "/pulls"): [],
            ("GET", "/labels/review%3A%20peer-requested"): {},
        }
    )

    selected = assign_peer_reviewers(api, config, event)  # type: ignore[arg-type]

    assert set(selected) == {"reviewer-a", "reviewer-b"}
    assert (
        "POST",
        "/pulls/21/requested_reviewers",
        {"reviewers": list(selected)},
    ) in api.calls


def test_digest_reports_workflow_state_without_grades() -> None:
    now = datetime(2026, 9, 25, 15, tzinfo=UTC)
    stale_time = (now - timedelta(days=8)).isoformat().replace("+00:00", "Z")
    recent_time = (now - timedelta(days=1)).isoformat().replace("+00:00", "Z")
    issues = [
        {
            "number": 10,
            "title": "Ready task",
            "html_url": "https://example.test/issues/10",
            "updated_at": recent_time,
            "assignees": [],
        },
        {
            "number": 11,
            "title": "Stale claimed task",
            "html_url": "https://example.test/issues/11",
            "updated_at": stale_time,
            "assignees": [{"login": "student"}],
        },
    ]
    pulls = [
        {
            "number": 12,
            "title": "Awaiting review",
            "html_url": "https://example.test/pull/12",
            "updated_at": stale_time,
            "labels": [{"name": "review: peer-requested"}],
            "requested_reviewers": [{"login": "reviewer"}],
        },
        {
            "number": 13,
            "title": "Completed review",
            "html_url": "https://example.test/pull/13",
            "updated_at": recent_time,
            "labels": [{"name": "review: peer-requested"}],
            "requested_reviewers": [],
        }
    ]

    digest = render_digest(issues, pulls, stale_after_days=7, now=now)

    assert "Ready task" in digest
    assert "Stale claimed task" in digest
    assert "Awaiting review" in digest
    assert "Completed review" not in digest
    assert "not a grade" in digest
