"""Exercise a base-to-head update in one persistent CI checkout.

The script itself runs in uv's isolated cache environment, not in repository
``.venv``.  It may therefore replace the project environment between Git
revisions exactly as the student refresh bootstrap does.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

try:
    from scripts.course_runtime import project_python, remove_project_environment
except ModuleNotFoundError:
    from course_runtime import (  # type: ignore[no-redef]
        project_python,
        remove_project_environment,
    )


def run(command: list[str], root: Path) -> None:
    """Run one visible, checked upgrade step."""

    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=root, check=True)


def main() -> None:
    """Build the base environment, then replace and verify it at PR head."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    arguments = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("uv is required for the runtime-upgrade check.")

    run(["git", "checkout", "--detach", arguments.base], root)
    run([uv, "sync", "--locked"], root)
    base_setup = root / "scripts" / "setup_course.py"
    run([str(project_python(root)), str(base_setup)], root)

    run(["git", "checkout", "--detach", arguments.head], root)
    # A changed contract is replaced, never mutated under a process created by
    # the old revision. The base setup exits before this removal begins.
    remove_project_environment(root)
    run(
        [
            uv,
            "sync",
            "--locked",
            "--python",
            (root / ".python-version").read_text().strip(),
            "--managed-python",
        ],
        root,
    )
    run([str(project_python(root)), str(root / "scripts" / "setup_course.py")], root)


if __name__ == "__main__":
    main()
