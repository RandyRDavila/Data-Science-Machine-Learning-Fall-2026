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

The repository also demonstrates delivery: reviewed `main` revisions publish a
small course site, while version tags produce approved, checksummed releases of
the textbook and Python package.

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
│   ├── lecture-09-supervised-learning-systems/
│   ├── lecture-10-linear-regression-regularization/
│   ├── lecture-11-classification-decisions/
│   ├── lecture-12-geometric-learning/
│   ├── lecture-13-decision-trees/
│   ├── lecture-14-ensemble-learning/
│   ├── lecture-15-model-selection-evaluation/
│   ├── lecture-16-neural-networks-autodiff/
│   ├── lecture-17-reliable-supervised-systems/
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
├── site/                      # Reviewed source for the deployed course site
└── .github/
    └── workflows/             # Integration, delivery, and release automation
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
and its required second pass. The
[`Part II roadmap`](notes/part-ii-roadmap.md) records the supervised-learning
architecture, unit sequence, running scientific case, and release standard.

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

## Continuous integration and delivery

GitHub Actions runs the locked setup on Linux, macOS, and Windows for every pull
request and every push to `main`. Restricting push runs to `main` prevents a
branch with an open pull request from launching the same matrix twice. CI checks
formatting, builds the package, verifies the source path and named kernel, runs
the unit and repository tests, and executes every notebook from top to bottom.

The workflow reports one stable required check named **CI gate**. In the GitHub
repository settings, protect the teaching branch by requiring pull requests and
the **CI gate** status check before merging. CI cannot stop a local `git push`,
but that branch rule prevents an unverified change from entering the protected
course branch.

Companion workflows compile changed textbook source and upload the PDF for
review, inspect changed dependencies for known high-severity vulnerabilities,
and apply area labels without executing pull-request code. Dependabot proposes
grouped updates for the `uv` environment and pinned GitHub Actions. The complete
workflow, deployment, release, environment, and rollback explanation lives in
[`.github/README.md`](.github/README.md).

The static course site is a deliberately bounded production example. A relevant
merge to `main` compiles the textbook, builds one identifiable site artifact,
deploys it through GitHub Pages, and verifies the public revision and PDF
checksum. A `course-vX.Y.Z` tag instead builds a checksummed textbook, wheel, and
source archive, records provenance, and waits for approval at the
`course-release` environment before creating a GitHub Release. Students can
follow the entire worked example in [From CI to delivery and
deployment](supplementary-materials/computing-foundations/08-continuous-delivery-and-deployment.md).

## Contributing and reporting problems

GitHub presents structured forms for software bugs, course-content corrections,
instructional proposals, and public repository questions. Please read
[`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a pull request. Suspected
vulnerabilities, exposed credentials, or private student information must be
reported privately according to [`SECURITY.md`](SECURITY.md), never through a
public issue.

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

### Part II: Supervised Learning Systems

Part II treats supervised learning as a complete prediction system rather than
an algorithm catalog. A recurring battery-cell case moves through three linked
paths: training creates a versioned candidate, prediction applies an approved
artifact, and feedback joins predictions to delayed outcomes. The units are:

| Unit | Topic | Executable entry point |
| ---: | --- | --- |
| 9 | Prediction contracts, leakage-safe splits, and baselines | [`lecture-09-supervised-learning-systems`](notebooks/lecture-09-supervised-learning-systems/) |
| 10 | Linear regression, optimization, and regularization | [`lecture-10-linear-regression-regularization`](notebooks/lecture-10-linear-regression-regularization/) |
| 11 | Classification, calibration, and decision policies | [`lecture-11-classification-decisions`](notebooks/lecture-11-classification-decisions/) |
| 12 | Nearest neighbors, margins, and kernels | [`lecture-12-geometric-learning`](notebooks/lecture-12-geometric-learning/) |
| 13 | Decision trees, pruning, and stability | [`lecture-13-decision-trees`](notebooks/lecture-13-decision-trees/) |
| 14 | Bagging, forests, boosting, voting, and stacking | [`lecture-14-ensemble-learning`](notebooks/lecture-14-ensemble-learning/) |
| 15 | Model selection, uncertainty, and promotion | [`lecture-15-model-selection-evaluation`](notebooks/lecture-15-model-selection-evaluation/) |
| 16 | Neural networks, backpropagation, and autodiff | [`lecture-16-neural-networks-autodiff`](notebooks/lecture-16-neural-networks-autodiff/) |
| 17 | Reliable release, monitoring, outcomes, and retraining | [`lecture-17-reliable-supervised-systems`](notebooks/lecture-17-reliable-supervised-systems/) |

Each directory currently contains its unit contract, planned detailed notebook
sequence, and a CI-executable entry notebook. These entry points will be expanded
into full laboratories one unit at a time. The textbook already carries the
connected Part II mathematical and systems narrative.

### Production monitoring laboratory

The executable
[`production-monitoring-lab`](projects/production-monitoring-lab/) places the
battery-risk example inside an instrumented prediction service. Package modules
implement the API, model, persistence, structured logging, metrics, and delayed
outcome path. Scripts generate traffic and controlled incidents; Docker Compose
runs Prometheus, Loki, Tempo, Grafana Alloy, and a provisioned Grafana dashboard.
Students diagnose failures from operational evidence and write a post-incident
review. The system is deliberately outside `notebooks/`: notebooks support live
explanation and statistical investigation but do not serve as the production
runtime.

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
