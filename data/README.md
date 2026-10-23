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

## Bounded MNIST teaching sample

`mnist_teaching_sample.npz` contains authentic 28-by-28 MNIST images: 240
training observations and 60 held-out observations from each digit class. The
deterministic, class-balanced subset keeps Lecture 12's from-scratch network
executable offline and in continuous integration. It does not replace the full
60,000/10,000 benchmark for research comparisons.

The source is the standard `mnist.npz` archive distributed by Keras from
`https://storage.googleapis.com/tensorflow/tf-keras-datasets/mnist.npz`.
The committed teaching artifact has SHA-256 digest
`16b57f334fb1b378baf07f5ae79fc9f46261525dd2fddaa6c7a19ac581a7b279`;
the test suite checks this digest so the reviewed authentic sample cannot be
silently replaced by generated or altered observations.
Given that upstream file, reproduce the committed subset with:

```bash
uv run python scripts/build_mnist_teaching_sample.py /path/to/mnist.npz
```

MNIST originates from NIST handwriting data and was standardized by Yann
LeCun, Corinna Cortes, and Christopher Burges. Consult the upstream MNIST page
and original data terms before redistribution outside this teaching context.
