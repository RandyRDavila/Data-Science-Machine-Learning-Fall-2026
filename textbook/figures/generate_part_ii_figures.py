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
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

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


def main() -> None:
    """Regenerate every Part II opening figure deterministically."""

    configure_style()
    tables = load_tables()
    learning_landscape(tables)
    supervised_evidence(tables)
    regression_geometry(tables)
    gradient_methods()


if __name__ == "__main__":
    main()
