"""Integration checks for the environment students use before class."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import sysconfig
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parents[1]
SOURCE_DIRECTORY = PROJECT_ROOT / "src"
SETUP_SCRIPT = PROJECT_ROOT / "scripts" / "setup_course.py"

module_spec = importlib.util.spec_from_file_location("course_setup", SETUP_SCRIPT)
assert module_spec is not None and module_spec.loader is not None
setup_course = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(setup_course)


def test_course_customization_points_to_project_src(tmp_path: Path) -> None:
    """The compatibility path must work even when the project path has spaces."""

    project_root = tmp_path / "course repository with spaces"
    source_directory = project_root / "src"
    source_directory.mkdir(parents=True)
    site_packages = tmp_path / "environment" / "site-packages"

    customization = setup_course.write_course_sitecustomize(
        project_root, site_packages
    )

    assert customization == site_packages / setup_course.SITE_CUSTOMIZE_FILE
    assert repr(str(source_directory)) in customization.read_text()


def test_course_customization_replaces_stale_path_and_preserves_other_code(
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "current-project"
    (project_root / "src").mkdir(parents=True)
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir()
    customization = site_packages / setup_course.SITE_CUSTOMIZE_FILE
    customization.write_text(
        "KEEP_ME = True\n\n"
        f"{setup_course.CUSTOMIZATION_BEGIN}\n"
        "_rice_dsm_source = '/an/old/checkout/src'\n"
        f"{setup_course.CUSTOMIZATION_END}\n"
    )

    setup_course.write_course_sitecustomize(project_root, site_packages)

    content = customization.read_text()
    assert "KEEP_ME = True" in content
    assert "/an/old/checkout/src" not in content
    assert repr(str(project_root / "src")) in content
    assert content.count(setup_course.CUSTOMIZATION_BEGIN) == 1


def test_course_customization_rejects_a_malformed_existing_block(
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "current-project"
    (project_root / "src").mkdir(parents=True)
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir()
    customization = site_packages / setup_course.SITE_CUSTOMIZE_FILE
    customization.write_text(f"{setup_course.CUSTOMIZATION_BEGIN}\n")

    with pytest.raises(RuntimeError, match="Malformed course block"):
        setup_course.write_course_sitecustomize(project_root, site_packages)


def test_course_customization_requires_a_src_directory(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="Expected source directory"):
        setup_course.write_course_sitecustomize(
            tmp_path / "incomplete-project", tmp_path / "site-packages"
        )


def test_configured_course_customization_is_present() -> None:
    """The durable startup hook must not depend on editable ``.pth`` files."""

    site_packages = Path(sysconfig.get_path("purelib"))
    customization = site_packages / setup_course.SITE_CUSTOMIZE_FILE

    assert customization.is_file()
    assert repr(str(SOURCE_DIRECTORY)) in customization.read_text()


def test_fresh_python_process_imports_course_package_outside_repository(
    tmp_path: Path,
) -> None:
    """Reproduce how a kernel imports without relying on the working directory."""

    completed = subprocess.run(
        [sys.executable, "-c", "import rice_dsm; print(rice_dsm.__file__)"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    imported_path = Path(completed.stdout.strip())
    assert imported_path.is_relative_to(SOURCE_DIRECTORY)


def test_rice_dsm_kernel_uses_project_environment() -> None:
    kernel_file = (
        Path(sys.prefix) / "share" / "jupyter" / "kernels" / "rice-dsm" / "kernel.json"
    )

    assert kernel_file.is_file()
    kernel = json.loads(kernel_file.read_text())
    kernel_executable = Path(kernel["argv"][0])

    assert kernel["display_name"] == "Rice DSM"
    assert kernel_executable.is_relative_to(Path(sys.prefix))
    assert "-m" in kernel["argv"]
    module_flag = kernel["argv"].index("-m")
    assert kernel["argv"][module_flag + 1] == "ipykernel_launcher"
    assert "-f" in kernel["argv"]
    connection_flag = kernel["argv"].index("-f")
    assert kernel["argv"][connection_flag + 1] == "{connection_file}"
