"""Generate reproducible decision-tree figures for Chapter 22."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from rice_dsm.ml.trees import DecisionTreeClassifier, DecisionTreeRegressor, plot_tree

OUTPUT = Path(__file__).parent / "generated"
OUTPUT.mkdir(parents=True, exist_ok=True)

NAVY = "#00205b"
RED = "#c8102e"
GOLD = "#f2a900"
GRAY = "#5b6770"


def save(figure: plt.Figure, name: str) -> None:
    for suffix in ("pdf", "png"):
        figure.savefig(OUTPUT / f"{name}.{suffix}", dpi=220, bbox_inches="tight")
    plt.close(figure)


def recursive_partition() -> None:
    rng = np.random.default_rng(438)
    x = rng.uniform(0, 10, size=(160, 2))
    labels = ((x[:, 0] > 5.4) & (x[:, 1] > 3.2)) | (
        (x[:, 0] <= 5.4) & (x[:, 1] > 7.0)
    )

    figure, axis = plt.subplots(figsize=(9.2, 5.2))
    axis.axvspan(0, 5.4, color="#e9f0f8", alpha=0.8)
    axis.axvspan(5.4, 10, color="#fff1f1", alpha=0.8)
    axis.axvline(5.4, color=NAVY, linewidth=2.4)
    axis.hlines(7.0, 0, 5.4, color=GOLD, linewidth=2.4)
    axis.hlines(3.2, 5.4, 10, color=GOLD, linewidth=2.4)
    axis.scatter(
        x[~labels, 0],
        x[~labels, 1],
        color=NAVY,
        edgecolor="white",
        linewidth=0.5,
        label="class 0",
    )
    axis.scatter(
        x[labels, 0],
        x[labels, 1],
        color=RED,
        marker="^",
        edgecolor="white",
        linewidth=0.5,
        label="class 1",
    )
    axis.text(5.55, 9.45, r"root: $x_1 > 5.4$", color=NAVY, weight="bold")
    axis.text(0.25, 7.25, r"left child: $x_2 > 7.0$", color=GRAY)
    axis.text(5.65, 3.45, r"right child: $x_2 > 3.2$", color=GRAY)
    axis.set(
        xlim=(0, 10),
        ylim=(0, 10),
        xlabel="feature 1",
        ylabel="feature 2",
        title="Recursive binary questions create rectangular prediction regions",
    )
    axis.legend(frameon=False, loc="lower left", ncol=2)
    figure.tight_layout()
    save(figure, "tree-recursive-partition")


def regression_and_complexity() -> None:
    rng = np.random.default_rng(577)
    x = np.linspace(0, 10, 80)
    signal = 2.0 + 0.7 * x + 2.2 * np.sin(0.9 * x)
    y = signal + rng.normal(0, 0.75, size=x.size)
    thresholds = [2.4, 5.2, 7.8]
    edges = [0.0, *thresholds, 10.0]
    prediction = np.empty_like(x)
    for left, right in zip(edges[:-1], edges[1:], strict=True):
        mask = (x >= left) & (x <= right if right == 10 else x < right)
        prediction[mask] = y[mask].mean()

    figure, axes = plt.subplots(1, 2, figsize=(12.5, 4.6))
    axes[0].scatter(x, y, color=NAVY, alpha=0.65, s=23, label="observations")
    axes[0].plot(x, signal, color=GRAY, linewidth=1.8, label="unobserved smooth signal")
    axes[0].step(
        x,
        prediction,
        where="post",
        color=RED,
        linewidth=2.6,
        label="tree estimate",
    )
    for threshold in thresholds:
        axes[0].axvline(threshold, color=GOLD, linestyle="--", linewidth=1.2)
    axes[0].set(
        xlabel="feature",
        ylabel="response",
        title="Regression leaves return local means",
    )
    axes[0].legend(frameon=False, fontsize=8)

    leaves = np.array([1, 2, 4, 7, 12, 20, 35])
    training = np.array([74, 60, 47, 38, 30, 23, 16])
    validation = np.array([78, 68, 59, 54, 56, 63, 75])
    axes[1].plot(leaves, training, marker="o", color=NAVY, label="training error")
    axes[1].plot(leaves, validation, marker="o", color=RED, label="validation error")
    axes[1].axvline(7, color=GOLD, linestyle="--", label="selected complexity")
    axes[1].set(
        xlabel="number of terminal leaves",
        ylabel="prediction error",
        title="Validation, not training fit, selects complexity",
    )
    axes[1].legend(frameon=False, fontsize=8)
    figure.tight_layout()
    save(figure, "tree-regression-complexity")


def classification_and_regression_anatomy() -> None:
    """Show how identical tree structure carries different statistical evidence."""

    measurements = np.arange(8, dtype=float).reshape(-1, 1)
    classes = np.array([0, 0, 0, 1, 1, 0, 1, 1])
    responses = np.array([2.0, 2.4, 3.1, 6.8, 7.4, 5.9, 10.2, 10.8])
    classifier = DecisionTreeClassifier(max_depth=2, min_samples_leaf=2).fit(
        measurements, classes
    )
    regressor = DecisionTreeRegressor(max_depth=2, min_samples_leaf=2).fit(
        measurements, responses
    )

    # Match the book's portrait text block so labels remain legible after inclusion.
    figure, axes = plt.subplots(2, 1, figsize=(7.2, 7.5))
    plot_tree(classifier, ["measurement"], ax=axes[0], precision=2)
    axes[0].set_title(
        "Classification: each leaf stores class counts and an empirical probability",
        color=NAVY,
        weight="bold",
        pad=8,
    )
    plot_tree(regressor, ["measurement"], ax=axes[1], precision=2)
    axes[1].set_title(
        "Regression: each leaf stores a local mean and within-leaf squared error",
        color=NAVY,
        weight="bold",
        pad=8,
    )
    figure.tight_layout(h_pad=2.0)
    save(figure, "tree-classification-regression-anatomy")


if __name__ == "__main__":
    recursive_partition()
    regression_and_complexity()
    classification_and_regression_anatomy()
