# The course environment

A Python installation contains an interpreter. A **virtual environment** is an
isolated project-specific installation space. This repository uses `uv` to
manage both Python and the environment consistently.

## Why isolation matters

Two projects may require different versions of the same library. Installing all
packages into one global Python can make an unrelated project fail after an
upgrade. The `.venv` directory keeps this course's installed packages local to
the repository.

`.venv` is generated and is intentionally excluded from Git. `uv.lock` is
committed because it records the exact dependency solution needed to recreate
the environment.

## The everyday command

Run these from the repository root:

```text
uv run python scripts/setup_course.py
```

`uv run` first reads `pyproject.toml` and `uv.lock`, creates or updates `.venv`,
and installs the local `rice-dsm` package. The setup script verifies that the
editable package can be imported and registers a named Jupyter kernelspec that
points back to `.venv`. The command then exits. Open notebooks and select the
**Rice DSM** kernel in VS Code; no manual environment activation is required.

Other examples are:

```text
uv run python
uv run pytest
uv run ruff check src tests
```

## Editable installation

The course package lives in `src/rice_dsm/`. It is installed in **editable**
mode, so changing its Python source changes what notebooks import without
building and reinstalling a wheel after every edit.

Restart a notebook kernel after modifying an already imported module. Python
caches imported modules within a running process.

## A reliable diagnostic sequence

When a command or import fails, collect evidence in this order:

```text
pwd
ls
uv --version
uv run python --version
uv run python -c "import rice_dsm; print(rice_dsm.__file__)"
```

On PowerShell, these commands also work. The results answer:

1. Am I in the repository root?
2. Is `uv` available?
3. Is the project using the expected Python?
4. Is the local package installed, and from where?

Avoid responding to every import error with `pip install`. Installing into the
wrong interpreter can hide the real issue and make the environment harder to
understand.

## Further reading

- [`uv` installation](https://docs.astral.sh/uv/getting-started/installation/)
- [Installing and managing Python with `uv`](https://docs.astral.sh/uv/guides/install-python/)
- [`uv` project guide](https://docs.astral.sh/uv/guides/projects/)
