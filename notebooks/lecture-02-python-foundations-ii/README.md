# Lecture 2: Python Foundations II — Programs and Native Data

This reference sequence turns Python expressions and collections into reliable
programs. Students design functions and domain records, adapt callable
interfaces, read common scientific data formats using only the standard
library, and integrate the pieces into a small tested pipeline. No NumPy or
pandas is required yet.

## Notebook sequence

| Notebook | Topic | Approximate time |
| --- | --- | ---: |
| 00 | Functions and interfaces through probability theory | 60 minutes |
| 01 | Classes and domain modeling across mathematics, science, and engineering | 60 minutes |
| 02 | Callable interfaces: lambdas, `*args`, and `**kwargs` | 45 minutes |
| 03 | Native JSON and CSV: build a scientific knowledge graph | 65 minutes |

The complete reference sequence is intentionally longer than one live meeting.
The lecture itinerary should select a core route and assign remaining worked
examples or practice outside class. This keeps the notebooks
useful as detailed references without pretending every cell fits into three
hours.

## Learning outcomes

By the end of the lecture, students should be able to:

- design focused functions with explicit inputs, outputs, documentation, and
  type hints;
- represent finite probability mass functions, events, and random variables as
  composable callables;
- validate probability mass and control pseudorandom state explicitly;
- represent a scientific observation with a class or dataclass when that
  improves clarity;
- use lambdas for small local callable adapters and choose named functions for
  substantial behavior;
- distinguish `*` and `**` unpacking at call sites from `*args` and `**kwargs`
  collection in function definitions;
- design variadic interfaces without hiding stable options or misspellings;
- use `pathlib` and context managers to handle files safely across platforms;
- read UTF-8 JSON and CSV with Python's standard library;
- convert raw mappings into validated nodes and relationships;
- enforce referential integrity in a custom knowledge graph;
- query graph neighborhoods and directed paths with breadth-first search;
- preserve provenance and report rejected records instead of silently losing
  them; and
- assemble and test a small ingestion, validation, transformation, and summary
  pipeline.

## Professional lens

The data scientist asks whether the loaded values preserve the scientific
meaning of the source. The software engineer asks whether another person can
rerun, test, diagnose, and safely extend the pipeline. Strong work satisfies
both forms of correctness.

## Preparation

Run the same setup command from the repository root:

```bash
uv run python scripts/setup_course.py
```

Open the notebooks in VS Code and select the **Rice DSM** kernel. Lecture 3 will
explain the packaging and environment machinery behind that workflow.
