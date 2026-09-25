"""Coordinate public course tasks and peer reviews through the GitHub API.

The module keeps selection and validation logic pure where possible so CI can
test it without network access. Live mutation requires both an enabled,
reviewed configuration and an explicit command invoked by a least-privilege
GitHub Actions workflow.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections.abc import Iterable, Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COURSE_CONFIG = PROJECT_ROOT / ".github" / "course" / "coordination.json"
TASK_MANIFEST = PROJECT_ROOT / ".github" / "course" / "tasks.json"
GITHUB_API = "https://api.github.com"
API_VERSION = "2026-03-10"
LOGIN_PATTERN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?")
TASK_ID_PATTERN = re.compile(r"[a-z][a-z0-9-]{2,49}")
TASK_MARKER_PATTERN = re.compile(r"<!--\s*course-task-id:\s*([a-z0-9-]+)\s*-->")
LINKED_ISSUE_PATTERN = re.compile(
    r"(?i)\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)"
)

LABELS = {
    "course: work": ("0052cc", "Shared-platform issue or pull request"),
    "course: task": ("1d76db", "Shared-platform course task"),
    "status: ready": ("0e8a16", "Ready for students to claim"),
    "status: claimed": ("fbca04", "Claimed by one or more participants"),
    "review: peer-requested": ("5319e7", "Peer reviews have been requested"),
    "course: coordination": ("bfdadc", "Course-coordination automation"),
}


class GitHubAPIError(RuntimeError):
    """Raised when GitHub rejects a coordination request."""


class GitHubAPI:
    """Minimal authenticated client for repository coordination endpoints."""

    def __init__(self, repository: str, token: str) -> None:
        if repository.count("/") != 1:
            raise ValueError("repository must have the form OWNER/NAME")
        if not token:
            raise ValueError("a GitHub token is required for live coordination")
        self.repository = repository
        self.token = token

    def request(
        self,
        method: str,
        path: str,
        *,
        payload: Mapping[str, Any] | None = None,
        query: Mapping[str, str | int] | None = None,
    ) -> Any:
        """Send one JSON request and return the decoded response."""

        suffix = f"?{urlencode(query)}" if query else ""
        url = f"{GITHUB_API}/repos/{self.repository}{path}{suffix}"
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(
            url,
            data=data,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "User-Agent": "rice-dsm-course-coordination",
                "X-GitHub-Api-Version": API_VERSION,
                **({"Content-Type": "application/json"} if data else {}),
            },
        )
        try:
            with urlopen(request, timeout=30) as response:  # noqa: S310
                body = response.read()
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise GitHubAPIError(
                f"GitHub {method} {path} failed with {error.code}: {detail}"
            ) from error
        return json.loads(body) if body else None

    def paginate(
        self,
        path: str,
        *,
        query: Mapping[str, str | int] | None = None,
    ) -> list[Any]:
        """Collect list results from ordinary page-number pagination."""

        collected: list[Any] = []
        page = 1
        while True:
            parameters = {**(query or {}), "per_page": 100, "page": page}
            result = self.request("GET", path, query=parameters)
            if not isinstance(result, list):
                raise GitHubAPIError(f"expected a list response from {path}")
            collected.extend(result)
            if len(result) < 100:
                return collected
            page += 1


def load_json_object(path: Path) -> dict[str, Any]:
    """Load a UTF-8 JSON object from ``path``."""

    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return document


def validate_configuration(
    config: Mapping[str, Any], manifest: Mapping[str, Any]
) -> tuple[str, ...]:
    """Return all structural errors in coordination configuration."""

    errors: list[str] = []
    if config.get("version") != 1:
        errors.append("coordination version must equal 1")
    if not isinstance(config.get("enabled"), bool):
        errors.append("enabled must be Boolean")

    for field in (
        "max_active_tasks_per_participant",
        "default_max_task_team_size",
        "reviewers_per_pull_request",
        "stale_after_days",
    ):
        value = config.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            errors.append(f"{field} must be a positive integer")

    paths = config.get("contribution_paths")
    if not isinstance(paths, list) or not paths or not all(
        isinstance(path, str) and path and not path.startswith("/") for path in paths
    ):
        errors.append("contribution_paths must be nonempty repository-relative paths")

    participants = config.get("participants")
    if not isinstance(participants, list):
        errors.append("participants must be a list")
        participants = []

    logins: list[str] = []
    for index, participant in enumerate(participants):
        if not isinstance(participant, dict):
            errors.append(f"participant {index} must be an object")
            continue
        login = participant.get("login")
        if not isinstance(login, str) or LOGIN_PATTERN.fullmatch(login) is None:
            errors.append(f"participant {index} has an invalid GitHub login")
        else:
            logins.append(login.casefold())
        for field in ("active", "reviewer"):
            if not isinstance(participant.get(field), bool):
                errors.append(f"participant {index} field {field} must be Boolean")
        for field in ("guild", "product_team"):
            value = participant.get(field)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                errors.append(
                    f"participant {index} field {field} must be null or nonempty text"
                )

    if len(logins) != len(set(logins)):
        errors.append("participant GitHub logins must be unique ignoring case")
    if config.get("enabled") and not participants:
        errors.append("enabled coordination requires at least one participant")

    errors.extend(validate_task_manifest(manifest))
    return tuple(errors)


def validate_task_manifest(manifest: Mapping[str, Any]) -> tuple[str, ...]:
    """Return all structural and dependency errors in the task manifest."""

    errors: list[str] = []
    if manifest.get("version") != 1:
        errors.append("task-manifest version must equal 1")
    tasks = manifest.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        return (*errors, "tasks must be a nonempty list")

    task_ids: list[str] = []
    dependencies_by_id: dict[str, list[str]] = {}
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            errors.append(f"task {index} must be an object")
            continue
        task_id = task.get("id")
        if not isinstance(task_id, str) or TASK_ID_PATTERN.fullmatch(task_id) is None:
            errors.append(f"task {index} has an invalid id")
            continue
        task_ids.append(task_id)
        for field in ("title", "family", "summary"):
            if not isinstance(task.get(field), str) or not task[field].strip():
                errors.append(f"task {task_id} field {field} must be nonempty text")
        for field in ("complexity", "max_team_size"):
            value = task.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                errors.append(f"task {task_id} field {field} must be positive")
        dependencies = task.get("dependencies")
        if not isinstance(dependencies, list) or not all(
            isinstance(dependency, str) for dependency in dependencies
        ):
            errors.append(f"task {task_id} dependencies must be a list of ids")
            dependencies = []
        dependencies_by_id[task_id] = dependencies
        acceptance = task.get("acceptance")
        if not isinstance(acceptance, list) or len(acceptance) < 2 or not all(
            isinstance(item, str) and item.strip() for item in acceptance
        ):
            errors.append(f"task {task_id} requires at least two acceptance criteria")

    if len(task_ids) != len(set(task_ids)):
        errors.append("task ids must be unique")

    known_ids = set(task_ids)
    for task_id, dependencies in dependencies_by_id.items():
        for dependency in dependencies:
            if dependency not in known_ids:
                errors.append(f"task {task_id} has unknown dependency {dependency}")
            if dependency == task_id:
                errors.append(f"task {task_id} cannot depend on itself")

    errors.extend(_dependency_cycle_errors(dependencies_by_id))
    return tuple(errors)


def _dependency_cycle_errors(graph: Mapping[str, Sequence[str]]) -> list[str]:
    errors: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str, route: tuple[str, ...]) -> None:
        if task_id in visiting:
            start = route.index(task_id)
            cycle = " -> ".join(route[start:] + (task_id,))
            errors.append(f"task dependency cycle: {cycle}")
            return
        if task_id in visited:
            return
        visiting.add(task_id)
        # Unknown dependency ids are reported separately.
        for dependency in graph.get(task_id, ()):
            if dependency in graph:
                visit(dependency, route + (task_id,))
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in graph:
        visit(task_id, ())
    return errors


def participant_by_login(
    participants: Iterable[Mapping[str, Any]], login: str
) -> Mapping[str, Any] | None:
    """Find an active participant using case-insensitive GitHub identity."""

    normalized = login.casefold()
    return next(
        (
            participant
            for participant in participants
            if participant.get("active") is True
            and str(participant.get("login", "")).casefold() == normalized
        ),
        None,
    )


def linked_issue_numbers(body: str | None) -> tuple[int, ...]:
    """Extract unique closing-reference issue numbers from a pull-request body."""

    matches = LINKED_ISSUE_PATTERN.findall(body or "")
    return tuple(dict.fromkeys(int(match) for match in matches))


def task_id_from_body(body: str | None) -> str | None:
    """Return the generated task id marker from an issue body."""

    match = TASK_MARKER_PATTERN.search(body or "")
    return match.group(1) if match else None


def contribution_files_changed(
    filenames: Iterable[str], prefixes: Sequence[str]
) -> bool:
    """Return whether a pull request changes a configured contribution path."""

    return any(
        filename == prefix.rstrip("/") or filename.startswith(prefix)
        for filename in filenames
        for prefix in prefixes
    )


def select_reviewers(
    participants: Sequence[Mapping[str, Any]],
    *,
    author: str,
    excluded_logins: Iterable[str],
    workload: Mapping[str, int],
    count: int,
    pull_request_number: int,
) -> tuple[str, ...]:
    """Choose reviewers by availability, independence, load, and stable tie-break."""

    excluded = {login.casefold() for login in excluded_logins}
    excluded.add(author.casefold())
    author_record = participant_by_login(participants, author)
    author_guild = author_record.get("guild") if author_record else None
    author_product_team = author_record.get("product_team") if author_record else None

    candidates: list[tuple[bool, int, str, str]] = []
    for participant in participants:
        login = str(participant.get("login", ""))
        if (
            participant.get("active") is not True
            or participant.get("reviewer") is not True
            or login.casefold() in excluded
        ):
            continue
        candidate_team = participant.get("product_team")
        if author_product_team is not None and candidate_team == author_product_team:
            continue
        same_guild = (
            author_guild is not None and participant.get("guild") == author_guild
        )
        stable_tie = hashlib.sha256(
            f"{pull_request_number}:{login.casefold()}".encode()
        ).hexdigest()
        candidates.append(
            (same_guild, workload.get(login.casefold(), 0), stable_tie, login)
        )

    candidates.sort()
    return tuple(candidate[3] for candidate in candidates[:count])


def render_task_issue(task: Mapping[str, Any]) -> str:
    """Render an auditable issue body from one manifest task."""

    dependencies = task["dependencies"]
    dependency_text = ", ".join(f"`{item}`" for item in dependencies) or "None"
    acceptance = "\n".join(f"- [ ] {item}" for item in task["acceptance"])
    return f"""<!-- course-task-id: {task['id']} -->

## Purpose

{task['summary']}

## Planning metadata

- Family: `{task['family']}`
- Complexity signal: `{task['complexity']}`
- Maximum active contributors: `{task['max_team_size']}`
- Manifest dependencies: {dependency_text}

Complexity supports workload planning; it is not a grade. Confirm prerequisite
issues and the current lecture contract before implementation.

## Acceptance evidence

{acceptance}

## Contribution process

1. Read the mathematical and software contract in the relevant lecture material.
2. Comment `/claim` after the instructor marks the task ready.
3. Propose interface changes before implementing a large patch.
4. Link the pull request with `Closes #ISSUE_NUMBER`.
5. Obtain peer review, pass CI, and receive final maintainer review.

Never post grades, student IDs, credentials, private student information, or
restricted data in this public issue.
"""


def ensure_label(api: GitHubAPI, name: str, color: str, description: str) -> None:
    """Create a repository label when it does not already exist."""

    try:
        api.request("GET", f"/labels/{quote(name, safe='')}")
    except GitHubAPIError as error:
        if "failed with 404" not in str(error):
            raise
        api.request(
            "POST",
            "/labels",
            payload={"name": name, "color": color, "description": description},
        )


def add_labels(api: GitHubAPI, issue_number: int, labels: Sequence[str]) -> None:
    """Add labels without replacing existing issue labels."""

    api.request(
        "POST", f"/issues/{issue_number}/labels", payload={"labels": list(labels)}
    )


def remove_label(api: GitHubAPI, issue_number: int, label: str) -> None:
    """Remove a label, tolerating the label already being absent."""

    try:
        api.request("DELETE", f"/issues/{issue_number}/labels/{quote(label, safe='')}")
    except GitHubAPIError as error:
        if "failed with 404" not in str(error):
            raise


def post_comment(api: GitHubAPI, issue_number: int, body: str) -> None:
    """Post one visible coordination decision."""

    api.request("POST", f"/issues/{issue_number}/comments", payload={"body": body})


def require_live_configuration(config: Mapping[str, Any]) -> None:
    """Refuse every mutation while reviewed automation is disabled."""

    if config.get("enabled") is not True:
        raise RuntimeError(
            "course coordination is disabled; review the opt-in roster before "
            "enabling it"
        )


def create_tasks(
    api: GitHubAPI | None,
    config: Mapping[str, Any],
    manifest: Mapping[str, Any],
    *,
    requested_ids: Sequence[str],
    apply: bool,
) -> list[str]:
    """Preview or create manifest tasks without duplicating existing ids."""

    tasks = {task["id"]: task for task in manifest["tasks"]}
    selected_ids = list(tasks) if requested_ids == ["all"] else list(requested_ids)
    unknown = sorted(set(selected_ids) - tasks.keys())
    if unknown:
        raise ValueError(f"unknown task id(s): {', '.join(unknown)}")

    preview = [f"{task_id}: {tasks[task_id]['title']}" for task_id in selected_ids]
    if not apply:
        return preview

    require_live_configuration(config)
    if api is None:
        raise ValueError("a GitHub API client is required when apply=True")
    for label, (color, description) in LABELS.items():
        ensure_label(api, label, color, description)

    existing_issues = api.paginate(
        "/issues", query={"state": "all", "labels": "course: task"}
    )
    existing_ids = {
        marker
        for issue in existing_issues
        if "pull_request" not in issue
        if (marker := task_id_from_body(issue.get("body"))) is not None
    }

    for task_id in selected_ids:
        if task_id in existing_ids:
            continue
        task = tasks[task_id]
        family_label = f"family: {task['family']}"
        ensure_label(api, family_label, "c5def5", "Course task family")
        api.request(
            "POST",
            "/issues",
            payload={
                "title": f"[Course task] {task['title']}",
                "body": render_task_issue(task),
                "labels": [
                    "course: work",
                    "course: task",
                    "status: ready",
                    family_label,
                ],
            },
        )
    return preview


def handle_issue_comment(
    api: GitHubAPI,
    config: Mapping[str, Any],
    manifest: Mapping[str, Any],
    event: Mapping[str, Any],
) -> str:
    """Handle an exact ``/claim`` or ``/release`` issue comment."""

    command = str(event["comment"]["body"]).strip().casefold()
    if command not in {"/claim", "/release"}:
        return "ignored: not a coordination command"
    if event["issue"].get("pull_request") is not None:
        return "ignored: commands apply to issues, not pull requests"
    if config.get("enabled") is not True:
        return "ignored: course coordination is disabled"

    require_live_configuration(config)
    login = str(event["comment"]["user"]["login"])
    participant = participant_by_login(config["participants"], login)
    if participant is None:
        post_comment(
            api,
            int(event["issue"]["number"]),
            f"@{login}, this command is limited to active, opt-in course participants. "
            "Contact the instructor privately if the roster needs correction.",
        )
        return "rejected: participant not active"

    issue = event["issue"]
    issue_number = int(issue["number"])
    label_names = {label["name"] for label in issue.get("labels", [])}
    if "course: task" not in label_names:
        return "ignored: issue is not a generated course task"

    task_id = task_id_from_body(issue.get("body"))
    tasks = {task["id"]: task for task in manifest["tasks"]}
    if task_id not in tasks:
        raise RuntimeError("course task issue has an unknown or missing task marker")

    assignees = [assignee["login"] for assignee in issue.get("assignees", [])]
    normalized_assignees = {assignee.casefold() for assignee in assignees}
    if command == "/release":
        if login.casefold() not in normalized_assignees:
            return "ignored: participant is not assigned"
        api.request(
            "DELETE",
            f"/issues/{issue_number}/assignees",
            payload={"assignees": [login]},
        )
        remaining = [name for name in assignees if name.casefold() != login.casefold()]
        if not remaining:
            remove_label(api, issue_number, "status: claimed")
            add_labels(api, issue_number, ["status: ready"])
        post_comment(api, issue_number, f"@{login} released this task assignment.")
        return "released"

    if login.casefold() in normalized_assignees:
        return "ignored: participant is already assigned"
    if len(assignees) >= int(tasks[task_id]["max_team_size"]):
        post_comment(
            api,
            issue_number,
            f"@{login}, this task already has its maximum active team. Choose another "
            "ready task or ask the instructor to revisit its scope.",
        )
        return "rejected: task team is full"

    active_issues = api.paginate(
        "/issues",
        query={"state": "open", "assignee": login, "labels": "course: task"},
    )
    active_count = sum(
        1
        for active_issue in active_issues
        if "pull_request" not in active_issue and active_issue["number"] != issue_number
    )
    if active_count >= int(config["max_active_tasks_per_participant"]):
        post_comment(
            api,
            issue_number,
            f"@{login}, finish or release your current course task before claiming "
            "another one. This limit keeps work visible and reviewable.",
        )
        return "rejected: active-task limit reached"

    api.request(
        "POST", f"/issues/{issue_number}/assignees", payload={"assignees": [login]}
    )
    remove_label(api, issue_number, "status: ready")
    add_labels(api, issue_number, ["status: claimed"])
    post_comment(
        api,
        issue_number,
        f"Assigned to @{login}. Begin with the stated contract and open a draft pull "
        "request early when interface feedback would prevent rework. Use `/release` "
        "if you cannot continue.",
    )
    return "claimed"


def assign_peer_reviewers(
    api: GitHubAPI,
    config: Mapping[str, Any],
    event: Mapping[str, Any],
) -> tuple[str, ...]:
    """Request balanced peer reviews for a contribution pull request."""

    if config.get("enabled") is not True:
        return ()
    require_live_configuration(config)
    pull_request = event["pull_request"]
    if pull_request.get("draft"):
        return ()
    number = int(pull_request["number"])
    files = api.paginate(f"/pulls/{number}/files")
    if not contribution_files_changed(
        (item["filename"] for item in files), config["contribution_paths"]
    ):
        return ()

    existing_labels = {label["name"] for label in pull_request.get("labels", [])}
    if "review: peer-requested" in existing_labels:
        return tuple(
            reviewer["login"]
            for reviewer in pull_request.get("requested_reviewers", [])
        )

    excluded = {
        reviewer["login"] for reviewer in pull_request.get("requested_reviewers", [])
    }
    for issue_number in linked_issue_numbers(pull_request.get("body")):
        linked_issue = api.request("GET", f"/issues/{issue_number}")
        excluded.update(assignee["login"] for assignee in linked_issue["assignees"])

    reviews = api.paginate(f"/pulls/{number}/reviews")
    excluded.update(review["user"]["login"] for review in reviews)

    workload: dict[str, int] = {}
    for open_pull in api.paginate("/pulls", query={"state": "open"}):
        for reviewer in open_pull.get("requested_reviewers", []):
            key = reviewer["login"].casefold()
            workload[key] = workload.get(key, 0) + 1

    reviewers = select_reviewers(
        config["participants"],
        author=pull_request["user"]["login"],
        excluded_logins=excluded,
        workload=workload,
        count=int(config["reviewers_per_pull_request"]),
        pull_request_number=number,
    )
    if not reviewers:
        post_comment(
            api,
            number,
            "Peer-review automation found no eligible reviewer. The maintainer must "
            "assign this pull request manually.",
        )
        return ()

    api.request(
        "POST",
        f"/pulls/{number}/requested_reviewers",
        payload={"reviewers": list(reviewers)},
    )
    for label, (color, description) in LABELS.items():
        if label in {"course: work", "review: peer-requested"}:
            ensure_label(api, label, color, description)
    add_labels(api, number, ["course: work", "review: peer-requested"])
    mentions = " and ".join(f"@{reviewer}" for reviewer in reviewers)
    post_comment(
        api,
        number,
        f"Peer review requested from {mentions}. Review the mathematical or scientific "
        "contract, boundary and failure behavior, tests, provenance, and limitations. "
        "A peer review is instructional evidence; final integration remains a "
        "maintainer decision.",
    )
    return reviewers


def render_digest(
    issues: Sequence[Mapping[str, Any]],
    pulls: Sequence[Mapping[str, Any]],
    *,
    stale_after_days: int,
    now: datetime,
) -> str:
    """Render a status digest without grades or quality scores."""

    cutoff_seconds = stale_after_days * 24 * 60 * 60

    def stale(item: Mapping[str, Any]) -> bool:
        updated = datetime.fromisoformat(str(item["updated_at"]).replace("Z", "+00:00"))
        return (now - updated).total_seconds() >= cutoff_seconds

    ready = [issue for issue in issues if not issue.get("assignees")]
    stale_issues = [issue for issue in issues if stale(issue)]
    awaiting_review = [pull for pull in pulls if pull.get("requested_reviewers")]
    stale_pulls = [pull for pull in pulls if stale(pull)]

    def links(items: Sequence[Mapping[str, Any]]) -> str:
        return "\n".join(
            f"- [#{item['number']}]({item['html_url']}) {item['title']}"
            for item in items
        ) or "- None"

    return f"""# Course coordination digest

Generated at {now.astimezone(UTC).isoformat(timespec="seconds")} from public
GitHub workflow state. This is an operational queue, not a grade or a measure
of contribution quality.

## Ready or unclaimed tasks

{links(ready)}

## Tasks without recent activity

{links(stale_issues)}

## Pull requests awaiting peer review

{links(awaiting_review)}

## Pull requests without recent activity

{links(stale_pulls)}
"""


def update_digest(api: GitHubAPI, config: Mapping[str, Any]) -> str:
    """Create or update the single public coordination digest issue."""

    if config.get("enabled") is not True:
        return "skipped because coordination is disabled"
    require_live_configuration(config)
    for label, (color, description) in LABELS.items():
        if label == "course: coordination":
            ensure_label(api, label, color, description)
    issues = [
        item
        for item in api.paginate(
            "/issues", query={"state": "open", "labels": "course: task"}
        )
        if "pull_request" not in item
    ]
    pulls = api.paginate("/pulls", query={"state": "open"})
    body = render_digest(
        issues,
        pulls,
        stale_after_days=int(config["stale_after_days"]),
        now=datetime.now(UTC),
    )
    digest_issues = [
        item
        for item in api.paginate(
            "/issues", query={"state": "open", "labels": "course: coordination"}
        )
        if "pull_request" not in item
        and item["title"] == "[Coordination] Shared-platform status"
    ]
    if digest_issues:
        api.request(
            "PATCH", f"/issues/{digest_issues[0]['number']}", payload={"body": body}
        )
        return "updated"
    api.request(
        "POST",
        "/issues",
        payload={
            "title": "[Coordination] Shared-platform status",
            "body": body,
            "labels": ["course: coordination"],
        },
    )
    return "created"


def load_event(path: str | None) -> dict[str, Any]:
    """Load the GitHub event JSON selected by the runner."""

    if not path:
        raise ValueError("GITHUB_EVENT_PATH is required")
    return load_json_object(Path(path))


def live_api() -> GitHubAPI:
    """Construct the API client from GitHub Actions environment variables."""

    return GitHubAPI(
        os.environ.get("GITHUB_REPOSITORY", ""), os.environ.get("GITHUB_TOKEN", "")
    )


def parse_requested_ids(value: str) -> list[str]:
    """Parse a comma-separated task selection."""

    task_ids = [item.strip() for item in value.split(",") if item.strip()]
    if not task_ids:
        raise ValueError("at least one task id or 'all' is required")
    if "all" in task_ids and task_ids != ["all"]:
        raise ValueError("'all' cannot be combined with individual task ids")
    return task_ids


def build_parser() -> argparse.ArgumentParser:
    """Build the coordination command-line interface."""

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="validate configuration and task manifest")
    subparsers.add_parser("handle-comment", help="process a /claim or /release event")
    subparsers.add_parser(
        "assign-reviewers", help="request balanced reviews for a contribution PR"
    )
    task_parser = subparsers.add_parser(
        "create-tasks", help="preview or create task issues from the manifest"
    )
    task_parser.add_argument(
        "--task-ids",
        default="all",
        help="comma-separated ids or 'all'; defaults to all",
    )
    task_parser.add_argument(
        "--apply",
        action="store_true",
        help="create issues; omission performs a local dry run",
    )
    subparsers.add_parser("update-digest", help="create or update the status digest")
    return parser


def main() -> int:
    """Validate or execute one explicit coordination operation."""

    arguments = build_parser().parse_args()
    config = load_json_object(COURSE_CONFIG)
    manifest = load_json_object(TASK_MANIFEST)
    errors = validate_configuration(config, manifest)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 2

    if arguments.command == "validate":
        print(
            f"Valid coordination config: {len(config['participants'])} participant(s), "
            f"{len(manifest['tasks'])} task(s), enabled={config['enabled']}"
        )
        return 0

    if arguments.command == "create-tasks":
        selected_ids = parse_requested_ids(arguments.task_ids)
        if arguments.apply:
            preview = create_tasks(
                live_api(), config, manifest, requested_ids=selected_ids, apply=True
            )
        else:
            preview = create_tasks(
                None,
                config,
                manifest,
                requested_ids=selected_ids,
                apply=False,
            )
        print("\n".join(preview))
        if not arguments.apply:
            print(
                "Dry run only: pass --apply through the protected workflow to mutate."
            )
        return 0

    api = live_api()
    if arguments.command == "handle-comment":
        print(
            handle_issue_comment(
                api, config, manifest, load_event(os.environ.get("GITHUB_EVENT_PATH"))
            )
        )
    elif arguments.command == "assign-reviewers":
        reviewers = assign_peer_reviewers(
            api, config, load_event(os.environ.get("GITHUB_EVENT_PATH"))
        )
        print(f"Requested reviewers: {', '.join(reviewers) if reviewers else 'none'}")
    elif arguments.command == "update-digest":
        print(f"Digest {update_digest(api, config)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
