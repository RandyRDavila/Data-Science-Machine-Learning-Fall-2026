# Tests for student contributions

Mirror each package under `src/rice_dsm/contrib/PROJECT_SLUG/` with a directory
named `tests/contrib/PROJECT_SLUG/`. Test public behavior rather than private
implementation details. Include normal examples, boundaries, invalid input,
and scientific or mathematical properties appropriate to the project.

Run one contribution's tests while developing:

```text
uv run pytest tests/contrib/PROJECT_SLUG -q
```

Before opening or updating a pull request, also run the complete repository
gate described in `CONTRIBUTING.md`.
