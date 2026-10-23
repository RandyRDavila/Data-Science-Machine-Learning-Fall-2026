"""Fast-forward main and prepare the complete course environment.

Run from anywhere inside the repository on macOS, Linux, or Windows:

    uv run --locked python scripts/refresh_course.py

The command intentionally refuses to change a dirty checkout or a non-main
branch. Student work should be committed on its own branch before refreshing.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


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

    project_root = Path(__file__).resolve().parents[1]
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

    remotes = set(
        run(["git", "remote"], project_root, capture=True).splitlines()
    )
    remote = "upstream" if "upstream" in remotes else "origin"
    if remote not in remotes:
        raise RuntimeError("No 'origin' or 'upstream' Git remote is configured.")

    print(f"1/3 Fast-forwarding main from {remote}/main ...")
    run(["git", "fetch", remote, "main"], project_root)
    run(["git", "merge", "--ff-only", f"{remote}/main"], project_root)

    uv_executable = shutil.which("uv")
    if uv_executable is None:
        raise RuntimeError("uv is not installed or is not available on PATH.")

    print("2/3 Synchronizing the exact locked environment ...")
    run([uv_executable, "sync", "--locked"], project_root)

    print("3/3 Verifying data/package paths and repairing the Rice DSM kernel ...")
    run(
        [sys.executable, str(project_root / "scripts" / "setup_course.py")],
        project_root,
    )
    print("Lecture-ready: open the repository in VS Code and select 'Rice DSM'.")


if __name__ == "__main__":
    main()
