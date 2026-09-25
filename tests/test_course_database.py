"""Contracts for the versioned real-data teaching database."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from scripts.build_course_database import build_database

PROJECT_ROOT = Path(__file__).parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "course_datasets.sqlite"


def table_names(connection: sqlite3.Connection) -> set[str]:
    """Return user-defined SQLite table names."""

    return {
        row[0]
        for row in connection.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
            """
        )
    }


def test_committed_database_has_catalog_and_real_observation_tables() -> None:
    assert DATABASE_PATH.is_file()
    with sqlite3.connect(f"file:{DATABASE_PATH}?mode=ro", uri=True) as connection:
        assert table_names(connection) == {
            "dataset_catalog",
            "dataset_columns",
            "diabetes_observations",
            "breast_cancer_observations",
            "wine_observations",
            "digits_observations",
        }
        counts = dict(
            connection.execute(
                "SELECT dataset_id, row_count FROM dataset_catalog ORDER BY dataset_id"
            )
        )
        assert counts == {
            "breast_cancer_wisconsin": 569,
            "diabetes": 442,
            "optical_digits": 1797,
            "wine_recognition": 178,
        }


def test_catalog_records_provenance_and_column_roles() -> None:
    with sqlite3.connect(f"file:{DATABASE_PATH}?mode=ro", uri=True) as connection:
        catalog_rows = connection.execute(
            """
            SELECT source_url, observational_unit, target_column, license_note
            FROM dataset_catalog
            """
        ).fetchall()
        assert len(catalog_rows) == 4
        assert all(
            row[0].startswith("https://scikit-learn.org/") for row in catalog_rows
        )
        assert all(all(value for value in row) for row in catalog_rows)
        roles = {
            row[0]
            for row in connection.execute("SELECT DISTINCT role FROM dataset_columns")
        }
        assert roles == {"identifier", "feature", "target", "target_label"}


def test_database_builder_reproduces_schema_and_counts(tmp_path: Path) -> None:
    rebuilt_path = tmp_path / "rebuilt.sqlite"
    build_database(rebuilt_path)

    with sqlite3.connect(DATABASE_PATH) as committed, sqlite3.connect(
        rebuilt_path
    ) as rebuilt:
        assert table_names(committed) == table_names(rebuilt)
        committed_catalog = committed.execute(
            "SELECT * FROM dataset_catalog ORDER BY dataset_id"
        ).fetchall()
        rebuilt_catalog = rebuilt.execute(
            "SELECT * FROM dataset_catalog ORDER BY dataset_id"
        ).fetchall()
        assert rebuilt_catalog == committed_catalog


def test_database_is_readable_in_sqlite_read_only_mode() -> None:
    with sqlite3.connect(f"file:{DATABASE_PATH}?mode=ro", uri=True) as connection:
        bmi_rows = connection.execute(
            """
            SELECT observation_id, bmi, disease_progression
            FROM diabetes_observations
            WHERE bmi IS NOT NULL
            ORDER BY observation_id
            LIMIT 5
            """
        ).fetchall()
    assert len(bmi_rows) == 5
    assert bmi_rows[0][0] == 1
