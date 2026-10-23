"""Prepare the local Python environment for course notebooks.

Run this script through the project environment after ``uv sync``:

    uv run python scripts/setup_course.py
"""

from __future__ import annotations

import json
import os
import sqlite3
import stat
import subprocess
import sys
import sysconfig
from pathlib import Path

KERNEL_NAME = "rice-dsm"
KERNEL_DISPLAY_NAME = "Rice DSM"
SITE_CUSTOMIZE_FILE = "sitecustomize.py"
CUSTOMIZATION_BEGIN = "# BEGIN rice-dsm course source"
CUSTOMIZATION_END = "# END rice-dsm course source"
COURSE_DATABASE = "data/course_datasets.sqlite"


def write_course_sitecustomize(
    project_root: Path | None = None,
    site_packages: Path | None = None,
) -> Path:
    """Register project source without relying on editable-install path files.

    Some macOS copies of Python ignore a packaging backend's editable-install
    ``.pth`` file when a package cache gives it the Finder hidden flag. Python
    imports ``sitecustomize`` directly at startup, so this project-owned hook is
    independent of that file-discovery edge case.
    """

    if project_root is None:
        project_root = Path(__file__).resolve().parents[1]
    source_directory = project_root / "src"
    if not source_directory.is_dir():
        raise RuntimeError(f"Expected source directory: {source_directory}")

    if site_packages is None:
        site_packages = Path(sysconfig.get_path("purelib"))
    site_packages.mkdir(parents=True, exist_ok=True)
    customization_file = site_packages / SITE_CUSTOMIZE_FILE
    existing = customization_file.read_text() if customization_file.exists() else ""

    if CUSTOMIZATION_BEGIN in existing:
        before, marked = existing.split(CUSTOMIZATION_BEGIN, maxsplit=1)
        if CUSTOMIZATION_END not in marked:
            raise RuntimeError(f"Malformed course block in {customization_file}")
        _, after = marked.split(CUSTOMIZATION_END, maxsplit=1)
        existing = f"{before.rstrip()}\n{after.lstrip()}".strip()

    block = os.linesep.join(
        [
            CUSTOMIZATION_BEGIN,
            "import sys as _rice_dsm_sys",
            f"_rice_dsm_source = {str(source_directory)!r}",
            "if _rice_dsm_source not in _rice_dsm_sys.path:",
            "    _rice_dsm_sys.path.insert(0, _rice_dsm_source)",
            "del _rice_dsm_source, _rice_dsm_sys",
            CUSTOMIZATION_END,
        ]
    )
    content = f"{existing}{os.linesep * 2}{block}" if existing else block
    customization_file.write_text(f"{content}{os.linesep}")
    return customization_file


def reveal_path_files_on_macos() -> list[Path]:
    """Clear the macOS hidden flag from .pth files used during Python startup."""

    if sys.platform != "darwin" or not hasattr(os, "chflags"):
        return []

    hidden_flag = getattr(stat, "UF_HIDDEN", 0)
    if not hidden_flag:
        return []

    site_packages = Path(sysconfig.get_path("purelib"))
    revealed: list[Path] = []
    for path_file in site_packages.glob("*.pth"):
        flags = path_file.stat().st_flags
        if flags & hidden_flag:
            os.chflags(path_file, flags & ~hidden_flag)
            revealed.append(path_file)
    return revealed


def verify_course_package() -> None:
    """Verify the editable package in a fresh Python process."""

    command = [
        sys.executable,
        "-c",
        "import rice_dsm; print(rice_dsm.__file__)",
    ]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    print("Verified rice_dsm:", completed.stdout.strip())


def verify_course_database(project_root: Path | None = None) -> Path:
    """Verify that the versioned teaching database is present and readable."""

    if project_root is None:
        project_root = Path(__file__).resolve().parents[1]
    database_path = project_root / COURSE_DATABASE
    if not database_path.is_file():
        raise RuntimeError(
            f"Missing course database: {database_path}. Restore it with Git or run "
            "`uv run python scripts/build_course_database.py`."
        )
    with sqlite3.connect(f"file:{database_path}?mode=ro", uri=True) as connection:
        dataset_count = connection.execute(
            "SELECT COUNT(*) FROM dataset_catalog"
        ).fetchone()[0]
    if dataset_count != 4:
        raise RuntimeError(
            f"Expected 4 cataloged datasets in {database_path}; found {dataset_count}."
        )
    print(f"Verified course database: {database_path} ({dataset_count} datasets)")
    return database_path


def install_course_kernel(project_root: Path | None = None) -> Path:
    """Install a named kernelspec with an explicit course-source contract.

    The editable installation and ``sitecustomize`` remain the ordinary import
    mechanisms. The kernelspec environment is a final, visible safeguard for
    VS Code and Jupyter clients that retain a stale working directory or ignore
    an editable-install path file.
    """

    if project_root is None:
        project_root = Path(__file__).resolve().parents[1]

    command = [
        sys.executable,
        "-m",
        "ipykernel",
        "install",
        "--prefix",
        sys.prefix,
        "--name",
        KERNEL_NAME,
        "--display-name",
        KERNEL_DISPLAY_NAME,
    ]
    subprocess.run(command, check=True)
    kernel_file = (
        Path(sys.prefix) / "share" / "jupyter" / "kernels" / KERNEL_NAME / "kernel.json"
    )
    if not kernel_file.is_file():
        raise RuntimeError(f"Kernel installation did not create {kernel_file}")

    kernel = json.loads(kernel_file.read_text())
    # Preserve the .venv path rather than resolving its interpreter symlink.
    # Executing the resolved uv-managed base interpreter can lose pyvenv.cfg
    # discovery and therefore the environment's installed dependencies.
    kernel["argv"][0] = sys.executable
    kernel["env"] = {
        **kernel.get("env", {}),
        "PYTHONPATH": str((project_root / "src").resolve()),
        "RICE_DSM_PROJECT_ROOT": str(project_root.resolve()),
    }
    kernel_file.write_text(f"{json.dumps(kernel, indent=2)}\n")
    return kernel_file


def main() -> None:
    """Prepare startup paths, verify the import, and register the course kernel."""

    if sys.prefix == sys.base_prefix:
        raise RuntimeError(
            "This script must run inside the project environment. Use "
            "`uv run python scripts/setup_course.py`."
        )

    customization_file = write_course_sitecustomize()
    print("Registered course source path:", customization_file)

    revealed = reveal_path_files_on_macos()
    for path_file in revealed:
        print("Enabled Python startup path:", path_file)

    verify_course_package()
    verify_course_database()
    kernel_file = install_course_kernel()
    print("Registered notebook kernel:", kernel_file)
    print("Kernel Python executable:", sys.executable)
    print(
        "Course setup complete. Open a notebook in VS Code and select the "
        f"{KERNEL_DISPLAY_NAME!r} kernel."
    )


if __name__ == "__main__":
    main()
