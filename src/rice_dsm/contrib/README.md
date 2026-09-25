# Student contribution namespace

This directory contains independently reviewable extensions developed through
the course contribution process. A contribution is real package code: it must
have a documented interface, tests, scientific or engineering motivation, and
a maintainer who responds to review.

This is an **onboarding and incubation namespace**, not the final architecture
of the shared machine-learning platform and not a home for complete final
products. The first scaffold proves that Git, packaging, tests, review, and CI
work. Mature algorithms move through an integration issue into `rice_dsm.ml`;
final products consume a tagged release from separate repositories.

## Layout

Use one unique, descriptive import name per contribution:

```text
src/rice_dsm/contrib/PROJECT_SLUG/
├── __init__.py       # Small public interface
├── core.py           # Implementation; split only when responsibilities differ
└── README.md         # Question, contract, provenance, examples, and limitations

tests/contrib/PROJECT_SLUG/
└── test_core.py      # Normal, boundary, and failure behavior
```

Create this layout from the repository root with:

```text
uv run python scripts/scaffold_student_package.py PROJECT_SLUG
```

The slug must use lowercase letters, digits, and underscores, begin with a
letter, and describe the problem rather than a person's name. For example,
`graph_statistics` is preferable to `randys_project`.

## Architectural boundary

Import contributions explicitly:

```python
from rice_dsm.contrib.graph_statistics import contribution_name
```

Do not add every contribution to `rice_dsm/__init__.py` or this package's
`__init__.py`. A central import registry would create unnecessary merge
conflicts, increase import time, and allow one optional project to break the
entire package. Code that becomes a stable, broadly useful part of `rice_dsm`
can later be promoted through a separate design review. Machine-learning
algorithms additionally satisfy the common contracts and acceptance standard in
[`rice_dsm.ml`](../ml/README.md).

Importing a contribution must not read files, contact a network service, train
a model, mutate global state, or require credentials. Put those operations
behind explicit functions and make their failure modes testable.

## Required evidence

Every contribution pull request must include:

- an approved issue defining the problem and unique slug;
- NumPy-style docstrings and type hints on its public interface;
- tests for ordinary behavior, at least one boundary, and relevant failures;
- a README that records assumptions, data provenance, limitations, and a small
  usage example;
- no secrets, private student information, graded work, or restricted data;
- passing Ruff, focused tests, and the complete CI gate; and
- review by two eligible classmates plus final maintainer review, or a
  maintainer-documented exception when two conflict-free reviewers are not
  available.

New third-party dependencies, changes to shared package interfaces, and edits
to deployment or GitHub Actions are separate architectural decisions. Propose
them in the issue before changing `pyproject.toml`, `uv.lock`, `.github/`, or
production workflows.

The complete worked process is in [Contributing to the shared course
package](../../../supplementary-materials/computing-foundations/11-contributing-to-the-shared-course-package.md).
