"""Generate the reproducible figures for the opening Part II chapters.

The figures deliberately read the repository's SQLite database rather than a
library convenience loader.  This keeps the textbook graphics on the same
data path that students inspect in the executable lecture companions.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.patches import Circle
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import confusion_matrix, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.svm import SVC

ROOT = Path(__file__).resolve().parents[2]
DATABASE = ROOT / "data" / "course_datasets.sqlite"
OUTPUT = Path(__file__).resolve().parent / "generated"

RICE_BLUE = "#00205B"
RICE_LIGHT_BLUE = "#A7C6DA"
RICE_GOLD = "#C9961A"
RICE_GREEN = "#2B7A4B"
RICE_RED = "#A33A32"
RICE_GRAY = "#5E6A71"


def configure_style() -> None:
    """Apply one restrained visual language to every textbook figure."""

    plt.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 220,
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.titleweight": "bold",
            "axes.labelsize": 9.5,
            "axes.edgecolor": "#CAD1D8",
            "axes.linewidth": 0.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.color": "#DDE3E8",
            "grid.linewidth": 0.6,
            "grid.alpha": 0.75,
            "legend.frameon": False,
            "pdf.fonttype": 42,
        }
    )


def load_tables() -> dict[str, pd.DataFrame]:
    """Load only the documented tables used by the figures."""

    if not DATABASE.is_file():
        raise FileNotFoundError(
            f"Missing {DATABASE}. Rebuild it with scripts/build_course_database.py."
        )
    with sqlite3.connect(DATABASE) as connection:
        return {
            "diabetes": pd.read_sql_query(
                "SELECT * FROM diabetes_observations ORDER BY observation_id",
                connection,
            ),
            "cancer": pd.read_sql_query(
                "SELECT * FROM breast_cancer_observations ORDER BY observation_id",
                connection,
            ),
            "wine": pd.read_sql_query(
                "SELECT * FROM wine_observations ORDER BY observation_id",
                connection,
            ),
            "digits": pd.read_sql_query(
                "SELECT * FROM digits_observations ORDER BY observation_id",
                connection,
            ),
        }


def panel_label(ax: Axes, label: str) -> None:
    """Place a consistent panel label just outside an axes."""

    ax.text(
        -0.12,
        1.04,
        label,
        transform=ax.transAxes,
        color=RICE_BLUE,
        fontsize=12,
        fontweight="bold",
    )


def save_figure(fig: plt.Figure, stem: str) -> None:
    """Save vector PDF for print and PNG for quick browser inspection."""

    OUTPUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(OUTPUT / f"{stem}.png", bbox_inches="tight")
    plt.close(fig)


def logistic_single_neuron_contract() -> None:
    """Connect logistic probability notation to single-neuron notation."""

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(11.6, 3.7),
        constrained_layout=True,
        gridspec_kw={"width_ratios": [1.35, 1.0]},
    )

    ax = axes[0]
    ax.set_xlim(0.0, 10.0)
    ax.set_ylim(0.0, 6.0)
    ax.axis("off")

    input_y = (4.8, 3.7, 2.6, 1.5)
    for index, y_position in enumerate(input_y, start=1):
        ax.add_patch(
            Circle(
                (0.9, y_position),
                0.34,
                facecolor=RICE_LIGHT_BLUE,
                edgecolor=RICE_BLUE,
                linewidth=1.4,
            )
        )
        ax.text(0.9, y_position, f"$x_{index}$", ha="center", va="center")
        ax.annotate(
            "",
            xy=(3.2, 3.15),
            xytext=(1.28, y_position),
            arrowprops={"arrowstyle": "->", "color": RICE_GRAY, "lw": 1.0},
        )

    ax.text(
        3.8,
        3.15,
        "$z=\\mathbf{w}^T\\mathbf{x}+b$",
        ha="center",
        va="center",
        fontsize=11,
        bbox={
            "boxstyle": "round,pad=0.55",
            "facecolor": "#F4F7FA",
            "edgecolor": RICE_BLUE,
            "linewidth": 1.5,
        },
    )
    ax.text(
        3.8,
        2.25,
        "preactivation / logit",
        ha="center",
        color=RICE_GRAY,
        fontsize=8.5,
    )
    ax.annotate(
        "",
        xy=(6.1, 3.15),
        xytext=(4.95, 3.15),
        arrowprops={"arrowstyle": "->", "color": RICE_GOLD, "lw": 1.8},
    )
    ax.text(
        6.9,
        3.15,
        "$a=\\sigma(z)=p$",
        ha="center",
        va="center",
        fontsize=11,
        bbox={
            "boxstyle": "round,pad=0.55",
            "facecolor": "#FFF8E7",
            "edgecolor": RICE_GOLD,
            "linewidth": 1.5,
        },
    )
    ax.text(
        6.9,
        2.25,
        "postactivation / event probability",
        ha="center",
        color=RICE_GRAY,
        fontsize=8.5,
    )
    ax.annotate(
        "",
        xy=(9.05, 3.15),
        xytext=(7.85, 3.15),
        arrowprops={"arrowstyle": "->", "color": RICE_RED, "lw": 1.8},
    )
    ax.text(
        9.25,
        3.15,
        "$\\ell(p;y)$",
        ha="center",
        va="center",
        fontsize=11,
        bbox={
            "boxstyle": "round,pad=0.48",
            "facecolor": "#FBECEB",
            "edgecolor": RICE_RED,
            "linewidth": 1.5,
        },
    )
    ax.annotate(
        "$\\delta=\\partial\\ell/\\partial z=p-y$",
        xy=(3.9, 3.78),
        xytext=(7.0, 5.15),
        ha="center",
        color=RICE_RED,
        fontsize=9.3,
        arrowprops={
            "arrowstyle": "->",
            "connectionstyle": "arc3,rad=0.18",
            "color": RICE_RED,
            "lw": 1.4,
        },
    )
    ax.text(
        5.0,
        0.45,
        "Forward: compute a probability.   Backward: transmit a score derivative.",
        ha="center",
        fontsize=9.2,
        color=RICE_BLUE,
        fontweight="bold",
    )
    ax.set_title("One logistic neuron", pad=4)
    panel_label(ax, "A")

    ax = axes[1]
    ax.axis("off")
    contract_rows = (
        ("Target", "$y\\in\\{0,1\\}$"),
        ("Activation", "$\\sigma(z)$"),
        ("Output meaning", "$p=P(Y=1\\mid X=x)$"),
        ("Training loss", "Bernoulli log loss"),
        ("Score derivative", "$p-y$"),
        ("Decision", "separate threshold policy"),
    )
    y_position = 0.87
    for label, value in contract_rows:
        ax.text(
            0.03,
            y_position,
            label,
            transform=ax.transAxes,
            color=RICE_BLUE,
            fontweight="bold",
            fontsize=9.5,
            va="center",
        )
        ax.text(
            0.40,
            y_position,
            value,
            transform=ax.transAxes,
            color="#202830",
            fontsize=9.5,
            va="center",
        )
        ax.plot(
            [0.03, 0.97],
            [y_position - 0.065, y_position - 0.065],
            transform=ax.transAxes,
            color="#DDE3E8",
            linewidth=0.8,
        )
        y_position -= 0.135
    ax.text(
        0.03,
        0.015,
        "The affine calculation alone does not define the estimator.",
        transform=ax.transAxes,
        color=RICE_RED,
        fontsize=9.2,
        fontweight="bold",
    )
    ax.set_title("Statistical specification", pad=4)
    panel_label(ax, "B")

    save_figure(fig, "logistic-single-neuron")


def neural_network_anatomy() -> None:
    """Draw literal neurons before compressing them into matrix notation."""

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(10.8, 5.0),
        gridspec_kw={"width_ratios": [1.55, 1.0]},
        constrained_layout=True,
    )

    ax = axes[0]
    ax.grid(False)
    layer_x = [0.0, 1.45, 2.9]
    input_y = np.array([2.5, 1.5, 0.5])
    hidden_y = np.array([2.65, 1.78, 0.92, 0.05])
    output_y = np.array([2.05, 0.75])

    for source_y in input_y:
        for target_y in hidden_y:
            ax.plot(
                [layer_x[0] + 0.15, layer_x[1] - 0.22],
                [source_y, target_y],
                color=RICE_LIGHT_BLUE,
                linewidth=0.8,
                alpha=0.7,
                zorder=0,
            )
    for source_y in hidden_y:
        for target_y in output_y:
            ax.plot(
                [layer_x[1] + 0.22, layer_x[2] - 0.22],
                [source_y, target_y],
                color="#AAB3BB",
                linewidth=0.9,
                alpha=0.72,
                zorder=0,
            )

    for index, y_value in enumerate(input_y, start=1):
        circle = Circle(
            (layer_x[0], y_value),
            0.18,
            facecolor=RICE_BLUE,
            edgecolor="white",
            linewidth=1.2,
            zorder=2,
        )
        ax.add_patch(circle)
        ax.text(
            layer_x[0],
            y_value,
            rf"$x_{index}$",
            color="white",
            ha="center",
            va="center",
            fontweight="bold",
        )

    def draw_neuron(x_value: float, y_value: float, layer: int, index: int) -> None:
        circle = Circle(
            (x_value, y_value),
            0.24,
            facecolor="#F7F9FB",
            edgecolor=RICE_BLUE,
            linewidth=1.6,
            zorder=2,
        )
        ax.add_patch(circle)
        ax.plot(
            [x_value, x_value],
            [y_value - 0.22, y_value + 0.22],
            color=RICE_BLUE,
            linewidth=1.0,
            zorder=3,
        )
        ax.text(
            x_value - 0.105,
            y_value,
            rf"$z_{{{index}}}^{{{layer}}}$",
            color=RICE_RED,
            ha="center",
            va="center",
            fontsize=8.2,
            zorder=4,
        )
        ax.text(
            x_value + 0.105,
            y_value,
            rf"$a_{{{index}}}^{{{layer}}}$",
            color=RICE_GREEN,
            ha="center",
            va="center",
            fontsize=8.2,
            zorder=4,
        )

    for index, y_value in enumerate(hidden_y, start=1):
        draw_neuron(layer_x[1], y_value, 1, index)
    for index, y_value in enumerate(output_y, start=1):
        draw_neuron(layer_x[2], y_value, 2, index)

    for x_value, label, subtitle in zip(
        layer_x,
        ("input", "hidden layer", "output layer"),
        (r"$a^0=x$", r"$a^1=\phi^1(z^1)$", r"$a^2=\phi^2(z^2)$"),
        strict=True,
    ):
        ax.text(
            x_value,
            3.12,
            label,
            color=RICE_BLUE,
            ha="center",
            fontweight="bold",
        )
        ax.text(x_value, 2.91, subtitle, color=RICE_GRAY, ha="center", fontsize=8.5)

    ax.text(
        1.45,
        -0.38,
        r"each circle preserves $z_j^\ell\rightarrow a_j^\ell$",
        ha="center",
        color=RICE_GRAY,
        fontsize=8.7,
    )
    ax.set(
        xlim=(-0.45, 3.35),
        ylim=(-0.55, 3.42),
        title="A network is a graph of individual neurons",
    )
    ax.axis("off")
    panel_label(ax, "A")

    ax = axes[1]
    ax.grid(False)
    ax.set(xlim=(-1.25, 1.35), ylim=(-1.25, 1.25))
    labels = (r"$a_1^{\ell-1}$", r"$a_2^{\ell-1}$", r"$a_k^{\ell-1}$")
    for y_value, label in zip((0.72, 0.0, -0.72), labels, strict=True):
        ax.plot([-1.05, -0.28], [y_value, 0.0], color=RICE_LIGHT_BLUE, linewidth=1.7)
        ax.text(-1.1, y_value, label, ha="right", va="center", fontsize=9)
    closeup = Circle(
        (0.0, 0.0),
        0.42,
        facecolor="#F7F9FB",
        edgecolor=RICE_BLUE,
        linewidth=2.0,
    )
    ax.add_patch(closeup)
    ax.plot([0.0, 0.0], [-0.39, 0.39], color=RICE_BLUE, linewidth=1.2)
    ax.text(
        -0.2,
        0.0,
        r"$z_j^\ell$",
        color=RICE_RED,
        ha="center",
        va="center",
        fontsize=12,
    )
    ax.text(
        0.2,
        0.0,
        r"$a_j^\ell$",
        color=RICE_GREEN,
        ha="center",
        va="center",
        fontsize=12,
    )
    ax.annotate(
        "",
        xy=(1.08, 0),
        xytext=(0.44, 0),
        arrowprops={"arrowstyle": "->", "color": RICE_GREEN, "lw": 2},
    )
    ax.text(
        0.75,
        0.16,
        r"$a_j^\ell=\phi^\ell(z_j^\ell)$",
        ha="center",
        color=RICE_GREEN,
        fontsize=9,
    )
    ax.text(
        0.0,
        -0.7,
        r"$z_j^\ell=\sum_k w_{j,k}^\ell a_k^{\ell-1}+b_j^\ell$",
        ha="center",
        color=RICE_RED,
        fontsize=9,
    )
    ax.text(
        0.0,
        -1.02,
        "affine aggregation, then nonlinear transformation",
        ha="center",
        color=RICE_GRAY,
        fontsize=8.5,
    )
    ax.set_title("The two stages inside one neuron")
    ax.axis("off")
    panel_label(ax, "B")

    save_figure(fig, "neural-network-anatomy")


def svm_hyperplane_geometry() -> None:
    """Derive distance, scale invariance, and canonical margin geometry."""

    weights = np.array([2.0, -1.0])
    bias = -1.0
    weight_norm = np.linalg.norm(weights)
    query = np.array([2.0, 1.5])
    query_score = float(query @ weights + bias)
    projection = query - query_score / (weights @ weights) * weights
    horizontal = np.linspace(-0.45, 2.75, 350)

    fig, axes = plt.subplots(1, 3, figsize=(11.4, 3.8), constrained_layout=True)

    ax = axes[0]
    boundary = (weights[0] * horizontal + bias) / (-weights[1])
    ax.plot(horizontal, boundary, color=RICE_BLUE, linewidth=2.5, label="$z=0$")
    ax.scatter(*query, color=RICE_RED, s=48, zorder=4, label="point $q$")
    ax.scatter(
        *projection,
        color=RICE_GREEN,
        s=48,
        zorder=4,
        label="projection $q_H$",
    )
    ax.plot(
        [query[0], projection[0]],
        [query[1], projection[1]],
        color=RICE_RED,
        linestyle="--",
        linewidth=2,
    )
    normal_origin = np.array([1.0, 1.0])
    ax.annotate(
        "",
        xy=normal_origin + 0.58 * weights,
        xytext=normal_origin,
        arrowprops={"arrowstyle": "->", "lw": 2.1, "color": RICE_GOLD},
    )
    ax.text(
        *(normal_origin + 0.60 * weights),
        "$w$",
        color=RICE_GOLD,
        fontsize=10,
    )
    ax.text(
        1.32,
        0.88,
        f"$|z(q)|/\\|w\\|={abs(query_score) / weight_norm:.3f}$",
        fontsize=7.5,
        bbox={"facecolor": "white", "alpha": 0.9, "edgecolor": "none"},
    )
    ax.set(
        title="Normal projection",
        xlabel="$x_1$",
        ylabel="$x_2$",
        xlim=(-0.45, 2.8),
        ylim=(-1.9, 4.0),
        aspect="equal",
    )
    ax.legend(fontsize=6.8, loc="lower right")
    panel_label(ax, "A")

    ax = axes[1]
    scales = np.array([0.5, 1.0, 2.0, 4.0])
    functional = scales * query_score
    geometric = functional / (scales * weight_norm)
    ax.plot(
        scales,
        functional,
        "o-",
        color=RICE_BLUE,
        linewidth=2.4,
        label="$y(cz)$: functional",
    )
    ax.plot(
        scales,
        geometric,
        "s--",
        color=RICE_RED,
        linewidth=2.2,
        label="$y(cz)/\\|cw\\|$: geometric",
    )
    ax.set(
        title="Scale invariance",
        xlabel="positive parameter scale $c$",
        ylabel="margin for the same point",
        xticks=scales,
    )
    ax.legend(fontsize=7.1)
    panel_label(ax, "B")

    ax = axes[2]
    toy_points = np.array(
        [
            [0.5, 1.0],
            [0.0, 0.5],
            [0.2, 1.2],
            [1.5, 1.0],
            [2.2, 1.3],
            [1.6, 0.5],
        ]
    )
    toy_labels = np.array([-1, -1, -1, 1, 1, 1])
    for label, color, name in (
        (-1, RICE_BLUE, "class $-1$"),
        (1, RICE_RED, "class $+1$"),
    ):
        mask = toy_labels == label
        ax.scatter(
            toy_points[mask, 0],
            toy_points[mask, 1],
            s=45,
            color=color,
            label=name,
            zorder=4,
        )
    functional_margins = toy_labels * (toy_points @ weights + bias)
    support_points = toy_points[np.isclose(functional_margins, 1.0)]
    ax.scatter(
        support_points[:, 0],
        support_points[:, 1],
        s=92,
        facecolors="none",
        edgecolors=RICE_GOLD,
        linewidths=1.8,
        label="support vector",
        zorder=5,
    )
    for level, style, line_width in (
        (-1.0, "--", 1.4),
        (0.0, "-", 2.4),
        (1.0, "--", 1.4),
    ):
        vertical = (level - bias - weights[0] * horizontal) / weights[1]
        ax.plot(
            horizontal,
            vertical,
            style,
            color=RICE_GRAY if level else RICE_BLUE,
            linewidth=line_width,
            label=f"$z={level:g}$",
        )
    boundary_point = np.array([1.25, 1.5])
    unit_normal = weights / weight_norm
    negative_edge = boundary_point - unit_normal / weight_norm
    positive_edge = boundary_point + unit_normal / weight_norm
    ax.annotate(
        "",
        xy=positive_edge,
        xytext=negative_edge,
        arrowprops={"arrowstyle": "<->", "lw": 2.1, "color": RICE_GREEN},
    )
    ax.text(
        1.02,
        1.86,
        "$2/\\|w\\|$",
        color=RICE_GREEN,
        fontsize=8,
        rotation=0,
    )
    ax.set(
        title="Canonical margin",
        xlabel="$x_1$",
        ylabel="$x_2$",
        xlim=(-0.45, 2.75),
        ylim=(-1.9, 4.0),
        aspect="equal",
    )
    ax.legend(fontsize=6.3, ncols=2, loc="lower right")
    panel_label(ax, "C")

    fig.suptitle(
        "Hyperplane geometry follows from one affine score",
        color=RICE_BLUE,
        fontsize=12,
        fontweight="bold",
    )
    save_figure(fig, "svm-hyperplane-geometry")


def linear_svm_geometry(tables: dict[str, pd.DataFrame]) -> None:
    """Show margin geometry, competing losses, and regularization tradeoffs."""

    cancer = tables["cancer"]
    features = cancer[["mean_radius", "mean_texture"]].to_numpy()
    target = cancer["diagnosis_code"].to_numpy()
    scaler = StandardScaler()
    standardized = scaler.fit_transform(features)
    classifier = SVC(kernel="linear", C=1.0).fit(standardized, target)

    fig, axes = plt.subplots(1, 3, figsize=(11.4, 3.8), constrained_layout=True)

    ax = axes[0]
    horizontal = np.linspace(
        standardized[:, 0].min() - 0.4,
        standardized[:, 0].max() + 0.4,
        260,
    )
    vertical = np.linspace(
        standardized[:, 1].min() - 0.4,
        standardized[:, 1].max() + 0.4,
        260,
    )
    grid_x, grid_y = np.meshgrid(horizontal, vertical)
    grid = np.column_stack([grid_x.ravel(), grid_y.ravel()])
    score = classifier.decision_function(grid).reshape(grid_x.shape)
    ax.contourf(
        grid_x,
        grid_y,
        score,
        levels=[-10, 0, 10],
        colors=[RICE_LIGHT_BLUE, "#F2DDD9"],
        alpha=0.34,
    )
    contours = ax.contour(
        grid_x,
        grid_y,
        score,
        levels=[-1, 0, 1],
        colors=[RICE_BLUE, RICE_RED, RICE_BLUE],
        linestyles=["--", "-", "--"],
        linewidths=[1.4, 2.2, 1.4],
    )
    ax.clabel(contours, fmt={-1: "$z=-1$", 0: "$z=0$", 1: "$z=1$"}, fontsize=7)
    for label, color, name in ((0, RICE_BLUE, "class 0"), (1, RICE_RED, "class 1")):
        mask = target == label
        ax.scatter(
            standardized[mask, 0],
            standardized[mask, 1],
            s=16,
            color=color,
            alpha=0.45,
            edgecolors="none",
            label=name,
        )
    support = classifier.support_vectors_
    ax.scatter(
        support[:, 0],
        support[:, 1],
        s=58,
        facecolors="none",
        edgecolors=RICE_GOLD,
        linewidths=1.2,
        label="support vector",
    )
    ax.set(
        title="Boundary and unit margins",
        xlabel="standardized mean radius",
        ylabel="standardized mean texture",
    )
    ax.legend(fontsize=6.8, loc="upper left")
    panel_label(ax, "A")

    ax = axes[1]
    signed_margin = np.linspace(-2.0, 2.5, 600)
    ax.axvspan(-2.0, 0.0, color=RICE_RED, alpha=0.10, label="misclassified")
    ax.axvspan(
        0.0,
        1.0,
        color=RICE_GOLD,
        alpha=0.14,
        label="correct, inside margin",
    )
    ax.axvspan(
        1.0,
        2.5,
        color=RICE_GREEN,
        alpha=0.10,
        label="correct, beyond margin",
    )
    ax.plot(
        signed_margin,
        np.maximum(0.0, 1.0 - signed_margin),
        color=RICE_BLUE,
        linewidth=2.7,
        label="hinge loss = minimum slack",
    )
    ax.axvline(0.0, color=RICE_GRAY, linestyle=":", linewidth=1.1)
    ax.axvline(1.0, color=RICE_GREEN, linestyle="--", linewidth=1.1)
    ax.set(
        title="Hinge loss measures margin violation",
        xlabel="signed margin $yz$",
        ylabel="hinge loss / slack",
        ylim=(-0.04, 3.2),
    )
    ax.legend(fontsize=6.8)
    panel_label(ax, "B")

    ax = axes[2]
    penalties = np.logspace(-2, 2, 24)
    margin_widths = []
    support_counts = []
    for penalty in penalties:
        candidate = SVC(kernel="linear", C=penalty).fit(standardized, target)
        margin_widths.append(2.0 / np.linalg.norm(candidate.coef_[0]))
        support_counts.append(candidate.support_.size)
    width_line = ax.semilogx(
        penalties,
        margin_widths,
        color=RICE_BLUE,
        linewidth=2.4,
        label="geometric margin width",
    )[0]
    ax.set(
        title="Changing penalty $C$",
        xlabel="penalty $C$ (log scale)",
        ylabel="margin width",
    )
    support_axis = ax.twinx()
    count_line = support_axis.semilogx(
        penalties,
        support_counts,
        color=RICE_RED,
        linewidth=2.0,
        linestyle="--",
        label="support-vector count",
    )[0]
    support_axis.set_ylabel("support-vector count", color=RICE_RED)
    support_axis.grid(False)
    ax.legend(handles=[width_line, count_line], fontsize=6.8, loc="center right")
    panel_label(ax, "C")

    fig.suptitle(
        "A linear SVM learns an affine score by a maximum-margin objective",
        color=RICE_BLUE,
        fontsize=12,
        fontweight="bold",
    )
    save_figure(fig, "linear-svm-margin")


def neural_composition_expressivity() -> None:
    """Contrast affine collapse with nonlinear width and depth."""

    fig, axes = plt.subplots(1, 3, figsize=(11.4, 3.8), constrained_layout=True)

    ax = axes[0]
    x = np.linspace(-1.0, 1.0, 500)
    first = 0.85 * x + 0.18
    second = -1.05 * first + 0.12
    third = 0.72 * second - 0.08
    ax.plot(x, first, color=RICE_LIGHT_BLUE, linewidth=1.8, label="layer 1")
    ax.plot(x, second, color=RICE_GOLD, linewidth=1.8, label="layer 2 composition")
    ax.plot(x, third, color=RICE_BLUE, linewidth=2.6, label="layer 3 composition")
    ax.set(title="Affine depth collapses", xlabel="$x$", ylabel="output")
    ax.legend(fontsize=7.3)
    panel_label(ax, "A")

    ax = axes[1]

    def relu(values: np.ndarray) -> np.ndarray:
        return np.maximum(values, 0.0)

    hinges = (
        0.75 * relu(x + 0.68),
        -1.55 * relu(x + 0.18),
        1.35 * relu(x - 0.38),
    )
    combined = 0.15 + sum(hinges)
    colors = (RICE_LIGHT_BLUE, RICE_GOLD, RICE_GREEN)
    for hinge, color in zip(hinges, colors, strict=True):
        ax.plot(x, hinge, color=color, linewidth=1.25, alpha=0.8)
    bends = np.array([-0.68, -0.18, 0.38])
    ax.plot(x, combined, color=RICE_BLUE, linewidth=2.8, label="weighted features")
    ax.scatter(
        bends,
        np.interp(bends, x, combined),
        color=RICE_RED,
        s=22,
        zorder=3,
        label="learned bends",
    )
    ax.set(title="Width combines nonlinear features", xlabel="$x$", ylabel="output")
    ax.legend(fontsize=7.2)
    panel_label(ax, "B")

    ax = axes[2]
    unit_interval = np.linspace(0.0, 1.0, 1001)

    def tent(values: np.ndarray) -> np.ndarray:
        return (
            2.0 * relu(values)
            - 4.0 * relu(values - 0.5)
            + 2.0 * relu(values - 1.0)
        )

    current = unit_interval.copy()
    offsets = (2.3, 1.15, 0.0)
    depth_colors = (RICE_LIGHT_BLUE, RICE_GOLD, RICE_BLUE)
    for depth, (offset, color) in enumerate(
        zip(offsets, depth_colors, strict=True), start=1
    ):
        current = tent(current)
        ax.plot(unit_interval, current + offset, color=color, linewidth=2.0)
        ax.text(
            1.02,
            offset + 0.5,
            rf"$T^{{\circ {depth}}}$",
            color=color,
            va="center",
            fontsize=8.5,
        )
    ax.set(
        title="Depth composes reusable features",
        xlabel="$x$",
        ylabel="vertically offset output",
        xlim=(0, 1.13),
        yticks=[],
    )
    panel_label(ax, "C")

    fig.suptitle(
        "Nonlinearity lets networks learn bends, regions, and representations",
        color=RICE_BLUE,
        fontsize=13,
        fontweight="bold",
    )
    save_figure(fig, "neural-composition-expressivity")


def learning_landscape(tables: dict[str, pd.DataFrame]) -> None:
    """Show that different learning structures answer different questions."""

    diabetes = tables["diabetes"]
    cancer = tables["cancer"]
    wine = tables["wine"]
    digits = tables["digits"]

    fig, axes = plt.subplots(2, 2, figsize=(10.4, 7.2), constrained_layout=True)

    ax = axes[0, 0]
    x = diabetes[["bmi"]].to_numpy()
    y = diabetes["disease_progression"].to_numpy()
    regression = LinearRegression().fit(x, y)
    grid = np.linspace(x.min(), x.max(), 200).reshape(-1, 1)
    ax.scatter(x, y, s=12, alpha=0.38, color=RICE_LIGHT_BLUE, edgecolors="none")
    ax.plot(grid, regression.predict(grid), color=RICE_BLUE, linewidth=2.4)
    ax.set(
        title="Supervised regression",
        xlabel="baseline BMI",
        ylabel="one-year progression score",
    )
    panel_label(ax, "A")

    ax = axes[0, 1]
    labels = cancer["diagnosis_label"].astype(str)
    for label, color in zip(
        sorted(labels.unique()), (RICE_GREEN, RICE_RED), strict=True
    ):
        mask = labels == label
        ax.scatter(
            cancer.loc[mask, "mean_radius"],
            cancer.loc[mask, "mean_texture"],
            s=14,
            alpha=0.48,
            color=color,
            label=label,
            edgecolors="none",
        )
    ax.set(
        title="Supervised classification",
        xlabel="mean radius",
        ylabel="mean texture",
    )
    ax.legend(title="observed diagnosis", fontsize=8)
    panel_label(ax, "B")

    ax = axes[1, 0]
    wine_features = wine.drop(
        columns=["observation_id", "cultivar_code", "cultivar_label"]
    )
    standardized_wine = StandardScaler().fit_transform(wine_features)
    embedding = PCA(n_components=2, random_state=17).fit_transform(standardized_wine)
    clusters = KMeans(n_clusters=3, n_init=20, random_state=17).fit_predict(embedding)
    colors = np.array([RICE_BLUE, RICE_GOLD, RICE_GREEN])
    ax.scatter(
        embedding[:, 0],
        embedding[:, 1],
        c=colors[clusters],
        s=20,
        alpha=0.68,
        edgecolors="white",
        linewidths=0.25,
    )
    ax.set(
        title="Unsupervised clustering",
        xlabel="principal coordinate 1",
        ylabel="principal coordinate 2",
    )
    panel_label(ax, "C")

    ax = axes[1, 1]
    pixel_columns = [column for column in digits if column.startswith("pixel_")]
    digit_features = StandardScaler().fit_transform(digits[pixel_columns])
    digit_embedding = PCA(n_components=2, random_state=17).fit_transform(digit_features)
    selected = digits["digit_label"].isin([0, 1, 4, 7])
    palette = {0: RICE_BLUE, 1: RICE_GOLD, 4: RICE_GREEN, 7: RICE_RED}
    for digit, color in palette.items():
        mask = selected & (digits["digit_label"] == digit)
        ax.scatter(
            digit_embedding[mask, 0],
            digit_embedding[mask, 1],
            s=12,
            alpha=0.48,
            color=color,
            label=str(digit),
            edgecolors="none",
        )
    ax.set(
        title="Learned two-dimensional representation",
        xlabel="principal coordinate 1",
        ylabel="principal coordinate 2",
    )
    ax.legend(title="label (audit only)", ncols=4, fontsize=8)
    panel_label(ax, "D")

    save_figure(fig, "learning-landscape")


def supervised_evidence(tables: dict[str, pd.DataFrame]) -> None:
    """Visualize the split boundary and the cost of adaptive model complexity."""

    diabetes = tables["diabetes"]
    x = diabetes[["bmi"]].to_numpy()
    y = diabetes["disease_progression"].to_numpy()
    x_train, x_holdout, y_train, y_holdout = train_test_split(
        x, y, test_size=0.30, random_state=438
    )
    x_validation, x_test, y_validation, y_test = train_test_split(
        x_holdout, y_holdout, test_size=0.50, random_state=438
    )

    degrees = np.arange(1, 16)
    train_rmse: list[float] = []
    validation_rmse: list[float] = []
    for degree in degrees:
        model = make_pipeline(
            PolynomialFeatures(degree=degree, include_bias=False),
            StandardScaler(),
            LinearRegression(),
        )
        model.fit(x_train, y_train)
        train_rmse.append(np.sqrt(mean_squared_error(y_train, model.predict(x_train))))
        validation_rmse.append(
            np.sqrt(mean_squared_error(y_validation, model.predict(x_validation)))
        )

    chosen_degree = int(degrees[np.argmin(validation_rmse)])
    chosen = make_pipeline(
        PolynomialFeatures(degree=chosen_degree, include_bias=False),
        StandardScaler(),
        LinearRegression(),
    ).fit(x_train, y_train)
    baseline = np.full_like(y_test, y_train.mean(), dtype=float)
    candidate = chosen.predict(x_test)

    fig, axes = plt.subplots(1, 3, figsize=(11.4, 3.45), constrained_layout=True)

    ax = axes[0]
    ax.scatter(x_train, y_train, s=16, alpha=0.46, color=RICE_BLUE, label="training")
    ax.scatter(
        x_validation,
        y_validation,
        s=22,
        alpha=0.75,
        color=RICE_GOLD,
        label="validation",
    )
    ax.scatter(
        x_test,
        y_test,
        s=24,
        facecolors="none",
        edgecolors=RICE_RED,
        linewidths=0.8,
        label="test (sealed)",
    )
    ax.set(title="One dataset, three responsibilities", xlabel="BMI", ylabel="target")
    ax.legend(fontsize=7.5)
    panel_label(ax, "A")

    ax = axes[1]
    ax.plot(degrees, train_rmse, marker="o", color=RICE_BLUE, label="training")
    ax.plot(
        degrees,
        validation_rmse,
        marker="o",
        color=RICE_GOLD,
        label="validation",
    )
    ax.axvline(chosen_degree, color=RICE_GREEN, linestyle="--", linewidth=1.4)
    ax.set(
        title=f"Validation selects degree {chosen_degree}",
        xlabel="polynomial degree",
        ylabel="RMSE",
        xticks=[1, 4, 7, 10, 13, 15],
    )
    ax.legend(fontsize=8)
    panel_label(ax, "B")

    ax = axes[2]
    test_scores = [
        np.sqrt(mean_squared_error(y_test, baseline)),
        np.sqrt(mean_squared_error(y_test, candidate)),
    ]
    bars = ax.bar(
        ["training-mean\nbaseline", f"degree-{chosen_degree}\ncandidate"],
        test_scores,
        color=[RICE_GRAY, RICE_BLUE],
        width=0.62,
    )
    for bar, score in zip(bars, test_scores, strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            score + 0.8,
            f"{score:.1f}",
            ha="center",
            fontsize=9,
        )
    ax.set(
        title="Open the test set once",
        ylabel="test RMSE",
        ylim=(0, max(test_scores) * 1.18),
    )
    panel_label(ax, "C")

    save_figure(fig, "supervised-evidence")


def regression_geometry(tables: dict[str, pd.DataFrame]) -> None:
    """Connect data space, residual space, and parameter space for OLS."""

    diabetes = tables["diabetes"]
    x = diabetes["bmi"].to_numpy()
    centered_x = x - x.mean()
    y = diabetes["disease_progression"].to_numpy()
    design = np.column_stack([np.ones(len(centered_x)), centered_x])
    intercept, slope = np.linalg.lstsq(design, y, rcond=None)[0]
    fitted = intercept + slope * centered_x
    residuals = y - fitted

    intercepts = np.linspace(intercept - 55, intercept + 55, 150)
    slopes = np.linspace(slope - 35, slope + 35, 150)
    B, W = np.meshgrid(intercepts, slopes)
    mse = np.mean(
        (y[:, None, None] - B[None, :, :] - W[None, :, :] * centered_x[:, None, None])
        ** 2,
        axis=0,
    )

    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.55), constrained_layout=True)

    ax = axes[0]
    order = np.argsort(x)
    ax.scatter(x, y, s=15, alpha=0.42, color=RICE_LIGHT_BLUE, edgecolors="none")
    ax.plot(x[order], fitted[order], color=RICE_BLUE, linewidth=2.5)
    sample = order[::45]
    ax.vlines(
        x[sample], fitted[sample], y[sample], color=RICE_RED, alpha=0.65, linewidth=0.8
    )
    ax.set(
        title="Data space",
        xlabel="baseline BMI",
        ylabel="target and fitted value",
    )
    panel_label(ax, "A")

    ax = axes[1]
    ax.axhline(0, color=RICE_GRAY, linewidth=1)
    ax.scatter(fitted, residuals, s=15, alpha=0.48, color=RICE_GREEN, edgecolors="none")
    ax.set(title="Residual space", xlabel="fitted value", ylabel="residual $y-\\hat y$")
    panel_label(ax, "B")

    ax = axes[2]
    contour = ax.contour(B, W, mse, levels=18, cmap="Blues_r", linewidths=1.0)
    ax.clabel(contour, inline=True, fontsize=6, fmt="%.0f")
    ax.scatter(
        [intercept],
        [slope],
        marker="*",
        s=120,
        color=RICE_GOLD,
        edgecolor=RICE_BLUE,
        linewidth=0.7,
        zorder=4,
    )
    ax.set(title="Parameter space", xlabel="intercept $b$", ylabel="slope $w$")
    panel_label(ax, "C")

    save_figure(fig, "regression-geometry")


def gradient_methods() -> None:
    """Compare stability, curvature, and acceleration on exact quadratics."""

    def scalar_history(rate: float, steps: int = 18) -> np.ndarray:
        values = [5.0]
        for _ in range(steps):
            values.append(values[-1] - rate * 2.0 * (values[-1] - 1.5))
        return np.asarray(values)

    hessian = np.diag([1.0, 40.0])

    def objective(point: np.ndarray) -> float:
        return float(0.5 * point @ hessian @ point)

    def gradient(point: np.ndarray) -> np.ndarray:
        return hessian @ point

    def trajectory(method: str, steps: int = 75) -> np.ndarray:
        point = np.array([5.5, 1.8])
        velocity = np.zeros(2)
        path = [point.copy()]
        # Look-ahead evaluates the steep coordinate at a different point and
        # requires a smaller stable step for this deliberately narrow valley.
        rate = 0.015 if method == "look-ahead momentum" else 0.035
        momentum = 0.82
        for _ in range(steps):
            if method == "gradient descent":
                point = point - rate * gradient(point)
            elif method == "heavy-ball":
                velocity = momentum * velocity - rate * gradient(point)
                point = point + velocity
            else:
                look_ahead = point + momentum * velocity
                velocity = momentum * velocity - rate * gradient(look_ahead)
                point = point + velocity
            path.append(point.copy())
        return np.asarray(path)

    fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.0), constrained_layout=True)

    ax = axes[0, 0]
    for rate, color in zip(
        (0.05, 0.35, 0.55), (RICE_GRAY, RICE_BLUE, RICE_RED), strict=True
    ):
        values = scalar_history(rate)
        ax.plot(
            values, marker="o", markersize=2.5, color=color, label=f"$\\eta={rate}$"
        )
    ax.axhline(1.5, color=RICE_GOLD, linestyle="--", linewidth=1.3, label="minimizer")
    ax.set(
        title="Step size controls stability",
        xlabel="iteration",
        ylabel="parameter $w_t$",
    )
    ax.legend(fontsize=8)
    panel_label(ax, "A")

    methods = {
        "gradient descent": (RICE_BLUE, "-"),
        "heavy-ball": (RICE_GOLD, "-"),
        "look-ahead momentum": (RICE_GREEN, "-"),
    }
    paths = {name: trajectory(name) for name in methods}
    x_grid = np.linspace(-6, 6, 240)
    y_grid = np.linspace(-2.1, 2.1, 240)
    XX, YY = np.meshgrid(x_grid, y_grid)
    ZZ = 0.5 * (XX**2 + 40.0 * YY**2)

    ax = axes[0, 1]
    ax.contour(
        XX, YY, ZZ, levels=np.geomspace(0.2, 100, 13), colors="#CBD6E2", linewidths=0.8
    )
    for name, (color, linestyle) in methods.items():
        path = paths[name]
        ax.plot(
            path[:, 0],
            path[:, 1],
            color=color,
            linestyle=linestyle,
            linewidth=1.8,
            label=name,
        )
        ax.scatter(path[0, 0], path[0, 1], color=color, s=18)
    ax.scatter([0], [0], marker="*", s=90, color=RICE_RED, zorder=5)
    ax.set(
        title="An ill-conditioned quadratic", xlabel="$\\theta_1$", ylabel="$\\theta_2$"
    )
    ax.legend(fontsize=7.5)
    panel_label(ax, "B")

    ax = axes[1, 0]
    for name, (color, _) in methods.items():
        values = np.array([objective(point) for point in paths[name]])
        ax.semilogy(values, color=color, linewidth=2, label=name)
    ax.set(
        title="Compare work on an objective scale",
        xlabel="gradient evaluation",
        ylabel="$J(\\theta_t)$ (log scale)",
    )
    ax.legend(fontsize=8)
    panel_label(ax, "C")

    ax = axes[1, 1]
    batch_sizes = np.array([1, 8, 32, 128, 512])
    relative_noise = 1 / np.sqrt(batch_sizes)
    relative_updates = 512 / batch_sizes
    ax.loglog(
        batch_sizes,
        relative_noise,
        marker="o",
        color=RICE_RED,
        label="gradient noise $\\propto B^{-1/2}$",
    )
    ax.loglog(
        batch_sizes,
        relative_updates / relative_updates.max(),
        marker="s",
        color=RICE_BLUE,
        label="updates per epoch (relative)",
    )
    ax.set(
        title="Mini-batch trade-off", xlabel="batch size $B$", ylabel="relative scale"
    )
    ax.legend(fontsize=7.5)
    panel_label(ax, "D")

    save_figure(fig, "gradient-methods")


def sigmoid(values: np.ndarray) -> np.ndarray:
    """Evaluate the logistic sigmoid without overflowing at extreme scores."""

    scores = np.asarray(values, dtype=float)
    probabilities = np.empty_like(scores)
    nonnegative = scores >= 0
    probabilities[nonnegative] = 1.0 / (1.0 + np.exp(-scores[nonnegative]))
    exponential = np.exp(scores[~nonnegative])
    probabilities[~nonnegative] = exponential / (1.0 + exponential)
    return probabilities


def logistic_sigmoid_data(tables: dict[str, pd.DataFrame]) -> None:
    """Connect sigmoid geometry to candidate and fitted curves on real data."""

    cancer = tables["cancer"].copy()
    cancer["malignant_event"] = (
        cancer["diagnosis_label"].astype(str).str.lower() == "malignant"
    ).astype(int)
    training, _ = train_test_split(
        cancer,
        test_size=0.30,
        random_state=438,
        stratify=cancer["malignant_event"],
    )

    feature = "worst_concave_points"
    raw_x = training[feature].to_numpy()
    y = training["malignant_event"].to_numpy()
    feature_grid = np.linspace(raw_x.min(), raw_x.max(), 500)
    logit_grid = np.linspace(-8.0, 8.0, 600)

    fitted_model = make_pipeline(
        StandardScaler(),
        LogisticRegression(C=np.inf, solver="lbfgs", max_iter=5_000),
    ).fit(training[[feature]], y)
    fitted_probability = fitted_model.predict_proba(
        pd.DataFrame({feature: feature_grid})
    )[:, 1]

    midpoint = float(training[feature].median())
    shifted_midpoint = float(training[feature].quantile(0.65))
    candidate_curves = (
        ("gentle", 25.0, midpoint, RICE_LIGHT_BLUE),
        ("steep", 70.0, midpoint, RICE_GOLD),
        ("shifted", 70.0, shifted_midpoint, RICE_RED),
    )

    fig, axes = plt.subplots(1, 3, figsize=(11.6, 3.55), constrained_layout=True)

    ax = axes[0]
    activation = sigmoid(logit_grid)
    derivative = activation * (1.0 - activation)
    ax.plot(
        logit_grid,
        activation,
        color=RICE_BLUE,
        linewidth=2.5,
        label="$\\sigma(z)$",
    )
    ax.plot(
        logit_grid,
        derivative,
        color=RICE_GOLD,
        linewidth=2.1,
        label="$\\sigma'(z)$",
    )
    ax.axvline(0.0, color=RICE_GRAY, linestyle="--", linewidth=0.9)
    ax.scatter([0], [0.5], color=RICE_RED, s=32, zorder=4)
    ax.annotate(
        "midpoint $(0,1/2)$",
        xy=(0, 0.5),
        xytext=(1.0, 0.63),
        arrowprops={"arrowstyle": "->", "color": RICE_GRAY},
        fontsize=8,
    )
    ax.set(
        title="Activation geometry",
        xlabel="affine score $z$",
        ylabel="function value",
        xlim=(-8, 8),
        ylim=(-0.03, 1.03),
    )
    ax.legend(fontsize=8)
    panel_label(ax, "A")

    jitter_rng = np.random.default_rng(438)
    jittered_y = y + jitter_rng.normal(0.0, 0.017, len(y))
    ax = axes[1]
    ax.scatter(
        raw_x,
        jittered_y,
        color=RICE_GRAY,
        alpha=0.26,
        s=13,
        edgecolors="none",
        label="observed outcome",
    )
    for label, slope, curve_midpoint, color in candidate_curves:
        ax.plot(
            feature_grid,
            sigmoid(slope * (feature_grid - curve_midpoint)),
            color=color,
            linewidth=2.0,
            label=label,
        )
    ax.set(
        title="Candidate models on data",
        xlabel="worst concave points",
        ylabel="$P(Y=1\\mid x)$",
        ylim=(-0.08, 1.08),
    )
    ax.legend(fontsize=7.4, loc="center right")
    panel_label(ax, "B")

    ax = axes[2]
    for event, label, color in (
        (0, "benign", RICE_GREEN),
        (1, "malignant", RICE_RED),
    ):
        selected = y == event
        ax.scatter(
            raw_x[selected],
            jittered_y[selected],
            color=color,
            alpha=0.32,
            s=14,
            edgecolors="none",
            label=label,
        )
    ax.plot(
        feature_grid,
        fitted_probability,
        color=RICE_BLUE,
        linewidth=2.6,
        label="training fit",
    )
    crossing_index = int(np.argmin(np.abs(fitted_probability - 0.5)))
    crossing = feature_grid[crossing_index]
    ax.axvline(crossing, color=RICE_GOLD, linestyle="--", linewidth=1.2)
    ax.annotate(
        "$\\hat p=0.5$",
        xy=(crossing, 0.5),
        xytext=(crossing + 0.025, 0.36),
        arrowprops={"arrowstyle": "->", "color": RICE_GRAY},
        fontsize=8,
    )
    ax.set(
        title="A fitted conditional probability",
        xlabel="worst concave points",
        ylabel="malignant-event probability",
        ylim=(-0.08, 1.08),
    )
    ax.legend(fontsize=7.2, loc="lower right")
    panel_label(ax, "C")

    save_figure(fig, "logistic-sigmoid-data")


def logistic_loss_geometry() -> None:
    """Show outcome loss, likelihood, and population-risk geometry."""

    probability = np.linspace(0.001, 0.999, 700)
    fig, axes = plt.subplots(1, 3, figsize=(11.6, 3.55), constrained_layout=True)

    ax = axes[0]
    ax.plot(
        probability,
        -np.log(probability),
        color=RICE_RED,
        linewidth=2.3,
        label="observed $y=1$",
    )
    ax.plot(
        probability,
        -np.log(1.0 - probability),
        color=RICE_GREEN,
        linewidth=2.3,
        label="observed $y=0$",
    )
    ax.set(
        title="Log loss judges a report",
        xlabel="reported probability $p$",
        ylabel="loss $\\ell(p;y)$",
        xlim=(0, 1),
        ylim=(0, 6.2),
    )
    ax.legend(fontsize=8)
    panel_label(ax, "A")

    ax = axes[1]
    for events, color in ((2, RICE_GREEN), (5, RICE_GOLD), (8, RICE_RED)):
        likelihood = probability**events * (1.0 - probability) ** (10 - events)
        relative_likelihood = likelihood / likelihood.max()
        ax.plot(
            probability,
            relative_likelihood,
            color=color,
            linewidth=2.2,
            label=f"$k={events}$ of $n=10$",
        )
        ax.scatter([events / 10], [1.0], color=color, s=28, zorder=4)
    ax.set(
        title="Data reshape the likelihood",
        xlabel="candidate parameter $p$",
        ylabel="relative likelihood",
        xlim=(0, 1),
        ylim=(0, 1.08),
    )
    ax.legend(fontsize=8)
    panel_label(ax, "B")

    ax = axes[2]
    for truth, color in ((0.2, RICE_GREEN), (0.5, RICE_GOLD), (0.8, RICE_RED)):
        expected_loss = -(
            truth * np.log(probability)
            + (1.0 - truth) * np.log(1.0 - probability)
        )
        ax.plot(
            probability,
            expected_loss,
            color=color,
            linewidth=2.2,
            label=f"true $q={truth:.1f}$",
        )
        minimum = -(truth * np.log(truth) + (1.0 - truth) * np.log(1.0 - truth))
        ax.scatter([truth], [minimum], color=color, s=30, zorder=4)
    ax.set(
        title="Truth minimizes expected log loss",
        xlabel="reported probability $p$",
        ylabel="$R_q(p)$",
        xlim=(0, 1),
        ylim=(0, 2.2),
    )
    ax.legend(fontsize=8)
    panel_label(ax, "C")

    save_figure(fig, "logistic-loss-geometry")


def logistic_validation_evidence(tables: dict[str, pd.DataFrame]) -> None:
    """Separate discrimination, calibration, and an operating policy."""

    cancer = tables["cancer"].copy()
    cancer["malignant_event"] = (
        cancer["diagnosis_label"].astype(str).str.lower() == "malignant"
    ).astype(int)
    # A deliberately modest one-feature model leaves visible overlap and
    # calibration uncertainty instead of producing a nearly perfect exhibit.
    features = ["worst_concave_points"]
    training, validation = train_test_split(
        cancer,
        test_size=0.30,
        random_state=438,
        stratify=cancer["malignant_event"],
    )
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(C=0.03, solver="lbfgs", max_iter=5_000),
    ).fit(training[features], training["malignant_event"])
    probability = model.predict_proba(validation[features])[:, 1]
    outcome = validation["malignant_event"].to_numpy()

    evidence = pd.DataFrame({"probability": probability, "event": outcome})
    evidence["bin"] = pd.qcut(evidence["probability"], q=6, duplicates="drop")
    summary = (
        evidence.groupby("bin", observed=True)
        .agg(
            rows=("event", "size"),
            mean_probability=("probability", "mean"),
            event_rate=("event", "mean"),
        )
        .reset_index(drop=True)
    )
    z_score = 1.96
    rows = summary["rows"].to_numpy(dtype=float)
    event_rate = summary["event_rate"].to_numpy()
    denominator = 1.0 + z_score**2 / rows
    wilson_center = (event_rate + z_score**2 / (2.0 * rows)) / denominator
    wilson_half_width = (
        z_score
        / denominator
        * np.sqrt(
            event_rate * (1.0 - event_rate) / rows
            + z_score**2 / (4.0 * rows**2)
        )
    )

    fig, axes = plt.subplots(1, 3, figsize=(11.6, 3.55), constrained_layout=True)

    ax = axes[0]
    histogram_bins = np.linspace(0.0, 1.0, 14)
    for event, label, color in (
        (0, "observed benign", RICE_GREEN),
        (1, "observed malignant", RICE_RED),
    ):
        ax.hist(
            probability[outcome == event],
            bins=histogram_bins,
            alpha=0.58,
            color=color,
            label=label,
        )
    ax.set(
        title="Discrimination",
        xlabel="modeled malignant probability",
        ylabel="validation observations",
        xlim=(0, 1),
    )
    ax.legend(fontsize=7.4)
    panel_label(ax, "A")

    ax = axes[1]
    ax.errorbar(
        summary["mean_probability"],
        wilson_center,
        yerr=wilson_half_width,
        fmt="o",
        capsize=4,
        color=RICE_BLUE,
        ecolor=RICE_LIGHT_BLUE,
        markersize=5,
        label="six validation bins",
    )
    ax.plot([0, 1], [0, 1], color=RICE_GRAY, linestyle="--", linewidth=1.2)
    ax.set(
        title="Calibration evidence",
        xlabel="mean modeled probability",
        ylabel="observed event fraction",
        xlim=(0, 1),
        ylim=(0, 1),
    )
    ax.legend(fontsize=7.5)
    panel_label(ax, "B")

    thresholds = np.linspace(0.01, 0.99, 197)
    costs = []
    for threshold in thresholds:
        predicted_event = probability >= threshold
        false_negative = np.sum((~predicted_event) & (outcome == 1))
        false_positive = np.sum(predicted_event & (outcome == 0))
        costs.append((5.0 * false_negative + false_positive) / len(outcome))
    costs_array = np.asarray(costs)
    selected_index = int(np.argmin(costs_array))
    selected_threshold = thresholds[selected_index]
    ax = axes[2]
    ax.plot(thresholds, costs_array, color=RICE_BLUE, linewidth=2.4)
    ax.scatter(
        [selected_threshold],
        [costs_array[selected_index]],
        color=RICE_RED,
        s=35,
        zorder=4,
    )
    ax.annotate(
        f"validation choice: {selected_threshold:.2f}",
        xy=(selected_threshold, costs_array[selected_index]),
        xytext=(0.38, costs_array.max() * 0.72),
        arrowprops={"arrowstyle": "->", "color": RICE_GRAY},
        fontsize=8,
    )
    ax.set(
        title="One declared decision policy",
        xlabel="probability threshold",
        ylabel="cost per validation row",
        xlim=(0, 1),
    )
    panel_label(ax, "C")

    save_figure(fig, "logistic-validation-evidence")


def classification_performance_context(tables: dict[str, pd.DataFrame]) -> None:
    """Show how confusion rates and predictive values depend on context."""

    cancer = tables["cancer"].copy()
    cancer["malignant_event"] = (
        cancer["diagnosis_label"].astype(str).str.lower() == "malignant"
    ).astype(int)
    feature = ["worst_concave_points"]
    training, validation = train_test_split(
        cancer,
        test_size=0.30,
        random_state=438,
        stratify=cancer["malignant_event"],
    )
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(C=0.03, solver="lbfgs", max_iter=5_000),
    ).fit(training[feature], training["malignant_event"])
    probability = model.predict_proba(validation[feature])[:, 1]
    outcome = validation["malignant_event"].to_numpy()

    # Use the same explicit five-to-one teaching cost as the preceding figure.
    thresholds = np.linspace(0.01, 0.99, 197)
    costs = []
    for threshold in thresholds:
        decision = probability >= threshold
        false_negative = np.sum((~decision) & (outcome == 1))
        false_positive = np.sum(decision & (outcome == 0))
        costs.append(5.0 * false_negative + false_positive)
    threshold = float(thresholds[int(np.argmin(costs))])
    matrix = confusion_matrix(outcome, probability >= threshold, labels=[0, 1])
    row_normalized = matrix / matrix.sum(axis=1, keepdims=True)

    true_negative, false_positive, false_negative, true_positive = matrix.ravel()
    sensitivity = true_positive / (true_positive + false_negative)
    specificity = true_negative / (true_negative + false_positive)
    prevalence = np.linspace(0.01, 0.99, 400)
    precision = (
        prevalence
        * sensitivity
        / (
            prevalence * sensitivity
            + (1.0 - prevalence) * (1.0 - specificity)
        )
    )
    negative_predictive_value = (
        (1.0 - prevalence)
        * specificity
        / (
            (1.0 - prevalence) * specificity
            + prevalence * (1.0 - sensitivity)
        )
    )
    accuracy = prevalence * sensitivity + (1.0 - prevalence) * specificity

    fig, axes = plt.subplots(1, 3, figsize=(11.6, 3.55), constrained_layout=True)

    for ax, values, title, formatter, label in (
        (axes[0], matrix, "Counts retain sample size", "d", "A"),
        (
            axes[1],
            row_normalized,
            "Condition on the actual class",
            ".0%",
            "B",
        ),
    ):
        image = ax.imshow(values, cmap="Blues", vmin=0)
        for row in range(2):
            for column in range(2):
                value = values[row, column]
                text = (
                    format(int(value), formatter)
                    if formatter == "d"
                    else format(value, formatter)
                )
                ax.text(column, row, text, ha="center", va="center", fontsize=11)
        ax.set(
            title=title,
            xlabel=f"predicted class at $t={threshold:.2f}$",
            ylabel="recorded outcome",
            xticks=[0, 1],
            yticks=[0, 1],
            xticklabels=["non-event", "event"],
            yticklabels=["non-event", "event"],
        )
        fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
        panel_label(ax, label)

    ax = axes[2]
    ax.plot(
        prevalence,
        precision,
        color=RICE_RED,
        linewidth=2.3,
        label="precision",
    )
    ax.plot(
        prevalence,
        negative_predictive_value,
        color=RICE_GREEN,
        linewidth=2.3,
        label="negative predictive value",
    )
    ax.plot(
        prevalence,
        accuracy,
        color=RICE_BLUE,
        linewidth=2.3,
        label="accuracy",
    )
    validation_prevalence = float(outcome.mean())
    ax.axvline(
        validation_prevalence,
        color=RICE_GRAY,
        linestyle="--",
        linewidth=1.2,
        label="validation prevalence",
    )
    ax.set(
        title="Case mix changes metrics",
        xlabel="event prevalence $\\pi$",
        ylabel="metric (fixed sensitivity/specificity)",
        xlim=(0, 1),
        ylim=(0, 1.02),
    )
    ax.legend(fontsize=7.1, loc="lower center")
    panel_label(ax, "C")

    save_figure(fig, "classification-performance-context")


def main() -> None:
    """Regenerate every Part II opening figure deterministically."""

    configure_style()
    tables = load_tables()
    learning_landscape(tables)
    supervised_evidence(tables)
    regression_geometry(tables)
    gradient_methods()
    logistic_single_neuron_contract()
    logistic_sigmoid_data(tables)
    logistic_loss_geometry()
    logistic_validation_evidence(tables)
    classification_performance_context(tables)
    svm_hyperplane_geometry()
    linear_svm_geometry(tables)
    neural_network_anatomy()
    neural_composition_expressivity()


if __name__ == "__main__":
    main()
