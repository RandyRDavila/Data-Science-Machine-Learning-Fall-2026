# Lecture 1: Python Foundations I — Objects and Collections

This three-hour lecture establishes a shared foundation in the Python language.
Students use a repository-local virtual environment and Jupyter kernel, but the
details of packaging, dependencies, and versioning are intentionally deferred to
Lecture 3. Work through the notebooks in numeric order.

| Notebook | Topic | Approximate time |
| --- | --- | ---: |
| 00 | Cross-platform environment and Jupyter setup | 10 minutes |
| 01 | Values, types, names, objects, and boundary decisions | 30 minutes |
| 02 | Strings and trustworthy text data | 40 minutes |
| 03 | Lists, tuples, and trustworthy sequences | 40 minutes |
| 04 | Dictionaries, sets, and trustworthy structured data | 40 minutes |
| 05 | Iteration, comprehensions, and generators through graph theory | 45 minutes |

The complete reference route is intentionally larger than one class meeting.
For a three-hour meeting, notebooks 00–03 form the live route; notebook 04 is
the bridge into the next meeting, and notebook 05 follows it. The setup notebook
is designed to be started as students arrive. Guided and extension exercises
can be selected for class or completed afterward depending on discussion time.

## Learning outcomes

By the end of the lecture, students should be able to:

- explain names, objects, identity, equality, mutability, and basic types;
- inspect, slice, parse, normalize, validate, and format text without losing
  raw evidence;
- work confidently with built-in containers;
- choose data structures that preserve the meaning of scientific data;
- write and debug clear loops, comprehensions, and generators; and
- state and test simple invariants about transformed data.

## Before class

Students who are new to terminals, PowerShell, VS Code, Jupyter, or virtual
environments should begin with
[`Computing Foundations`](../../supplementary-materials/computing-foundations/README.md).
Lecture 1 requires only the practical setup recipe; Lecture 3 explains what the
commands and project files do.

From the repository root, run:

```bash
uv run python scripts/setup_course.py
```

This one command creates or updates the environment, verifies the course
package, and registers the **Rice DSM** kernel. Open the notebooks in VS Code and
select that named kernel.
