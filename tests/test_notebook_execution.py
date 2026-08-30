"""Execute course notebooks exactly as a student kernel would."""

from pathlib import Path

import nbformat
import pytest
from nbclient import NotebookClient

PROJECT_ROOT = Path(__file__).parents[1]
NOTEBOOKS = sorted((PROJECT_ROOT / "notebooks").glob("lecture-*/*.ipynb"))


@pytest.mark.parametrize("notebook_path", NOTEBOOKS, ids=lambda path: path.name)
def test_notebook_executes_from_top_to_bottom(
    notebook_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Catch stale imports, missing names, bad paths, and out-of-order assumptions."""

    # The testing lesson demonstrates a nested pytest command. Skip only that
    # nested command here so this test cannot recursively execute itself.
    monkeypatch.setenv("RICE_DSM_RUNNING_NOTEBOOK_TESTS", "1")
    notebook = nbformat.read(notebook_path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=120,
        kernel_name="rice-dsm",
        resources={"metadata": {"path": str(PROJECT_ROOT)}},
    )

    client.execute()
