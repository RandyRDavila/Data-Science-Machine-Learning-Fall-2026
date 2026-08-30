## Purpose

<!-- What problem does this change solve, and for whom? -->

## What changed

<!-- Summarize the smallest coherent set of changes. -->

## Evidence

<!-- List commands run, relevant results, and any manual inspection. -->

- [ ] Targeted tests pass.
- [ ] `uv run ruff check src tests scripts` passes when Python changed.
- [ ] `uv run pytest -q` passes, or omitted checks are explained below.
- [ ] Changed notebooks restart and run from top to bottom with the Rice DSM kernel.
- [ ] Changed LaTeX compiles without warnings and the PDF was visually inspected.

## Contract and teaching impact

<!-- Check every statement that is true; explain material changes below. -->

- [ ] Student-facing instructions remain accurate on Windows, macOS, and Linux.
- [ ] New or changed behavior has tests, including relevant failure cases.
- [ ] Data provenance, units, schemas, and split boundaries are documented.
- [ ] Reusable logic is in `rice_dsm`, not available only through notebook state.
- [ ] No secrets, credentials, private student data, or restricted data are included.
- [ ] Dependency, API, artifact, or compatibility changes are identified below.

## Reviewer notes

<!-- Where should review attention go? Include risks, limitations, screenshots, PDF pages, or follow-up work. -->

## Related issue

<!-- Use "Closes #123" when merging this PR should close an issue. -->
