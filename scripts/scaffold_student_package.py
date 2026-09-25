"""Create a minimal, passing student-contribution package.

The generated smoke-test interface proves that package discovery, imports, and
test collection work before a student begins the domain implementation. Replace
that interface only when the first real behavior and its tests are added.
"""

from __future__ import annotations

import argparse
import keyword
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SLUG_PATTERN = re.compile(r"[a-z][a-z0-9_]{2,39}")
WINDOWS_RESERVED_NAMES = {
    "aux",
    "con",
    "nul",
    "prn",
    *(f"com{number}" for number in range(1, 10)),
    *(f"lpt{number}" for number in range(1, 10)),
}


def validate_slug(slug: str) -> str:
    """Validate and return a Python import name for one contribution.

    Parameters
    ----------
    slug
        Proposed subpackage name.

    Returns
    -------
    str
        The unchanged, validated slug.

    Raises
    ------
    ValueError
        If the slug is not a lowercase Python-style name between 3 and 40
        characters.
    """

    if SLUG_PATTERN.fullmatch(slug) is None:
        raise ValueError(
            "project slug must be 3-40 characters, begin with a lowercase "
            "letter, and contain only lowercase letters, digits, or underscores"
        )
    if keyword.iskeyword(slug):
        raise ValueError(f"project slug must not be the Python keyword {slug!r}")
    if slug.casefold() in WINDOWS_RESERVED_NAMES:
        raise ValueError(f"project slug {slug!r} is a reserved filename on Windows")
    return slug


def scaffold_contribution(
    slug: str, *, project_root: Path = PROJECT_ROOT
) -> tuple[Path, ...]:
    """Create source, documentation, and test files for a contribution.

    Parameters
    ----------
    slug
        Unique import name for the contribution.
    project_root
        Repository root. Tests override this with a temporary directory.

    Returns
    -------
    tuple[pathlib.Path, ...]
        Paths created by the operation.

    Raises
    ------
    ValueError
        If ``slug`` is invalid.
    FileExistsError
        If either the source or test destination already exists. No files are
        written in that case.
    """

    validated_slug = validate_slug(slug)
    source_directory = project_root / "src" / "rice_dsm" / "contrib" / validated_slug
    test_directory = project_root / "tests" / "contrib" / validated_slug

    collisions = [path for path in (source_directory, test_directory) if path.exists()]
    if collisions:
        joined = ", ".join(str(path) for path in collisions)
        raise FileExistsError(f"refusing to overwrite existing path(s): {joined}")

    source_directory.mkdir(parents=True)
    test_directory.mkdir(parents=True)

    files = {
        source_directory / "__init__.py": _init_template(validated_slug),
        source_directory / "core.py": _core_template(validated_slug),
        source_directory / "README.md": _readme_template(validated_slug),
        test_directory / "test_core.py": _test_template(validated_slug),
    }
    for path, content in files.items():
        path.write_text(content, encoding="utf-8", newline="\n")

    return tuple(files)


def _init_template(slug: str) -> str:
    return f'''"""Public interface for the ``{slug}`` course contribution."""

from rice_dsm.contrib.{slug}.core import contribution_name

__all__ = ["contribution_name"]
'''


def _core_template(slug: str) -> str:
    return f'''"""Core behavior for the ``{slug}`` course contribution."""


def contribution_name() -> str:
    """Return the contribution's stable import name.

    Returns
    -------
    str
        The package slug used in imports.

    Notes
    -----
    This is a smoke-test seam for the onboarding pull request. Replace it only
    alongside the first real domain behavior and tests.
    """

    return "{slug}"
'''


def _test_template(slug: str) -> str:
    return f'''"""Tests for the ``{slug}`` course contribution."""

from rice_dsm.contrib.{slug} import contribution_name


def test_contribution_is_importable_by_its_stable_name() -> None:
    assert contribution_name() == "{slug}"
'''


def _readme_template(slug: str) -> str:
    return f"""# `{slug}`

## Problem and users

State the scientific, mathematical, or engineering problem and who needs the
result. Link the approved issue.

## Public interface

Describe the functions, classes, inputs, outputs, units, and exceptions that
callers may rely on. Include one minimal executable example.

## Assumptions and invariants

Record mathematical assumptions, valid ranges, shapes, units, randomness, and
determinism guarantees.

## Data and model provenance

Identify every dataset, model, license, transformation, and train/evaluation
boundary. Write `Not applicable` when the contribution uses none.

## Verification

Explain the normal cases, boundaries, failure modes, and domain properties
covered by tests. Give the focused test command.

## Limitations and responsible use

State what the contribution does not establish, populations or regimes where
it may fail, and any privacy, safety, fairness, or computational constraints.

## Maintainers

Git history and the pull request preserve authorship. Listing a GitHub handle
here is optional; do not include a student ID, grade, or private information.
"""


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(
        description="Create a tested subpackage under rice_dsm.contrib."
    )
    parser.add_argument(
        "slug",
        help="unique lowercase import name, for example graph_statistics",
    )
    return parser


def main() -> int:
    """Run the contribution scaffolder from the command line."""

    arguments = build_parser().parse_args()
    try:
        created = scaffold_contribution(arguments.slug)
    except (ValueError, FileExistsError) as error:
        raise SystemExit(f"error: {error}") from error

    print("Created a passing contribution scaffold:")
    for path in created:
        print(f"  {path.relative_to(PROJECT_ROOT)}")
    print("\nNext: read the generated README and run the focused test.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
