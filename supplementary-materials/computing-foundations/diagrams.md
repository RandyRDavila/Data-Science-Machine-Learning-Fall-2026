# Workflow diagrams

These diagrams provide mental models for the tools used in the course. The
arrows describe relationships, not commands that students must memorize.

## From repository to running notebook

```mermaid
flowchart LR
    A[Course repository] --> B[pyproject.toml and uv.lock]
    B -->|one setup command| C[Local .venv]
    C --> D[Rice DSM kernel]
    E[VS Code and Jupyter extension] --> D
    E --> F[Notebook document]
    D --> G[Installed rice_dsm package]
    G --> H[src/rice_dsm]
```

VS Code sends a code cell through its Jupyter extension to the kernel. The
kernel—not VS Code or the notebook file itself—runs Python and imports the
editable course package.

## Where should code live?

```mermaid
flowchart TD
    A[New code written during exploration] --> B{Mostly explanation or one-time exploration?}
    B -->|Yes| C[Keep it in the lecture notebook]
    B -->|No| D{Useful across notebooks or independently testable?}
    D -->|Not yet| C
    D -->|Yes| E[Move it into src/rice_dsm]
    E --> F[Add tests in tests/]
    F --> G[Import it from notebooks]
```

Moving code into the package is a design decision made when reuse or testing
becomes valuable, not a requirement for every small notebook example.

## Diagnosing an import problem

```mermaid
flowchart TD
    A[Import fails] --> B{At repository root?}
    B -->|No| C[Navigate to repository root]
    B -->|Yes| D{Environment synchronized?}
    C --> D
    D -->|No| E[Run the course setup command]
    D -->|Yes| F{Notebook kernel uses .venv?}
    E --> F
    F -->|No| G[Select the .venv kernel]
    F -->|Yes| H[Read the specific traceback and inspect the import]
    G --> I[Restart kernel and retry]
    H --> I
```

This sequence checks location and interpreter before installing anything.

## Filesystem orientation

```mermaid
flowchart TD
    A[Computer filesystem] --> B[Courses folder]
    B --> C[Course repository root]
    C --> D[notebooks]
    D --> E[lecture-01-python-foundations]
    C --> F[src]
    F --> G[rice_dsm package]
    C --> H[tests]
    C --> I[supplementary-materials]
```

## From a student fork to the shared package

```mermaid
flowchart LR
    A[Course repository<br/>upstream] -->|fork once| B[Student GitHub fork<br/>origin]
    B -->|clone once| C[Local repository]
    A -->|fetch accepted changes| C
    C -->|create feature branch| D[Student contribution]
    D -->|focused and full tests| E[Local evidence]
    E -->|commit and push| B
    B -->|open pull request| F[Review boundary]
    F --> G[Peer review]
    F --> H[Read-only CI<br/>Linux, macOS, Windows]
    G --> I[Maintainer review]
    H --> I
    I -->|merge accepted revision| A
```

The fork supplies a writable remote without granting write access to the course
repository. A pull request does not bypass ownership: it presents an exact
revision for discussion, automated checks, and maintainer integration.

## Trust boundaries in course automation

```mermaid
flowchart TD
    A[Untrusted fork pull request] --> B[pull_request workflows]
    B --> C[Read-only token]
    B --> D[No repository secrets]
    B --> E[Build, lint, and tests]
    E --> F{Review and CI pass?}
    F -->|No| G[Revise the branch]
    F -->|Yes| H[Maintainer merges]
    H --> I[Reviewed main revision]
    I --> J[Site deployment]
    I --> K[Maintainer-created release tag]
    K --> L[Protected release approval]
```

Testing contributor code and publishing trusted artifacts are different
privilege levels. Secrets and write credentials never need to cross backward
into the untrusted pull-request job.
