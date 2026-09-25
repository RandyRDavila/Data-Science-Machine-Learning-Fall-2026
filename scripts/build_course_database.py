"""Build the versioned SQLite database used by the teaching notebooks.

The analysis notebooks query the resulting database; they do not call dataset
loaders directly. This script is the ingestion boundary and is intentionally
small enough for students to inspect.
"""

from __future__ import annotations

import argparse
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import sklearn
from sklearn.datasets import (
    load_breast_cancer,
    load_diabetes,
    load_digits,
    load_wine,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "course_datasets.sqlite"
SCHEMA_VERSION = 1


@dataclass(frozen=True)
class DatasetRecord:
    """One database table and its provenance metadata."""

    dataset_id: str
    table_name: str
    title: str
    domain: str
    task: str
    observational_unit: str
    target_column: str
    target_description: str
    source_url: str
    bundled_loader: str
    source_note: str
    license_note: str
    frame: pd.DataFrame


def snake_case(value: str) -> str:
    """Convert an upstream feature name into a stable SQL identifier."""

    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip()).strip("_").lower()
    if not normalized or normalized[0].isdigit():
        normalized = f"feature_{normalized}"
    return normalized


def with_observation_id(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with a stable, one-based observation identifier."""

    result = frame.reset_index(drop=True).copy()
    result.insert(0, "observation_id", range(1, len(result) + 1))
    return result


def load_records() -> list[DatasetRecord]:
    """Load real datasets from the installed, locked scikit-learn package."""

    diabetes_bunch = load_diabetes(as_frame=True, scaled=False)
    diabetes = diabetes_bunch.data.rename(columns=snake_case)
    diabetes["disease_progression"] = diabetes_bunch.target.to_numpy()

    cancer_bunch = load_breast_cancer(as_frame=True)
    cancer = cancer_bunch.data.rename(columns=snake_case)
    cancer["diagnosis_code"] = cancer_bunch.target.astype(int).to_numpy()
    cancer["diagnosis_label"] = cancer_bunch.target.map(
        dict(enumerate(cancer_bunch.target_names))
    ).to_numpy()

    wine_bunch = load_wine(as_frame=True)
    wine = wine_bunch.data.rename(columns=snake_case)
    wine["cultivar_code"] = wine_bunch.target.astype(int).to_numpy()
    wine["cultivar_label"] = wine_bunch.target.map(
        dict(enumerate(wine_bunch.target_names))
    ).to_numpy()

    digits_bunch = load_digits()
    digits = pd.DataFrame(
        digits_bunch.data,
        columns=[f"pixel_{index}" for index in range(digits_bunch.data.shape[1])],
    )
    digits["digit_label"] = digits_bunch.target.astype(int)

    shared_license_note = (
        "Bundled with scikit-learn; inspect the upstream dataset description and "
        "terms before redistribution or non-instructional use."
    )
    return [
        DatasetRecord(
            "diabetes",
            "diabetes_observations",
            "Diabetes progression",
            "clinical research",
            "regression",
            "one patient",
            "disease_progression",
            "quantitative disease-progression measure one year after baseline",
            "https://scikit-learn.org/stable/datasets/toy_dataset.html#diabetes-dataset",
            "sklearn.datasets.load_diabetes(scaled=False)",
            "Ten baseline variables for 442 patients; some feature meanings are "
            "incompletely documented.",
            shared_license_note,
            with_observation_id(diabetes),
        ),
        DatasetRecord(
            "breast_cancer_wisconsin",
            "breast_cancer_observations",
            "Wisconsin Diagnostic Breast Cancer",
            "medical imaging",
            "classification",
            "one fine-needle aspirate of a breast mass",
            "diagnosis_code",
            "0=malignant and 1=benign in the bundled encoding",
            "https://scikit-learn.org/stable/datasets/toy_dataset.html#breast-cancer-wisconsin-diagnostic-dataset",
            "sklearn.datasets.load_breast_cancer()",
            "Features were computed from digitized images of cell nuclei.",
            shared_license_note,
            with_observation_id(cancer),
        ),
        DatasetRecord(
            "wine_recognition",
            "wine_observations",
            "Wine recognition",
            "analytical chemistry",
            "classification and clustering",
            "one wine sample",
            "cultivar_code",
            "three cultivar classes in the bundled encoding",
            "https://scikit-learn.org/stable/datasets/toy_dataset.html#wine-recognition-dataset",
            "sklearn.datasets.load_wine()",
            "Thirteen chemical measurements for 178 Italian wine samples.",
            shared_license_note,
            with_observation_id(wine),
        ),
        DatasetRecord(
            "optical_digits",
            "digits_observations",
            "Optical recognition of handwritten digits",
            "computer vision",
            "classification and dimensionality reduction",
            "one processed 8 by 8 handwritten-digit image",
            "digit_label",
            "digit identity from 0 through 9",
            "https://scikit-learn.org/stable/datasets/toy_dataset.html#optical-recognition-of-handwritten-digits-dataset",
            "sklearn.datasets.load_digits()",
            "Each of 64 columns is an integer-valued pixel intensity from 0 "
            "through 16.",
            shared_license_note,
            with_observation_id(digits),
        ),
    ]


def build_database(output_path: Path) -> None:
    """Build the database atomically at ``output_path``."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(".sqlite.tmp")
    temporary_path.unlink(missing_ok=True)
    records = load_records()

    connection = sqlite3.connect(temporary_path)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(
            """
            CREATE TABLE dataset_catalog (
                dataset_id TEXT PRIMARY KEY,
                table_name TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                domain TEXT NOT NULL,
                task TEXT NOT NULL,
                observational_unit TEXT NOT NULL,
                target_column TEXT NOT NULL,
                target_description TEXT NOT NULL,
                row_count INTEGER NOT NULL CHECK (row_count > 0),
                feature_count INTEGER NOT NULL CHECK (feature_count > 0),
                source_url TEXT NOT NULL,
                bundled_loader TEXT NOT NULL,
                source_note TEXT NOT NULL,
                license_note TEXT NOT NULL,
                schema_version INTEGER NOT NULL,
                sklearn_version TEXT NOT NULL
            );

            CREATE TABLE dataset_columns (
                dataset_id TEXT NOT NULL,
                ordinal_position INTEGER NOT NULL,
                column_name TEXT NOT NULL,
                role TEXT NOT NULL CHECK (
                    role IN ('identifier', 'feature', 'target', 'target_label')
                ),
                PRIMARY KEY (dataset_id, column_name),
                FOREIGN KEY (dataset_id) REFERENCES dataset_catalog(dataset_id)
            );
            """
        )

        for record in records:
            record.frame.to_sql(
                record.table_name, connection, index=False, if_exists="fail"
            )
            connection.execute(
                f'CREATE UNIQUE INDEX "idx_{record.table_name}_observation" '
                f'ON "{record.table_name}" (observation_id)'
            )
            target_label = record.target_column.replace("_code", "_label")
            feature_count = sum(
                column not in {"observation_id", record.target_column, target_label}
                for column in record.frame.columns
            )
            connection.execute(
                """
                INSERT INTO dataset_catalog
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.dataset_id,
                    record.table_name,
                    record.title,
                    record.domain,
                    record.task,
                    record.observational_unit,
                    record.target_column,
                    record.target_description,
                    len(record.frame),
                    feature_count,
                    record.source_url,
                    record.bundled_loader,
                    record.source_note,
                    record.license_note,
                    SCHEMA_VERSION,
                    sklearn.__version__,
                ),
            )
            column_rows = []
            for position, column in enumerate(record.frame.columns, start=1):
                if column == "observation_id":
                    role = "identifier"
                elif column == record.target_column:
                    role = "target"
                elif column == target_label:
                    role = "target_label"
                else:
                    role = "feature"
                column_rows.append((record.dataset_id, position, column, role))
            connection.executemany(
                "INSERT INTO dataset_columns VALUES (?, ?, ?, ?)", column_rows
            )
        connection.commit()
        connection.execute("VACUUM")
    finally:
        connection.close()

    temporary_path.replace(output_path)


def main() -> None:
    """Parse command-line arguments and build the teaching database."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    build_database(arguments.output.resolve())
    print(f"built {arguments.output.resolve()}")


if __name__ == "__main__":
    main()
