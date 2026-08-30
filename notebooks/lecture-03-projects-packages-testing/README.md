# Lecture 3: Projects, Packages, and Testing

This unit opens the machinery used implicitly in Lectures 1 and 2: project
boundaries, virtual environments, dependency resolution, versions, modules,
packages, tests, automation, and CI/CD. It shows how experimental notebook code
graduates into reusable and independently verified software.

## Notebook sequence

| Notebook | Topic | Approximate reference time |
| --- | --- | ---: |
| 00 | Reproducible projects, environments, packages, and versions | 60 minutes |
| 01 | From notebook exploration to a tested Python package | 60 minutes |
| 02 | Testing scientific software: from unit tests to CI/CD | 120 minutes |

The complete reference route is longer than a typical live segment. The weekly
announcement identifies the sections demonstrated in class and the sections
assigned as laboratory reading or practice.

## Learning outcomes

Students should be able to:

- explain what `uv sync`, `uv run`, and the course setup script do;
- distinguish an interpreter, virtual environment, Jupyter kernel, distribution,
  import package, module, script, and command-line interface;
- explain version constraints, resolved versions, and a lockfile;
- move stable behavior from a notebook into `src/rice_dsm/` behind a deliberate
  public interface;
- derive unit, integration, system, regression, and data tests from risks and
  contracts; and
- distinguish CI, continuous delivery, and continuous deployment while reading
  this repository's cross-platform workflow.

## Preparation

Run `uv run python scripts/setup_course.py` from VS Code's integrated terminal.
Read [How the course Python project works](../../supplementary-materials/computing-foundations/06-how-the-course-python-project-works.md)
alongside notebook 00.
