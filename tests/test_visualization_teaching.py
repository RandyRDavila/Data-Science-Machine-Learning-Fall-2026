"""Contracts for Lecture 3's visualization and simulation studio."""

import ast
import tomllib
from pathlib import Path

import nbformat

PROJECT_ROOT = Path(__file__).parents[1]
NOTEBOOK_PATH = (
    PROJECT_ROOT
    / "notebooks"
    / "lecture-03-packages-numpy-pandas"
    / "04-visualization-and-simulation.ipynb"
)


def notebook() -> nbformat.NotebookNode:
    """Load the visualization and simulation notebook."""

    return nbformat.read(NOTEBOOK_PATH, as_version=4)


def notebook_trees() -> list[ast.Module]:
    """Parse every code cell independently."""

    return [
        ast.parse(cell.source)
        for cell in notebook().cells
        if cell.cell_type == "code"
    ]


def narrative() -> str:
    """Return normalized lowercase prose for conceptual assertions."""

    markdown = "\n".join(
        cell.source for cell in notebook().cells if cell.cell_type == "markdown"
    )
    return " ".join(markdown.lower().split())


def code_text() -> str:
    """Return all code cells as one searchable string."""

    return "\n".join(
        cell.source for cell in notebook().cells if cell.cell_type == "code"
    )


def test_visualization_stack_is_declared_and_locked() -> None:
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)

    declared = project["project"]["dependencies"]
    for package in ("matplotlib", "seaborn", "plotly"):
        assert any(requirement.startswith(f"{package}>=") for requirement in declared)

    lock_text = (PROJECT_ROOT / "uv.lock").read_text(encoding="utf-8")
    for package in ("matplotlib", "seaborn", "plotly"):
        assert f'name = "{package}"' in lock_text


def test_notebook_is_a_broad_long_form_visualization_studio() -> None:
    lesson = notebook()
    markdown_count = sum(cell.cell_type == "markdown" for cell in lesson.cells)
    code_count = sum(cell.cell_type == "code" for cell in lesson.cells)

    assert len(lesson.cells) >= 120
    assert markdown_count >= 75
    assert code_count >= 35
    assert lesson.metadata.rice_dsm.estimated_core_minutes >= 150
    assert lesson.metadata.rice_dsm.practice_minutes >= 100


def test_notebook_teaches_visual_reasoning_before_chart_syntax() -> None:
    lesson = narrative()

    for concept in (
        "question → analytical unit → data transformation",
        "marks",
        "encodings",
        "scales",
        "guides",
        "facets",
        "exploratory",
        "diagnostic",
        "explanatory",
        "operational",
        "do not confuse visual salience with scientific importance",
    ):
        assert concept in lesson


def test_notebook_covers_major_static_statistical_and_interactive_apis() -> None:
    source = code_text()

    for example in (
        "plt.subplots(",
        "plt.subplot_mosaic(",
        ".scatter(",
        ".fill_between(",
        ".errorbar(",
        ".hist(",
        ".step(",
        ".loglog(",
        "sns.scatterplot(",
        "sns.relplot(",
        "sns.kdeplot(",
        "sns.ecdfplot(",
        "sns.boxplot(",
        "sns.violinplot(",
        "sns.regplot(",
        "sns.heatmap(",
        ".plot(marker=",
        "px.line(",
        "px.scatter(",
        ".write_html(",
    ):
        assert example in source


def test_notebook_names_uncertainty_and_visual_failure_modes() -> None:
    lesson = narrative()

    for concept in (
        "standard deviation, standard error, confidence intervals",
        "unit of replication",
        "histogram bin choices",
        "kernel density",
        "truncated bar-axis",
        "dual y-axes",
        "overplotting",
        "rainbow maps",
        "model output as observed truth",
        "shared scales",
    ):
        assert concept in lesson


def test_notebook_treats_accessibility_and_export_as_contracts() -> None:
    lesson = narrative()
    source = code_text()

    for concept in (
        "accessibility is part of correctness",
        "do not encode a critical distinction with color alone",
        "text alternative",
        "grayscale",
        "svg/pdf",
        "self-contained plotly html",
        "network dependency",
    ):
        assert concept in lesson

    for export in (
        'savefig(png_path, dpi=180',
        "savefig(svg_path",
        "savefig(pdf_path",
        "TemporaryDirectory()",
        "include_plotlyjs=True",
    ):
        assert export in source


def test_notebook_contains_deterministic_scientific_simulations() -> None:
    lesson = narrative()
    source = code_text()

    for studio in (
        "heat diffusion",
        "random walks",
        "monte carlo convergence",
        "central limit effect",
        "nonlinear dynamics",
        "bifurcation diagram",
    ):
        assert studio in lesson

    for seed in ("seed=438", "seed=577"):
        assert seed in source
    assert "np.random.default_rng(" in source
    assert "np.random.seed(" not in source


def test_reusable_functions_are_documented_annotated_and_validated() -> None:
    functions = {
        node.name: node
        for tree in notebook_trees()
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }

    for name in (
        "simulate_heat_diffusion",
        "logistic_trajectory",
        "plot_temperature_profiles",
    ):
        function = functions[name]
        docstring = ast.get_docstring(function)
        parameters = [*function.args.args, *function.args.kwonlyargs]

        assert docstring is not None
        assert "Parameters\n----------" in docstring
        assert "Returns\n-------" in docstring
        assert "Raises\n------" in docstring
        assert all(parameter.annotation is not None for parameter in parameters)
        assert function.returns is not None


def test_plotting_examples_close_figures_and_avoid_network_data() -> None:
    source = code_text()

    assert source.count("plt.close(") >= 20
    assert "sns.load_dataset(" not in source
    assert "requests." not in source
    assert "http" not in source


def test_notebook_contains_no_personal_paths() -> None:
    complete_text = "\n".join(cell.source for cell in notebook().cells)

    assert "/Users/" not in complete_text
    assert "C:\\Users\\" not in complete_text
