# Guided exercises

Complete these in order. Record the command you ran, the important part of its
output, and one sentence explaining what the command did.

## Exercise 1: orient yourself

1. Open a terminal.
2. Display the current working directory.
3. Navigate to the repository root.
4. List its contents.
5. Confirm that `README.md`, `pyproject.toml`, and `notebooks/` are present.

**Check:** How is the current working directory different from the repository
root? When are they the same?

## Exercise 2: navigate without a graphical file browser

1. Enter `notebooks/lecture-01-python-foundations/`.
2. List its files.
3. Move back to the repository root using `..`.
4. Confirm your location.

**Challenge:** From the repository root, list the lecture directory without
first entering it.

## Exercise 3: inspect the environment

Run:

```text
uv --version
uv sync
uv run python --version
uv run python -c "import sys; print(sys.executable); print(sys.prefix)"
```

**Check:** Which `sys.prefix` output shows that Python is using this repository's
virtual environment? Why might `sys.executable` show uv's underlying interpreter?

## Exercise 4: prepare and verify a VS Code notebook

1. Run `uv run python scripts/setup_course.py` in VS Code's terminal.
2. Open the first Lecture 1 notebook.
3. Select the **Rice DSM** kernel in the notebook's upper-right corner.
4. Execute the cell that displays `sys.executable` and `sys.prefix`.
5. Confirm that `sys.prefix` identifies this repository's `.venv`.

## Exercise 5: use the package outside a notebook

From the repository root, run:

```text
uv run python -c "from rice_dsm import StudentRecord; print(StudentRecord('ada lovelace', 95))"
```

Explain why the name is normalized and identify the source file that defines
`StudentRecord`.

## Exercise 6: diagnose a location error

Move to the parent directory of the repository and run `uv run pytest`. Observe
the message without trying random fixes. Return to the repository root and run
the command again.

**Reflection:** What evidence distinguished a project-location problem from a
Python-code problem?

## Exercise 7: interpreter detective

Compare these commands if both are available:

```text
python --version
uv run python --version
```

They may match, but they do not have to. Explain why course commands use the
second form.

## Optional challenge: paths in Python

Use `pathlib.Path` to print the absolute path of the first Lecture 1 notebook,
check whether it exists, and print its filename without its extension.
