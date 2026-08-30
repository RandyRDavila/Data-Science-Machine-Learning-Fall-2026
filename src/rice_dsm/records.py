"""Small record-processing examples introduced during Lecture 1."""

from collections.abc import Iterable
from dataclasses import dataclass
from statistics import fmean


@dataclass(frozen=True, slots=True)
class StudentRecord:
    """A validated score associated with a student name."""

    name: str
    score: float

    def __post_init__(self) -> None:
        cleaned_name = " ".join(self.name.split())
        if not cleaned_name:
            raise ValueError("name must not be empty")
        if not 0 <= self.score <= 100:
            raise ValueError("score must be between 0 and 100")
        object.__setattr__(self, "name", cleaned_name.title())


def summarize_scores(records: Iterable[StudentRecord]) -> dict[str, float | int]:
    """Return the count, mean, minimum, and maximum for a collection of records."""

    scores = [record.score for record in records]
    if not scores:
        raise ValueError("at least one record is required")
    return {
        "count": len(scores),
        "mean": fmean(scores),
        "minimum": min(scores),
        "maximum": max(scores),
    }
