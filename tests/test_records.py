"""Executable examples for the package-backed records revisited in Lecture 3.

Each test states one behavior. Read a test as:

    arrange the example -> act on the code -> assert the expected result
"""

from dataclasses import FrozenInstanceError

import pytest

from rice_dsm import StudentRecord, summarize_scores


def test_student_record_normalizes_name() -> None:
    """Repeated whitespace and capitalization are normalized at construction."""

    # Arrange and act: construct an object from intentionally messy input.
    record = StudentRecord("  grace   hopper ", 98)

    # Assert: compare the observable result with the contract.
    assert record.name == "Grace Hopper"


def test_student_record_preserves_score() -> None:
    record = StudentRecord("Ada Lovelace", 92.5)

    assert record.score == 92.5


@pytest.mark.parametrize("score", [0, 50.5, 100])
def test_student_record_accepts_scores_on_closed_interval(score: float) -> None:
    record = StudentRecord("Katherine Johnson", score)

    assert record.score == score


@pytest.mark.parametrize("score", [-1, 101])
def test_student_record_rejects_score_outside_range(score: float) -> None:
    """One test definition checks several examples through parametrization."""

    with pytest.raises(ValueError, match="between 0 and 100"):
        StudentRecord("Ada Lovelace", score)


def test_student_record_rejects_blank_name() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        StudentRecord("   ", 80)


def test_student_record_is_immutable() -> None:
    record = StudentRecord("Alan Turing", 95)

    with pytest.raises(FrozenInstanceError):
        record.score = 100  # type: ignore[misc]


def test_summarize_scores_returns_descriptive_statistics() -> None:
    records = [StudentRecord("Ada", 90), StudentRecord("Alan", 80)]

    assert summarize_scores(records) == {
        "count": 2,
        "mean": 85.0,
        "minimum": 80,
        "maximum": 90,
    }


def test_summarize_scores_accepts_one_pass_iterables() -> None:
    """The Iterable annotation promises more than list inputs alone."""

    examples = [("Ada", 70), ("Alan", 90)]
    records = (StudentRecord(name, score) for name, score in examples)

    assert summarize_scores(records)["mean"] == 80


def test_summarize_scores_requires_a_record() -> None:
    with pytest.raises(ValueError, match="at least one"):
        summarize_scores([])
