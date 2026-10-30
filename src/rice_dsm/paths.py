"""Resolve repository resources independently of a process's working directory."""

from __future__ import annotations

import tomllib
from pathlib import Path

PROJECT_NAME = "rice-dsm"
COURSE_DATABASE = Path("data/course_datasets.sqlite")
MNIST_TEACHING_SAMPLE = Path("data/mnist_teaching_sample.npz")
MOVIELENS_TEACHING_DIRECTORY = Path("data/lecture_13_movielens")


def _is_project_root(candidate: Path) -> bool:
    """Return whether *candidate* is the root of this course repository."""

    project_file = candidate / "pyproject.toml"
    if not project_file.is_file():
        return False
    try:
        with project_file.open("rb") as stream:
            configuration = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError):
        return False
    return configuration.get("project", {}).get("name") == PROJECT_NAME


def find_project_root(start: Path | str | None = None) -> Path:
    """Find the course repository without assuming a working directory.

    Parameters
    ----------
    start
        Directory from which to search upward. When omitted, search from the
        process working directory and then from this installed module. The
        module fallback supports VS Code kernels launched outside the repository
        root when the course package is installed in editable mode.

    Returns
    -------
    pathlib.Path
        Absolute path to the course repository root.

    Raises
    ------
    FileNotFoundError
        If no parent directory contains this course's ``pyproject.toml``.
    """

    origins = [Path.cwd() if start is None else Path(start)]
    if start is None:
        origins.append(Path(__file__))

    searched: list[Path] = []
    for origin in origins:
        resolved = origin.resolve()
        directory = resolved if resolved.is_dir() else resolved.parent
        for candidate in (directory, *directory.parents):
            if candidate in searched:
                continue
            searched.append(candidate)
            if _is_project_root(candidate):
                return candidate

    locations = ", ".join(str(path) for path in searched)
    raise FileNotFoundError(
        f"Could not locate the {PROJECT_NAME!r} repository. Searched: {locations}"
    )


def course_database_path(start: Path | str | None = None) -> Path:
    """Return the absolute path to the versioned course database.

    The database is intentionally resolved from the repository root rather than
    from ``Path.cwd()``. Notebook kernels, test runners, terminals, and deployed
    programs are all free to use different working directories.
    """

    database_path = find_project_root(start) / COURSE_DATABASE
    if not database_path.is_file():
        raise FileNotFoundError(
            f"Missing course database: {database_path}. Restore the tracked file "
            "with Git or rebuild it from the repository root with "
            "`uv run python scripts/build_course_database.py`."
        )
    return database_path


def mnist_teaching_sample_path(start: Path | str | None = None) -> Path:
    """Return the absolute path to the bounded, versioned MNIST sample.

    Resolving this artifact through the repository root keeps Lecture 12
    independent of the directory from which VS Code starts a notebook kernel.
    """

    sample_path = find_project_root(start) / MNIST_TEACHING_SAMPLE
    if not sample_path.is_file():
        raise FileNotFoundError(
            f"Missing MNIST teaching sample: {sample_path}. Restore the tracked "
            "file with Git or rebuild it from an upstream mnist.npz with "
            "`uv run python scripts/build_mnist_teaching_sample.py /path/to/mnist.npz`."
        )
    return sample_path


def movielens_teaching_directory(start: Path | str | None = None) -> Path:
    """Return the directory containing the bounded MovieLens teaching subset."""

    data_directory = find_project_root(start) / MOVIELENS_TEACHING_DIRECTORY
    required_files = (data_directory / "ratings.csv", data_directory / "movies.csv")
    if not all(path.is_file() for path in required_files):
        raise FileNotFoundError(
            f"Missing MovieLens teaching data in {data_directory}. Restore the "
            "tracked files with Git or rebuild them from the official archive with "
            "`uv run python scripts/build_movielens_teaching_sample.py "
            "/path/to/ml-latest-small.zip`."
        )
    return data_directory
