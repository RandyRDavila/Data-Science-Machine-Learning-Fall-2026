"""Tests for the student-contribution boundary and scaffolding tool."""

from pathlib import Path

import pytest

from scripts.scaffold_student_package import scaffold_contribution, validate_slug

PROJECT_ROOT = Path(__file__).parents[1]
CONTRIBUTION_ROOT = PROJECT_ROOT / "src" / "rice_dsm" / "contrib"
CONTRIBUTION_TEST_ROOT = PROJECT_ROOT / "tests" / "contrib"


@pytest.mark.parametrize(
    "slug",
    ["graph_statistics", "ode2", "chemical_features"],
)
def test_valid_contribution_slugs_are_stable_import_names(slug: str) -> None:
    assert validate_slug(slug) == slug


@pytest.mark.parametrize(
    "slug",
    [
        "ab",
        "Uppercase",
        "2fast",
        "contains-hyphen",
        "contains space",
        "a" * 41,
    ],
)
def test_invalid_contribution_slugs_explain_the_contract(slug: str) -> None:
    with pytest.raises(ValueError, match="3-40 characters"):
        validate_slug(slug)


@pytest.mark.parametrize("slug", ["class", "lambda", "return"])
def test_python_keywords_cannot_be_package_slugs(slug: str) -> None:
    with pytest.raises(ValueError, match="Python keyword"):
        validate_slug(slug)


@pytest.mark.parametrize("slug", ["con", "nul", "com1", "lpt9"])
def test_windows_reserved_names_cannot_be_package_slugs(slug: str) -> None:
    with pytest.raises(ValueError, match="reserved filename on Windows"):
        validate_slug(slug)


def test_scaffold_creates_importable_source_documentation_and_tests(
    tmp_path: Path,
) -> None:
    created = scaffold_contribution("graph_statistics", project_root=tmp_path)

    expected = {
        tmp_path / "src/rice_dsm/contrib/graph_statistics/__init__.py",
        tmp_path / "src/rice_dsm/contrib/graph_statistics/core.py",
        tmp_path / "src/rice_dsm/contrib/graph_statistics/README.md",
        tmp_path / "tests/contrib/graph_statistics/test_core.py",
    }
    assert set(created) == expected

    for path in created:
        assert path.is_file()
        assert "graph_statistics" in path.read_text(encoding="utf-8")
        if path.suffix == ".py":
            compile(path.read_text(encoding="utf-8"), str(path), "exec")


def test_scaffold_refuses_partial_or_complete_overwrites(tmp_path: Path) -> None:
    existing = tmp_path / "tests/contrib/graph_statistics"
    existing.mkdir(parents=True)

    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        scaffold_contribution("graph_statistics", project_root=tmp_path)

    assert not (tmp_path / "src/rice_dsm/contrib/graph_statistics").exists()


def test_every_contribution_has_documentation_and_a_test_directory() -> None:
    assert (CONTRIBUTION_ROOT / "__init__.py").is_file()
    assert (CONTRIBUTION_ROOT / "README.md").is_file()
    assert (CONTRIBUTION_TEST_ROOT / "README.md").is_file()

    package_directories = sorted(
        path
        for path in CONTRIBUTION_ROOT.iterdir()
        if path.is_dir() and not path.name.startswith("_")
    )
    for package_directory in package_directories:
        assert validate_slug(package_directory.name) == package_directory.name
        assert (package_directory / "__init__.py").is_file()
        assert (package_directory / "README.md").is_file()

        test_directory = CONTRIBUTION_TEST_ROOT / package_directory.name
        assert test_directory.is_dir()
        assert any(test_directory.glob("test_*.py"))
