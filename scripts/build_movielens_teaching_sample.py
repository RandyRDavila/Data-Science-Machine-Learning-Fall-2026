"""Build the deterministic Lecture 13 MovieLens teaching subset.

Usage
-----
uv run python scripts/build_movielens_teaching_sample.py /path/to/ml-latest-small.zip
"""

from __future__ import annotations

import argparse
import csv
import io
import zipfile
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]
OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "lecture_13_movielens"
N_MOVIES = 80


def rows_from_archive(archive: zipfile.ZipFile, filename: str) -> list[dict[str, str]]:
    """Read one UTF-8 CSV member from the official MovieLens archive."""

    member = f"ml-latest-small/{filename}"
    with archive.open(member) as raw_stream:
        text_stream = io.TextIOWrapper(raw_stream, encoding="utf-8", newline="")
        return list(csv.DictReader(text_stream))


def write_rows(
    path: Path, rows: list[dict[str, str]], fieldnames: tuple[str, ...]
) -> None:
    """Write selected rows with stable columns and Unix newlines."""

    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build(archive_path: Path) -> None:
    """Select the 80 most-rated movies, retaining every rating on them."""

    with zipfile.ZipFile(archive_path) as archive:
        ratings = rows_from_archive(archive, "ratings.csv")
        movies = rows_from_archive(archive, "movies.csv")

    counts = Counter(row["movieId"] for row in ratings)
    selected_movie_ids = {
        movie_id
        for movie_id, _ in sorted(
            counts.items(), key=lambda pair: (-pair[1], int(pair[0]))
        )[:N_MOVIES]
    }
    selected_ratings = [
        row for row in ratings if row["movieId"] in selected_movie_ids
    ]
    selected_movies = [row for row in movies if row["movieId"] in selected_movie_ids]
    selected_movies.sort(key=lambda row: int(row["movieId"]))

    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    write_rows(
        OUTPUT_DIRECTORY / "ratings.csv",
        selected_ratings,
        ("userId", "movieId", "rating", "timestamp"),
    )
    write_rows(
        OUTPUT_DIRECTORY / "movies.csv",
        selected_movies,
        ("movieId", "title", "genres"),
    )
    print(
        f"Wrote {len(selected_ratings):,} authentic ratings for "
        f"{len(selected_movies)} movies to {OUTPUT_DIRECTORY.relative_to(PROJECT_ROOT)}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    arguments = parser.parse_args()
    build(arguments.archive)


if __name__ == "__main__":
    main()
