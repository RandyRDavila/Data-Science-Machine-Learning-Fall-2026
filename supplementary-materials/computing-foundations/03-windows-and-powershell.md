# Windows and PowerShell

Windows students can complete the course using PowerShell. The course commands
using `uv`, Python, Jupyter, pytest, and Ruff are the same after the project is
installed; filesystem navigation is where differences are most visible.

## Opening PowerShell in the right folder

Choose one of these approaches:

1. Open the repository in File Explorer, click the address bar, type
   `powershell`, and press Enter.
2. In VS Code, open the repository with **File → Open Folder**, then select
   **Terminal → New Terminal**.
3. Open PowerShell normally and navigate with `cd`.

Confirm the location:

```powershell
Get-Location
Get-ChildItem
```

You should see `README.md`, `pyproject.toml`, and `uv.lock`.

## Paths in PowerShell

PowerShell commonly displays paths with backslashes:

```powershell
cd C:\Users\student\courses\Data-Science-Machine-Learning-Fall-2026
```

Use quotes when a path contains spaces:

```powershell
cd "C:\Users\student\My Courses\Data Science"
```

PowerShell is usually case-insensitive for Windows paths, while Python package
and Git behavior may still expose case mistakes. Match repository spelling.

## Installing and checking `uv`

Use one of the Windows methods in the official
[`uv` installation guide](https://docs.astral.sh/uv/getting-started/installation/).
For example, students who already use Windows Package Manager can run:

```powershell
winget install --id=astral-sh.uv -e
```

Close and reopen the terminal after installation, then check:

```powershell
uv --version
```

## Course startup

From the repository root:

```powershell
uv run python scripts/setup_course.py
```

You do not need to activate `.venv` manually when using `uv run`. Return to VS
Code, open a course notebook, and select the **Rice DSM** kernel.

## Common Windows issues

### “uv is not recognized”

Close and reopen PowerShell. If the problem remains, confirm the installation
method completed and consult the official installation guide's PATH guidance.

### A command works in one terminal but not another

The terminals may have different environment settings or may be in different
folders. Run `Get-Location`, `uv --version`, and `uv run python --version` in
the terminal that fails.

### OneDrive or network folders

Synchronization, permissions, and very long paths can interfere with developer
tools. If unexplained file-locking problems occur, place the repository in a
short local path such as `C:\Users\student\courses\`.

### PowerShell execution-policy messages

Do not change security settings blindly. Record the exact message and ask for
help. The `winget` installation method may avoid running a downloaded installer
script directly.
