# Data Science and Machine Learning

*A Systems Approach*

This repository is the source and executable companion for a developing
graduate text used in **CMOR 438 / INDE 577: Data Science & Machine Learning**
at Rice University.

The text treats data science and machine learning as mathematical,
computational, and engineered disciplines. Its central question is how
scientific meaning survives the path from evidence and code to models,
interfaces, deployment, and revision. The repository makes that argument
executable through lecture notebooks, a progressively developed Python package,
tests, data, exercises, and continuous integration.

The LaTeX source lives under [`textbook/`](textbook/), and the compiled text
is published at
[`output/pdf/data-science-machine-learning-textbook.pdf`](output/pdf/data-science-machine-learning-textbook.pdf).
The notebooks are computational laboratories rather than substitutes for the
prose. Reusable implementations move into `rice_dsm`; tests and CI preserve
their contracts.

## Text and repository

- `textbook/` develops definitions, arguments, examples, and exercises.
- `notebooks/` provides executable investigations organized by lecture.
- `src/rice_dsm/` holds reusable software developed under professional
  engineering conventions.
- `tests/` and `.github/workflows/` make selected claims executable across
  supported operating systems.
- `supplementary-materials/` provides slower introductions to terminals, VS
  Code, environments, Git, and related tools.

## Repository structure

```text
.
├── README.md
├── LICENSE
├── pyproject.toml             # Package metadata, dependencies, and tool config
├── uv.lock                    # Reproducible Python environment
├── .vscode/
│   └── extensions.json        # Recommend the Python and Jupyter extensions
├── syllabus/
│   ├── syllabus.tex           # Main LaTeX source
│   ├── references.bib
│   ├── figures/
│   └── Makefile               # Compile and clean the syllabus
├── notebooks/
│   ├── lecture-01-python-foundations/
│   │   ├── README.md          # Lecture plan, outcomes, and preparation
│   │   ├── 00-cross-platform-environment-and-jupyter.ipynb
│   │   ├── 01-values-types-and-objects.ipynb
│   │   ├── 02-strings-and-text-data.ipynb
│   │   └── ...
│   ├── lecture-02-python-foundations-ii/
│   │   ├── README.md
│   │   ├── 00-functions-and-functional-patterns.ipynb
│   │   └── ...
│   ├── lecture-03-projects-packages-testing/
│   │   ├── README.md
│   │   ├── 00-projects-environments-and-packaging.ipynb
│   │   ├── 01-scripts-modules-and-packages.ipynb
│   │   └── 02-testing-and-automation.ipynb
│   ├── lecture-04-numpy-pandas/
│   ├── lecture-05-visualization-simulation/
│   ├── lecture-06-databases-data-systems/
│   ├── lecture-07-llm-tools-agents/
│   ├── lecture-08-end-to-end-data-products/
│   └── ...                    # One directory per instructional unit
├── src/
│   └── rice_dsm/
│       ├── __init__.py
│       └── ...                # Reusable code developed during the course
├── tests/                     # Executable examples and repository safeguards
├── assignments/               # Assignment descriptions and starter materials
├── notes/                     # Topic notes and supporting instructional content
├── supplementary-materials/   # Computing guides, readings, exercises, diagrams
├── data/
│   ├── README.md              # Provenance and retrieval instructions
│   ├── raw/                   # Immutable source data, usually not committed
│   └── processed/             # Derived data, usually reproducible
├── scripts/                   # Repeatable data, build, and maintenance tasks
└── .github/
    └── workflows/             # Package tests and other automated checks
```

The exact contents will evolve with the course. Empty directories should be
added only when they are needed rather than created in advance.

## Working conventions

### Lecture units and class meetings

Each numbered lecture directory is a coherent **instructional unit**, not a
promise that the unit occupies one complete class meeting. An in-person
three-hour meeting may combine several shorter units, spend most of its time on
one substantial unit, or follow a selected core route while assigning the
remaining notebook sections as laboratory work. The syllabus and weekly
announcement determine the live itinerary.

Lecture units use the naming convention `lecture-NN-short-topic/`. Their numbers
preserve conceptual order without coupling the material to dates or forcing a
one-to-one relationship with meetings. Within a lecture directory, notebooks
use `NN-short-subtopic.ipynb` so they appear in the intended local order.
Lecture-specific figures and small supporting files may live beside them in a
clearly named companion directory.

Notebooks are experimental laboratories: they combine a question, executable
investigation, evidence, and interpretation. They may demonstrate an
end-to-end path, but they are not the production system or the sole record of a
serious research project. Reusable logic moves into `rice_dsm`; verification
moves into tests and CI; repeatable operations move into scripts or workflows;
and shared state and user-facing behavior move behind databases and services.
The notebooks then import and explain those durable components.

The [`Teaching Notebook Standard`](notebooks/TEACHING_NOTEBOOK_STANDARD.md)
defines the required instructional arc, practice ladder, professional-quality
signals, and release rubric used as notebooks are upgraded.
The companion [`Professional Practices Spine`](notebooks/PROFESSIONAL_PRACTICES.md)
maps scientific and software-engineering habits across the semester.
Internal curriculum decisions and restart points are recorded in
[`notes/`](notes/); the current handoff captures the provisional Part I boundary
and its required second pass.

### Python environment and package

The project will target one documented Python version and use `pyproject.toml`
as the source of truth for package metadata, dependencies, and development-tool
configuration. A repository-local virtual environment (`.venv`) and a committed
lockfile will make the environment reproducible.

The package uses the `src` layout so that notebooks and tests exercise the
installed package instead of accidentally importing files from the repository
root. During development, the package should be installed in editable mode.

This repository uses `uv` for Python installation, environment creation,
dependency locking, editable package installation, and command execution.

## Getting started

Install `uv`, clone the repository, open the repository folder in VS Code, and
run one command in VS Code's integrated terminal:

```bash
uv run python scripts/setup_course.py
```

`uv run` automatically synchronizes `.venv` from the committed project files.
The setup script then verifies the editable course package and registers the
environment as the **Rice DSM** notebook kernel. Open a notebook in VS Code and
select that kernel. The repository recommends Microsoft's Python and Jupyter
extensions when the folder first opens.

Run the automated package checks with:

```bash
uv run pytest
uv run ruff check src tests
```

The [`tests/README.md`](tests/README.md) guide explains how to read and run the
suite, interpret failures, choose edge cases, and use tests as executable
specifications while the course package develops.

## Continuous integration

GitHub Actions runs the locked setup on Linux, macOS, and Windows for every push
and pull request. CI checks formatting, builds the package, verifies the source
path and named kernel, runs the unit and repository tests, and executes every
notebook from top to bottom.

The workflow reports one stable required check named **CI gate**. In the GitHub
repository settings, protect the teaching branch by requiring pull requests and
the **CI gate** status check before merging. CI cannot stop a local `git push`,
but that branch rule prevents an unverified change from entering the protected
course branch.

## Lecture materials

### Lecture 1: Python foundations I

The first lecture develops the language foundations used throughout the course:
the practical use of a cross-platform environment, values and types, Python's
object model, Boolean control flow, strings, sequences, mappings, sets,
iteration, comprehensions, and generators. Its notebooks and detailed lecture plan live in
[`notebooks/lecture-01-python-foundations`](notebooks/lecture-01-python-foundations/).

### Lecture 2: Python foundations II and native data

The second lecture develops functions, interfaces, classes, and data modeling;
introduces lambdas, argument unpacking, and carefully designed variadic
interfaces; then loads JSON concepts and CSV relationships into a custom
scientific knowledge graph using only Python's standard library. Its notebooks
and detailed lecture plan live in
[`notebooks/lecture-02-python-foundations-ii`](notebooks/lecture-02-python-foundations-ii/).

### Lecture 3: Projects, packages, and testing

The third lecture explains the environment and commands used in Lectures 1 and
2, including project configuration, dependencies, lockfiles, modules, packages,
versioning, testing, automation, and CI/CD. Its notebooks live in
[`notebooks/lecture-03-projects-packages-testing`](notebooks/lecture-03-projects-packages-testing/).

### Lecture 4: NumPy and pandas

This unit moves from native Python containers to array-oriented numerical work
with NumPy and labeled tabular work with pandas. Its notebook lives in
[`notebooks/lecture-04-numpy-pandas`](notebooks/lecture-04-numpy-pandas/).

### Lecture 5: Visualization and simulation

This unit develops honest, accessible scientific visualization and uses
simulation as a form of executable reasoning. Its notebook lives in
[`notebooks/lecture-05-visualization-simulation`](notebooks/lecture-05-visualization-simulation/).

### Lecture 6: Databases and data systems

This unit treats local and remote databases, transactions, analytical files,
cloud roles, and larger-than-memory workflows as parts of the scientific
system. Its notebook lives in
[`notebooks/lecture-06-databases-data-systems`](notebooks/lecture-06-databases-data-systems/).

### Lecture 7: LLM tools and agents

This unit places language models inside deterministic validation, authority,
evaluation, and recovery boundaries. Its notebook and offline demonstrations
live in
[`notebooks/lecture-07-llm-tools-agents`](notebooks/lecture-07-llm-tools-agents/).

### Lecture 8: End-to-end data products

The Part I synthesis traces a value from durable storage through a service and
HTTP API to a client, deployment workflow, and operational evidence. Its
notebook and local vertical-slice demonstration live in
[`notebooks/lecture-08-end-to-end-data-products`](notebooks/lecture-08-end-to-end-data-products/).

## Supplementary materials

Students who are new to terminals, PowerShell, VS Code, Jupyter, virtual
environments, or project navigation can begin with the
[`supplementary-materials`](supplementary-materials/) guides. These readings,
exercises, and diagrams are optional support materials and do not assume prior
developer-tool experience.

### Syllabus

The syllabus source lives in `syllabus/` and is written in LaTeX. Its build
command should be captured in the local `Makefile` so the PDF can be reproduced
without remembering a long command. LaTeX intermediate files should not be
committed; whether the compiled PDF is versioned or published as a release
artifact will be decided with the course distribution workflow.

### Data

Small, license-compatible teaching datasets may be committed when useful. Large,
restricted, or readily downloadable datasets should stay out of Git. Retrieval
and transformation steps should be documented in `data/README.md` and automated
in `scripts/` whenever practical.

## Status

This graduate text and its executable repository are under active development
for Fall 2026. Part I has a complete draft, and the Python foundations,
packaging, testing, numerical-computing, data-systems, agent, and deployment
materials are being refined as one cumulative argument.
