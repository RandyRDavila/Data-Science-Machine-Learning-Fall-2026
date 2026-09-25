# Course datasets

`course_datasets.sqlite` is the versioned, read-only teaching database used by
the opening machine-learning notebooks. It contains real observations from the
four small datasets distributed with the repository's locked scikit-learn
version:

- diabetes progression;
- Wisconsin Diagnostic Breast Cancer;
- wine recognition; and
- optical handwritten digits.

The `dataset_catalog` table records provenance, task, observational unit,
target, upstream source, and limitations. `dataset_columns` records the role of
every column. The four observation tables use stable one-based
`observation_id` values.

Students should query the committed database. Dataset loaders belong only to
the ingestion script, which rebuilds the artifact deterministically:

```bash
uv run python scripts/build_course_database.py
```

SQLite is embedded and cross-platform; no database server or network connection
is needed. Rebuilding requires the locked project environment. A reachable
dataset is not automatically licensed, representative, ethical, or suitable for
deployment, so follow the source links and review upstream terms before reuse.
