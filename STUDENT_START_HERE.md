# Student start here

This is the canonical entry point for CMOR 438 / INDE 577. You do not need
prior experience with a terminal, virtual environments, GitHub Actions,
containers, or monitoring tools. Follow the core route below in order; use the
linked computing-foundations readings when a tool is unfamiliar.

## What you need for the first class

Install these three tools:

1. [Git](https://git-scm.com/downloads), which retrieves and versions the
   repository;
2. [Visual Studio Code](https://code.visualstudio.com/download), which is the
   course editor; and
3. [uv](https://docs.astral.sh/uv/getting-started/installation/), which installs
   the required Python version and creates the course environment.

When VS Code opens this repository, accept its recommendation to install the
Microsoft Python and Jupyter extensions. A GitHub account is needed only when
you begin opening issues or pull requests. Docker is not required until the
production-systems laboratory.

## Get the repository

Choose a normal local folder that you can write to. Avoid a temporary download
directory, a read-only network drive, or an aggressively synchronized folder.
Open a terminal and run:

```text
git clone https://github.com/RandyRDavila/Data-Science-Machine-Learning-Fall-2026.git
cd Data-Science-Machine-Learning-Fall-2026
code .
```

If `code` is not available as a terminal command, open VS Code normally and use
**File -> Open Folder** to open the repository root. Open the folder, not one
isolated notebook.

## Prepare Python once

In VS Code, choose **Terminal -> New Terminal**. Confirm that the prompt is at
the repository root, then run:

```text
uv run python scripts/setup_course.py
```

A successful run ends with a message containing:

```text
Verified rice_dsm:
Course setup complete. Open a notebook in VS Code and select the 'Rice DSM' kernel.
```

The exact paths above those lines differ across Windows, macOS, and Linux. Open
the assigned notebook, select **Rice DSM** in the kernel picker, and run its
environment-check cell. `sys.prefix` should identify this repository's
`.venv`; `rice_dsm.__file__` should identify `src/rice_dsm` in this repository.

## Verify before class

Run the fast structural checks:

```text
uv run pytest tests/test_course_setup.py tests/test_repository.py -q
```

If they pass, the shell, project environment, package import, and repository
structure agree. The complete suite takes longer because it executes the
instructional notebooks:

```text
uv run pytest -q
```

## The ordinary weekly workflow

Before beginning new work:

```text
git status
git switch main
git pull --ff-only
uv run python scripts/setup_course.py
```

Then read the assigned lecture directory's `README.md`, open notebook 00, and
follow the announced route. A numbered lecture directory is an instructional
unit, not necessarily one class meeting.

Use notebooks to investigate, visualize, and explain. Put reusable behavior in
`src/rice_dsm`, verification in `tests`, repeatable operations in `scripts`, and
operated applications in `projects`. A notebook is not a production server,
scheduler, deployment controller, or durable workflow engine.

## When you contribute code or course material

Read `CONTRIBUTING.md`, then use one branch for one coherent purpose:

```text
git switch -c student/short-description
git status
git add PATHS-YOU-INTEND-TO-COMMIT
git commit -m "Describe the completed change"
git push -u origin student/short-description
```

Open a pull request against `main`, complete its template, and read the first
causal failure from GitHub Actions if a check fails. Do not change a test merely
to make the check green; decide whether the implementation or the expectation
is wrong. Students without direct write access should work from a GitHub fork;
the course Git appendix explains both models.

Never commit API keys, passwords, tokens, private student information,
restricted research data, `.venv`, or notebook output containing such data.
Use the private reporting route in `SECURITY.md` for sensitive problems.

## Additional tools by unit

| Before this material | Prepare or read |
| --- | --- |
| Lecture 1 | Computing Foundations 01-05 |
| Lecture 3 and first pull request | Computing Foundations 06 and the Git/GitHub textbook appendix |
| Hosted APIs and agents | Computing Foundations 07 and the unit's `.env.example` |
| CI/CD and end-to-end systems | Computing Foundations 08 |
| Production monitoring laboratory | Computing Foundations 09-10 and Docker with Compose |

The production monitoring lab includes an offline evidence route for students
who cannot run containers locally. It teaches the same diagnostic reasoning but
does not claim that reading saved evidence is equivalent to operating a live
service.

## Diagnose by layer

When something fails, do not reinstall everything immediately.

1. **Location:** does the terminal contain `README.md`, `pyproject.toml`, and
   `notebooks/`?
2. **Command:** does `uv --version` work?
3. **Environment:** does `uv run python -c "import sys; print(sys.prefix)"`
   point to `.venv`?
4. **Package:** does `uv run python -c "import rice_dsm; print(rice_dsm.__file__)"`
   point into this repository?
5. **Notebook:** is the selected kernel **Rice DSM**, and has the notebook been
   restarted and run from top to bottom?
6. **Containers, when required:** is Docker running, are the expected ports
   free, and what does `docker compose ... ps` report?

The detailed recovery guides live in
`supplementary-materials/computing-foundations/`.
