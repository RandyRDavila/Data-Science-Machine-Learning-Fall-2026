"""Diagnose the versioned course environment without modifying it."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

try:
    from scripts.course_runtime import (
        active_course_kernels,
        project_python,
        read_runtime_stamp,
        runtime_contract,
    )
except ModuleNotFoundError:  # Direct execution: python scripts/course_doctor.py
    from course_runtime import (  # type: ignore[no-redef]
        active_course_kernels,
        project_python,
        read_runtime_stamp,
        runtime_contract,
    )


def main() -> None:
    """Print runtime identity, stale kernels, and an executable health check."""

    project_root = Path(__file__).resolve().parents[1]
    uv_executable = shutil.which("uv")
    if uv_executable is None:
        raise RuntimeError("uv is not installed or is not available on PATH.")

    desired = runtime_contract(project_root, uv_executable)
    installed = read_runtime_stamp(project_root)
    print("Course runtime doctor")
    print("Repository:", project_root)
    print("Desired Python:", desired["python"])
    print("uv:", desired["uv"])
    print("Runtime fingerprint:", desired["fingerprint"][:12])
    print(
        "Verified fingerprint:",
        installed.get("fingerprint", "missing")[:12] if installed else "missing",
    )

    kernels = active_course_kernels(project_root)
    if kernels:
        print("Active Rice DSM kernels:")
        for item in kernels:
            print(f"  PID {item['pid']} (age {item['age']})")
    else:
        print("Active Rice DSM kernels: none")

    python = project_python(project_root)
    if not python.is_file():
        raise RuntimeError(".venv is missing. Run the documented refresh command.")
    completed = subprocess.run(
        [str(python), str(project_root / "scripts" / "setup_course.py"), "--check"],
        cwd=project_root,
        check=False,
        timeout=240,
    )
    if completed.returncode:
        raise RuntimeError(
            "The course runtime is unhealthy. Fully quit VS Code and run the "
            "documented refresh command with --repair."
        )
    print("Doctor result: healthy")


if __name__ == "__main__":
    main()
