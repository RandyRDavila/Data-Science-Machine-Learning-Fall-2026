"""Generate the nearest-neighbor chapter's reproducible figures."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

from rice_dsm.ml.neighbors import KNearestNeighborsClassifier

ROOT = Path(__file__).parents[2]
OUTPUT = ROOT / "textbook" / "figures" / "generated"
OUTPUT.mkdir(parents=True, exist_ok=True)

BLUE = "#00205B"
RED = "#C8102E"
GOLD = "#F2A900"


def save_figure(figure: plt.Figure, name: str) -> None:
    """Write matching vector and review-friendly raster artifacts."""

    figure.savefig(OUTPUT / f"{name}.pdf", bbox_inches="tight")
    figure.savefig(OUTPUT / f"{name}.png", dpi=180, bbox_inches="tight")
    plt.close(figure)


def neighbor_geometry() -> None:
    """Connect distance ordering to classification and regression aggregation."""

    points = np.array([[0.0, 0.0], [1.0, 1.0], [3.0, 1.0], [4.0, 3.0]])
    labels = np.array([0, 0, 1, 1])
    responses = np.array([1.0, 1.5, 3.5, 4.0])
    query = np.array([2.5, 1.5])
    distances = np.linalg.norm(points - query, axis=1)
    neighbors = np.argsort(distances)[:3]

    figure, axes = plt.subplots(1, 2, figsize=(11.2, 4.7), constrained_layout=True)
    for axis in axes:
        axis.scatter(points[labels == 0, 0], points[labels == 0, 1], s=100,
                     color=BLUE, marker="o", label="class A")
        axis.scatter(points[labels == 1, 0], points[labels == 1, 1], s=110,
                     color=RED, marker="^", label="class B")
        axis.scatter(*query, s=190, color=GOLD, marker="*", edgecolor="black",
                     zorder=4, label="query")
        for index in neighbors:
            axis.plot([query[0], points[index, 0]], [query[1], points[index, 1]],
                      color="0.55", linewidth=1.4, zorder=0)
        axis.set(xlabel=r"feature $x_1$", ylabel=r"feature $x_2$", aspect="equal")
    axes[0].set_title("Classification: two of three neighbors vote B")
    axes[1].set_title(r"Regression: local mean $=(1.5+3.5+4.0)/3$")
    for index, response in enumerate(responses):
        axes[1].annotate(
            f"$y={response:.1f}$", points[index] + [0.08, 0.08], fontsize=9
        )
    axes[0].legend(frameon=True, loc="upper left")
    save_figure(figure, "knn-local-aggregation")


def smoothing_and_dimension() -> None:
    """Show k-dependent smoothing and distance concentration from noise features."""

    generator = np.random.default_rng(438)
    angles = generator.uniform(0.0, 2.0 * np.pi, 90)
    radii = generator.uniform(0.15, 2.0, 90)
    features = np.column_stack([radii * np.cos(angles), radii * np.sin(angles)])
    targets = (radii > 1.05).astype(int)
    xx, yy = np.meshgrid(np.linspace(-2.2, 2.2, 130), np.linspace(-2.2, 2.2, 130))
    grid = np.column_stack([xx.ravel(), yy.ravel()])

    dimensions = np.array([2, 5, 10, 25, 50, 100])
    ratios = []
    for dimension in dimensions:
        cloud = generator.normal(size=(700, dimension))
        query = generator.normal(size=(1, dimension))
        distances = np.linalg.norm(cloud - query, axis=1)
        ratios.append(distances.min() / distances.max())

    figure, axes = plt.subplots(1, 3, figsize=(14.2, 4.2), constrained_layout=True)
    background = ListedColormap(["#DCE6F1", "#F6D5D2"])
    for axis, k in zip(axes[:2], (1, 25), strict=True):
        model = KNearestNeighborsClassifier(k).fit(features, targets)
        surface = model.predict(grid).reshape(xx.shape)
        axis.contourf(xx, yy, surface, levels=[-0.5, 0.5, 1.5], cmap=background)
        axis.scatter(features[:, 0], features[:, 1], c=targets,
                     cmap=ListedColormap([BLUE, RED]), edgecolor="white", s=28)
        axis.set(title=f"$k={k}$", xlabel=r"$x_1$", ylabel=r"$x_2$", aspect="equal")
    axes[2].plot(dimensions, ratios, marker="o", color=BLUE, linewidth=2.2)
    axes[2].set(xlabel="dimension", ylabel="nearest / farthest distance",
                title="Noise dimensions flatten contrast", ylim=(0, 1))
    figure.suptitle("Locality depends on smoothing and representation", fontsize=15)
    save_figure(figure, "knn-smoothing-dimensionality")


def recommender_system() -> None:
    """Draw the distinction between events, fitted similarity, and ranking."""

    figure, axis = plt.subplots(figsize=(11.5, 4.6))
    axis.set_xlim(0, 12)
    axis.set_ylim(0, 5)
    axis.axis("off")
    boxes = [
        (0.3, 1.55, 2.0, 1.7, "rating events", "user, item, stars, time"),
        (3.0, 1.55, 2.1, 1.7, "validated matrix", "missing is not dislike"),
        (5.8, 1.55, 2.1, 1.7, "item similarity", "co-rating support"),
        (8.6, 1.55, 2.1, 1.7, "candidate scores", "exclude seen items"),
    ]
    for index, (x, y, width, height, title, subtitle) in enumerate(boxes):
        color = BLUE if index % 2 == 0 else RED
        rectangle = plt.Rectangle((x, y), width, height, facecolor="white",
                                  edgecolor=color, linewidth=2.2)
        axis.add_patch(rectangle)
        axis.text(x + width / 2, y + 1.08, title, ha="center", va="center",
                  fontsize=11, weight="bold", color=color)
        axis.text(x + width / 2, y + 0.52, subtitle, ha="center", va="center",
                  fontsize=9.5)
        if index < len(boxes) - 1:
            axis.annotate("", xy=(boxes[index + 1][0] - 0.08, y + height / 2),
                          xytext=(x + width + 0.08, y + height / 2),
                          arrowprops={"arrowstyle": "->", "lw": 1.8, "color": "0.3"})
    axis.text(11.1, 2.4, "top-$N$\nranking", ha="center", va="center",
              bbox={"boxstyle": "round,pad=0.45", "facecolor": "#FFF3C4",
                    "edgecolor": GOLD, "linewidth": 2})
    axis.annotate("", xy=(10.82, 2.4), xytext=(10.72, 2.4),
                  arrowprops={"arrowstyle": "->", "lw": 1.8, "color": "0.3"})
    axis.text(6.0, 0.55,
              "Offline recall is exposure-biased; production also measures coverage, "
              "diversity, latency, and user outcomes.",
              ha="center", fontsize=10.5)
    axis.set_title("An item-kNN recommender is a data product, not only a formula",
                   fontsize=15, pad=16)
    save_figure(figure, "knn-recommender-system")


if __name__ == "__main__":
    plt.style.use("seaborn-v0_8-whitegrid")
    neighbor_geometry()
    smoothing_and_dimension()
    recommender_system()
