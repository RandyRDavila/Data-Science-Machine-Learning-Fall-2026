# Files, folders, and paths

Programming tools need precise locations. Graphical file browsers hide some of
that detail, while terminals and Python expose it directly.

## The repository root

The **repository** is the course folder downloaded with Git. Its top-level
folder is the **repository root**. In this course, the root contains files such
as `README.md`, `pyproject.toml`, and `uv.lock`, as well as folders such as
`notebooks/`, `src/`, and `tests/`.

Many course commands must be run from this root because tools search the current
folder for configuration files.

## Absolute and relative paths

An **absolute path** begins at the filesystem's root and identifies one location
without additional context.

Examples:

```text
/Users/student/courses/data-science/README.md        # macOS
/home/student/courses/data-science/README.md         # Linux
C:\Users\student\courses\data-science\README.md     # Windows
```

A **relative path** begins at the current working directory:

```text
notebooks/lecture-01-python-foundations/README.md
```

Useful relative-path symbols are:

- `.` — the current directory;
- `..` — the parent directory;
- `/` — the separator on macOS and Linux;
- `\` — the conventional separator on Windows.

Python's `pathlib` library handles platform differences and is generally safer
than manually joining path strings.

```python
from pathlib import Path

lecture = Path("notebooks") / "lecture-01-python-foundations"
print(lecture.resolve())
```

## Extensions and hidden files

The ending of a filename often indicates its format: `.py`, `.ipynb`, `.md`, or
`.toml`. Files beginning with a dot, such as `.gitignore` and `.python-version`,
may be hidden by the operating system but still affect the project.

Avoid renaming configuration files or moving notebooks without also updating
the paths that refer to them.

## Checkpoint

Open the repository in your graphical file browser. Locate `pyproject.toml`,
`src/rice_dsm/`, and the Lecture 1 directory. Then identify the repository's
absolute path using the address bar or file information panel.
