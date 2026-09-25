# Contributing

Contributions should improve the mathematical accuracy, instructional clarity,
reproducibility, or professional quality of the course repository. Small,
reviewable changes are easier to validate and teach from than broad rewrites.
All participation follows the repository's
[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md): critique claims and code rather than
people, protect privacy, give credit, and move confidential course matters out
of public GitHub artifacts.

## Before starting

Search existing issues and pull requests. Open the appropriate structured issue
for a bug, content correction, proposal, or public repository question. For a
substantial change, agree on the problem and scope before writing a large patch.

Never post grades, graded submissions, accommodations, personal circumstances,
API keys, credentials, private student information, or restricted data in an
issue, commit, notebook output, or pull request.

Students proposing a shared package extension should use the **Student package
contribution** issue form and wait for its scope and unique import name to be
approved. The worked [course-package contribution
guide](supplementary-materials/computing-foundations/11-contributing-to-the-shared-course-package.md)
explains the public fork, branch, review, CI, conflict, and maintenance process
without assuming prior open-source experience.

## Local setup

Clone the repository, open its root folder in VS Code, and run:

```bash
uv run python scripts/setup_course.py
```

Use a short branch with one purpose. Keep local secrets in ignored environment
files or an approved secret manager, never in tracked source.

## Make the change

- Preserve cross-platform behavior on Windows, macOS, and Linux.
- Put reusable logic in `src/rice_dsm/` with types, NumPy-style docstrings,
  explicit exceptions, and tests.
- Treat notebooks as experimental laboratories. Restart and run all cells; move
  durable state and reusable behavior into packages, tests, scripts, or services.
- Preserve data provenance, licenses, units, schemas, observational units, time
  boundaries, and train/evaluation splits.
- Add the smallest useful dependency and update `uv.lock` through `uv`.
- Do not commit generated caches, local environments, secrets, or private data.

### Student subpackages

Student-developed extensions live under `src/rice_dsm/contrib/PROJECT_SLUG/`
with mirrored tests under `tests/contrib/PROJECT_SLUG/`. Create a minimal,
passing layout with:

```bash
uv run python scripts/scaffold_student_package.py PROJECT_SLUG
```

Do not register each extension in the root `rice_dsm` interface. Contributions
remain explicitly imported and independently testable until a separate design
review promotes shared behavior into the core package. Propose new dependencies
or changes to `pyproject.toml`, `uv.lock`, `.github/`, deployment, or shared core
interfaces before implementing them.

The contribution namespace is an onboarding and incubation boundary. Mature
machine-learning components integrate into `src/rice_dsm/ml/` only after an
approved platform issue establishes the common interface, mathematical
contract, differential evidence, and migration plan. Final products belong in
separate repositories and consume a tagged release rather than copying package
source.

## Validate

For Python or repository changes, run:

```bash
uv run ruff check src tests scripts
uv run pytest -q
```

For textbook changes, build and visually inspect the PDF:

```bash
make -C textbook
```

The build must finish without warnings. Check equations, code, page breaks,
tables, figures, headers, and the table of contents. Update the stable PDF under
`output/pdf/` when textbook source changes.

## Open the pull request

Write a coherent commit message and complete the pull-request template. Explain
the problem, what changed, evidence, compatibility impact, limitations, and the
highest-risk review areas. Do not mark an inapplicable checklist item as complete;
explain why it does not apply.

The stable `CI gate` must pass before merge. Other workflows provide dependency,
labeling, and textbook evidence when their paths are relevant. Address review
comments with code, evidence, or a reasoned technical response.

Student contributions require reviews from two eligible classmates in addition
to final maintainer review. If the roster cannot provide two conflict-free
reviewers, the maintainer records the exception on the pull request and assigns
the strongest available independent review. Peer review is an engineering
exercise, even when the peer does not have merge permission: examine the
contract, mathematical or scientific validity, tests, provenance, limitations,
and failure behavior.

## Publishing

Merging to `main` may deploy the public course site. Review visible copy,
textbook links, and deployment-contract changes accordingly. Only maintainers
publish versioned releases. A release tag must be annotated and must exactly
match the version in `pyproject.toml`, for example `course-v0.1.0` for version
`0.1.0`. Never move an existing release tag; publish a corrected patch version.

The release workflow deliberately pauses at the protected `course-release`
environment. Inspect the completed build and test evidence before approving
publication.
