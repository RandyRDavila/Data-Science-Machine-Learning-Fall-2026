"""Fast-forward main and prepare the complete course environment.

Run from the repository root on macOS, Linux, or Windows:

    uv run --isolated --no-project --python 3.12.13 python scripts/refresh_course.py

The command intentionally refuses to change a dirty checkout or a non-main
branch. It also runs outside ``.venv`` so a live or damaged environment can be
detected and replaced safely. Student work should be committed on its own branch
before refreshing.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from scripts.course_runtime import (
        project_environment,
        project_python,
        python_request,
        remove_project_environment,
        require_no_active_course_kernels,
        runtime_contract,
        runtime_matches,
    )
except ModuleNotFoundError:  # Direct execution: python scripts/refresh_course.py
    from course_runtime import (  # type: ignore[no-redef]
        project_environment,
        project_python,
        python_request,
        remove_project_environment,
        require_no_active_course_kernels,
        runtime_contract,
        runtime_matches,
    )


def run(command: list[str], project_root: Path, *, capture: bool = False) -> str:
    """Run one checked command and optionally return stripped standard output."""

    completed = subprocess.run(
        command,
        cwd=project_root,
        check=True,
        capture_output=capture,
        text=True,
    )
    return completed.stdout.strip() if capture else ""


def main() -> None:
    """Update a clean main branch, sync its lockfile, and repair the kernel."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repair",
        action="store_true",
        help="discard and recreate .venv even when its fingerprint matches",
    )
    arguments = parser.parse_args()
    project_root = Path(__file__).resolve().parents[1]
    environment = project_environment(project_root)
    try:
        running_inside_environment = Path(sys.prefix).resolve() == environment.resolve()
    except OSError:
        running_inside_environment = False
    if running_inside_environment:
        raise RuntimeError(
            "The refresh must run outside .venv so it can repair that environment "
            "safely. Use: uv run --isolated --no-project --python 3.12.13 python "
            "scripts/refresh_course.py"
        )

    branch = run(
        ["git", "branch", "--show-current"], project_root, capture=True
    )
    if branch != "main":
        raise RuntimeError(
            f"Refresh is intentionally limited to main; current branch is {branch!r}. "
            "Commit student work on its branch, then switch to main."
        )

    changes = run(
        ["git", "status", "--porcelain"], project_root, capture=True
    )
    if changes:
        raise RuntimeError(
            "The checkout has uncommitted changes. Commit them on a branch or "
            "restore them before refreshing main."
        )

    print("1/4 Checking that VS Code released the course environment ...")
    require_no_active_course_kernels(project_root)

    remotes = set(
        run(["git", "remote"], project_root, capture=True).splitlines()
    )
    remote = "upstream" if "upstream" in remotes else "origin"
    if remote not in remotes:
        raise RuntimeError("No 'origin' or 'upstream' Git remote is configured.")

    print(f"2/4 Fast-forwarding main from {remote}/main ...")
    run(["git", "fetch", remote, "main"], project_root)
    run(["git", "merge", "--ff-only", f"{remote}/main"], project_root)

    uv_executable = shutil.which("uv")
    if uv_executable is None:
        raise RuntimeError("uv is not installed or is not available on PATH.")

    contract = runtime_contract(project_root, uv_executable)
    rebuild = arguments.repair or not runtime_matches(project_root, contract)
    if rebuild:
        reason = "repair requested" if arguments.repair else "runtime contract changed"
        print(f"3/4 Rebuilding the disposable environment ({reason}) ...")
        remove_project_environment(project_root)
    else:
        print("3/4 Synchronizing the verified environment ...")
    run(
        [
            uv_executable,
            "sync",
            "--locked",
            "--python",
            python_request(project_root),
            "--managed-python",
        ],
        project_root,
    )

    print("4/4 Registering, launching, and warming the Rice DSM kernel ...")
    run(
        [
            str(project_python(project_root)),
            str(project_root / "scripts" / "setup_course.py"),
        ],
        project_root,
    )
    print("Lecture-ready: open the repository in VS Code and select 'Rice DSM'.")


if __name__ == "__main__":
    main()
