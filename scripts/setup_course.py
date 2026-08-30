"""Prepare the local Python environment for course notebooks.

Run this script through the project environment after ``uv sync``:

    uv run python scripts/setup_course.py
"""

from __future__ import annotations

import os
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


def install_course_kernel() -> None:
    """Install a named kernelspec inside the current virtual environment."""

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
    install_course_kernel()
    print(
        "Course setup complete. Open a notebook in VS Code and select the "
        f"{KERNEL_DISPLAY_NAME!r} kernel."
    )


if __name__ == "__main__":
    main()
