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
