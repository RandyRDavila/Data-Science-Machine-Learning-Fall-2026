"""Generate explanatory figures for Part III's unsupervised-learning opening."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path(__file__).resolve().parent / "generated"
DATABASE = ROOT / "data" / "course_datasets.sqlite"
OUTPUT.mkdir(parents=True, exist_ok=True)

NAVY = "#00205b"
BLUE = "#5b8db8"
GOLD = "#f2c14e"
RED = "#c75b39"
GREEN = "#3f7d66"
GRAY = "#5b6770"
LIGHT = "#edf2f7"
RANDOM_STATE = 438


def save(figure: plt.Figure, stem: str) -> None:
    """Save one figure in print and browser formats."""

    for suffix in ("pdf", "png"):
        figure.savefig(OUTPUT / f"{stem}.{suffix}", bbox_inches="tight", dpi=220)
    plt.close(figure)


def unsupervised_task_map() -> None:
    """Draw the shared-data/different-objective mental model."""

    figure, axis = plt.subplots(figsize=(11, 5.7))
    axis.set_xlim(0, 11)
    axis.set_ylim(0, 6)
    axis.axis("off")

    def box(x: float, y: float, width: float, height: float, text: str, color: str):
        patch = FancyBboxPatch(
            (x, y), width, height, boxstyle="round,pad=0.12",
            facecolor=color, edgecolor=NAVY, linewidth=1.3,
        )
        axis.add_patch(patch)
        axis.text(x + width / 2, y + height / 2, text, ha="center", va="center")

    box(0.3, 2.35, 2.0, 1.2, "observations $X$\nor relations $A$", "#dce6f2")
    destinations = [
        (3.3, 4.35, "clustering\nassignments / memberships", "#f7e7a9"),
        (
            3.3,
            2.35,
            "dimensionality reduction\ncoordinates / reconstruction",
            "#e4f0e9",
        ),
        (3.3, 0.35, "graph learning\ncommunities / embeddings / links", "#f6ddd5"),
    ]
    audits = [
        (7.2, 4.35, "stability + internal geometry"),
        (7.2, 2.35, "retention + downstream utility"),
        (7.2, 0.35, "edge sensitivity + task evidence"),
    ]
    for (x, y, text, color), (audit_x, audit_y, audit) in zip(
        destinations, audits, strict=True
    ):
        box(x, y, 2.9, 1.0, text, color)
        box(audit_x, audit_y, 3.2, 1.0, audit, LIGHT)
        axis.add_patch(FancyArrowPatch((2.3, 2.95), (x, y + 0.5), arrowstyle="-|>",
                                       mutation_scale=13, color=GRAY))
        axis.add_patch(FancyArrowPatch((x + 2.9, y + 0.5),
                                       (audit_x, audit_y + 0.5), arrowstyle="-|>",
                                       mutation_scale=13, color=GRAY))
    axis.text(5.5, 5.75, "Same unlabeled evidence, different mathematical questions",
              ha="center", color=NAVY, fontsize=15, weight="bold")
    axis.text(8.8, 5.12, "evaluation must match the objective",
              ha="center", color=RED, fontsize=10)
    save(figure, "unsupervised-task-map")


def pca_projection_geometry() -> None:
    """Show PCA scores and orthogonal reconstruction residuals."""

    observations = np.array(
        [[-2.4, -1.5], [-1.8, -1.2], [-1.1, -0.3], [-0.4, -0.5],
         [0.2, 0.3], [0.8, 0.4], [1.2, 1.1], [1.9, 1.2], [2.4, 1.8]]
    )
    centered = observations - observations.mean(axis=0)
    _, _, right_vectors = np.linalg.svd(centered, full_matrices=False)
    direction = right_vectors[0]
    scores = centered @ direction
    reconstructed = np.outer(scores, direction)

    figure, axis = plt.subplots(figsize=(8.2, 5.8))
    axis.scatter(
        centered[:, 0], centered[:, 1], s=62, color=BLUE,
        edgecolor="white", linewidth=0.7, label="centered observations", zorder=3,
    )
    extent = np.outer([scores.min() - 0.4, scores.max() + 0.4], direction)
    axis.plot(extent[:, 0], extent[:, 1], color=RED, linewidth=2.5,
              label="first principal direction")
    for point, estimate in zip(centered, reconstructed, strict=True):
        axis.plot([point[0], estimate[0]], [point[1], estimate[1]], color=GRAY,
                  linewidth=1.1, alpha=0.8)
    axis.scatter(reconstructed[:, 0], reconstructed[:, 1], marker="x", s=55,
                 color=NAVY, label="rank-one reconstruction", zorder=4)
    axis.set(aspect="equal", xlabel="centered feature 1", ylabel="centered feature 2",
             title="PCA chooses the axis with the smallest squared residuals")
    axis.legend(frameon=False)
    axis.grid(alpha=0.18)
    save(figure, "pca-projection-geometry")


def load_digits() -> tuple[np.ndarray, np.ndarray]:
    """Load the real handwritten observations from course SQLite."""

    with sqlite3.connect(DATABASE) as connection:
        frame = pd.read_sql_query(
            "SELECT * FROM digits_observations ORDER BY observation_id", connection
        )
    pixels = frame[[f"pixel_{index}" for index in range(64)]].to_numpy(float)
    labels = frame["digit_label"].to_numpy(int)
    return pixels, labels


def digits_reconstruction() -> None:
    """Visualize information retained at several PCA ranks."""

    pixels, labels = load_digits()
    train, test, _, _ = train_test_split(
        pixels, labels, test_size=0.30, stratify=labels, random_state=RANDOM_STATE
    )
    model = PCA(n_components=40, svd_solver="full").fit(train)
    examples = test[:6]
    ranks = [2, 10, 20, 40]
    figure, axes = plt.subplots(5, 6, figsize=(9.2, 7.4))

    for column, image in enumerate(examples):
        axes[0, column].imshow(image.reshape(8, 8), cmap="magma", vmin=0, vmax=16)
        axes[0, column].axis("off")
    axes[0, 0].set_ylabel("original", rotation=0, labelpad=30, va="center")

    for row, rank in enumerate(ranks, start=1):
        approximation = ((examples - model.mean_) @ model.components_[:rank].T)
        approximation = approximation @ model.components_[:rank] + model.mean_
        for column, image in enumerate(approximation):
            axes[row, column].imshow(image.reshape(8, 8), cmap="magma", vmin=0, vmax=16)
            axes[row, column].axis("off")
        axes[row, 0].set_ylabel(f"rank {rank}", rotation=0, labelpad=30, va="center")
    figure.suptitle("PCA rank controls a visible reconstruction tradeoff", color=NAVY)
    figure.tight_layout()
    save(figure, "pca-digits-reconstruction")


def supervised_tradeoff() -> None:
    """Compare real digit accuracy and KNN coordinate cost across PCA ranks."""

    pixels, labels = load_digits()
    train, test, train_labels, test_labels = train_test_split(
        pixels, labels, test_size=0.30, stratify=labels, random_state=RANDOM_STATE
    )
    ranks = [10, 20, 30, 40, 64]
    accuracies = []
    for rank in ranks:
        steps = [("scale", StandardScaler())]
        if rank < 64:
            steps.append(("pca", PCA(n_components=rank, svd_solver="full")))
        steps.append(("classifier", KNeighborsClassifier(n_neighbors=5)))
        candidate = Pipeline(steps).fit(train, train_labels)
        accuracies.append(accuracy_score(test_labels, candidate.predict(test)))

    figure, left = plt.subplots(figsize=(8.8, 5.2))
    left.plot(ranks, accuracies, marker="o", linewidth=2.2, color=NAVY,
              label="held-out accuracy")
    left.set(xlabel="coordinates used by KNN", ylabel="held-out accuracy",
             ylim=(min(accuracies) - 0.015, 1.0),
             title="PCA can reduce distance work while preserving useful accuracy")
    right = left.twinx()
    right.plot(ranks, np.array(ranks) / 64, marker="s", linestyle="--", color=RED,
               label="relative coordinates per distance")
    right.set(ylabel="relative coordinate operations", ylim=(0, 1.05))
    handles = left.lines + right.lines
    left.legend(handles, [line.get_label() for line in handles], frameon=False,
                loc="lower right")
    left.grid(alpha=0.18)
    figure.tight_layout()
    save(figure, "pca-supervised-tradeoff")


if __name__ == "__main__":
    unsupervised_task_map()
    pca_projection_geometry()
    digits_reconstruction()
    supervised_tradeoff()
