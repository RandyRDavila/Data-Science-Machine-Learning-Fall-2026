# VS Code and Jupyter

VS Code is an editor and project workspace. Jupyter is an interactive notebook
system. VS Code can display and run Jupyter notebooks, but the two tools are not
the same.

## Open the folder, not an isolated file

In VS Code, select **File → Open Folder** and choose the repository root. The
Explorer should show `README.md`, `notebooks/`, `src/`, and `tests/` together.

Opening only one notebook can hide project context and make imports or terminals
start in an unexpected location.

## Recommended extensions

Install Microsoft's **Python** and **Jupyter** extensions from the VS Code
Extensions view. Students should verify the publisher rather than choosing a
similarly named third-party extension.

The repository includes workspace recommendations for these two extensions, so
VS Code should offer to install them when the course folder first opens.

## The integrated terminal

Select **Terminal → New Terminal**. It should open at the repository root. Check
with `pwd` and `ls`, then prepare the project:

```text
uv run python scripts/setup_course.py
```

This single command creates or updates `.venv`, installs the locked tools,
verifies the course package, and registers the **Rice DSM** kernel. It exits when
setup is complete; editing and navigation remain inside VS Code.

The terminal is a real shell embedded in VS Code. Commands behave the same as in
a separate terminal application.

## Opening a notebook

Navigate to `notebooks/lecture-01-python-foundations/` and open the first
`.ipynb` file. A notebook contains:

- Markdown cells for explanation;
- code cells sent to a Python kernel;
- outputs produced by executed code; and
- hidden metadata describing the notebook format and preferred kernel.

Use the kernel picker near the notebook's upper-right corner to select
**Rice DSM**. That kernelspec launches the Python interpreter inside this
repository's `.venv`. The exact interface may change, so consult the official
[VS Code kernel-selection guide](https://code.visualstudio.com/docs/datascience/jupyter-kernel-management)
if the environment is not listed.

## Cell execution order

The kernel retains variables until it is restarted. This means cells can appear
to work only because an earlier cell ran out of order.

Before considering a notebook complete:

1. restart the kernel;
2. run all cells from top to bottom; and
3. confirm that no cell depends on hidden prior state.

## When imports fail

Run this inside the notebook:

```python
import sys

print(sys.executable)
print(sys.prefix)
```

`sys.prefix` should point to this repository's `.venv`. `sys.executable` may
instead display uv's underlying managed Python when the executable is a symbolic
link; that is normal. If `sys.prefix` is not the project environment, select the
**Rice DSM** kernel rather than installing the package into an unrelated Python.
