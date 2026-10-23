"""Contracts for the one-command course refresh workflow."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]
REFRESH_SCRIPT = PROJECT_ROOT / "scripts" / "refresh_course.py"


def test_refresh_command_is_cross_platform_and_fail_safe() -> None:
    source = REFRESH_SCRIPT.read_text(encoding="utf-8")

    for required_contract in (
        'branch != "main"',
        '"status", "--porcelain"',
        'remote = "upstream" if "upstream" in remotes else "origin"',
        '"merge", "--ff-only"',
        '"sync", "--locked"',
        '"scripts" / "setup_course.py"',
        "Lecture-ready",
    ):
        assert required_contract in source


def test_primary_guides_publish_the_same_one_command_refresh() -> None:
    command = "uv run --locked python scripts/refresh_course.py"
    guides = (
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "notebooks" / "PART_II_STUDENT_GUIDE.md",
        PROJECT_ROOT / "textbook" / "appendices" / "setup-reference.tex",
    )

    for guide in guides:
        assert command in guide.read_text(encoding="utf-8")
