"""Regression tests for working-directory-independent course resources."""

import sqlite3
from pathlib import Path

import pytest

from rice_dsm.paths import (
    course_database_path,
    find_project_root,
    mnist_teaching_sample_path,
)

PROJECT_ROOT = Path(__file__).parents[1].resolve()


def test_find_project_root_from_nested_directory() -> None:
    nested_directory = (
        PROJECT_ROOT / "notebooks" / "lecture-09-supervised-learning-systems"
    )

    assert find_project_root(nested_directory) == PROJECT_ROOT


def test_course_database_path_does_not_depend_on_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    database_path = course_database_path()

    assert database_path == PROJECT_ROOT / "data" / "course_datasets.sqlite"
    with sqlite3.connect(f"{database_path.as_uri()}?mode=ro", uri=True) as connection:
        dataset_count = connection.execute(
            "SELECT COUNT(*) FROM dataset_catalog"
        ).fetchone()[0]
    assert dataset_count == 4


def test_missing_database_error_names_absolute_path_and_recovery_command(
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "course-copy"
    nested_directory = project_root / "notebooks" / "lecture"
    nested_directory.mkdir(parents=True)
    (project_root / "pyproject.toml").write_text(
        '[project]\nname = "rice-dsm"\n', encoding="utf-8"
    )

    with pytest.raises(FileNotFoundError) as error:
        course_database_path(nested_directory)

    expected_path = project_root / "data" / "course_datasets.sqlite"
    assert str(expected_path) in str(error.value)
    assert "uv run python scripts/build_course_database.py" in str(error.value)


def test_mnist_sample_path_does_not_depend_on_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    sample_path = mnist_teaching_sample_path()

    assert sample_path == PROJECT_ROOT / "data" / "mnist_teaching_sample.npz"


def test_missing_mnist_sample_error_explains_recovery(tmp_path: Path) -> None:
    project_root = tmp_path / "course-copy"
    nested_directory = project_root / "notebooks" / "lecture"
    nested_directory.mkdir(parents=True)
    (project_root / "pyproject.toml").write_text(
        '[project]\nname = "rice-dsm"\n', encoding="utf-8"
    )

    with pytest.raises(FileNotFoundError) as error:
        mnist_teaching_sample_path(nested_directory)

    assert str(project_root / "data" / "mnist_teaching_sample.npz") in str(error.value)
    assert "scripts/build_mnist_teaching_sample.py" in str(error.value)
