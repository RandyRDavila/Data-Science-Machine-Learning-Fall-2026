"""Generate the explanatory figures for Chapter 16 on ensemble learning."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUTPUT = Path(__file__).resolve().parent / "generated"
OUTPUT.mkdir(parents=True, exist_ok=True)

NAVY = "#00205b"
BLUE = "#5b8db8"
GOLD = "#f2c14e"
RED = "#c75b39"
GREEN = "#3f7d66"
GRAY = "#5b6770"


def save(figure: plt.Figure, stem: str) -> None:
    for suffix in ("pdf", "png"):
        figure.savefig(OUTPUT / f"{stem}.{suffix}", bbox_inches="tight", dpi=220)
    plt.close(figure)


def variance_correlation() -> None:
    sizes = np.arange(1, 201)
    figure, axis = plt.subplots(figsize=(8.6, 4.8))
    for correlation, color in zip(
        (0.0, 0.1, 0.3, 0.6, 1.0), (GREEN, BLUE, NAVY, RED, GRAY), strict=True
    ):
        relative_variance = correlation + (1 - correlation) / sizes
        axis.plot(
            sizes,
            relative_variance,
            color=color,
            linewidth=2.2,
            label=rf"$\rho={correlation}$",
        )
    axis.set(
        xlabel="number of ensemble members $M$",
        ylabel=r"$\operatorname{Var}(\bar E)/\sigma^2$",
        title="Averaging removes independent variation, not shared error",
        xlim=(1, 200),
        ylim=(-0.02, 1.03),
    )
    axis.legend(ncol=5, loc="upper right", frameon=False)
    axis.grid(alpha=0.2)
    figure.tight_layout()
    save(figure, "ensemble-correlation-variance")


def forest_mechanism() -> None:
    figure, axis = plt.subplots(figsize=(10, 5.7))
    axis.set_xlim(0, 10)
    axis.set_ylim(0, 6)
    axis.axis("off")

    def box(x, y, width, height, text, color, fontsize=10):
        patch = FancyBboxPatch(
            (x, y), width, height, boxstyle="round,pad=0.12",
            facecolor=color, edgecolor=NAVY, linewidth=1.2
        )
        axis.add_patch(patch)
        axis.text(x + width / 2, y + height / 2, text, ha="center", va="center",
                  fontsize=fontsize)

    def arrow(start, end):
        axis.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>",
                                      mutation_scale=13, color=GRAY, linewidth=1.4))

    box(0.25, 2.35, 1.6, 1.0, "training rows\nand features", "#dce6f2")
    ys = (4.5, 2.5, 0.5)
    for index, y in enumerate(ys, start=1):
        box(2.45, y, 1.55, 0.8, f"bootstrap {index}\nwith replacement", "#edf2f7", 9)
        box(4.65, y, 1.55, 0.8, f"randomized\ntree {index}", "#f7e7a9", 9)
        box(6.85, y, 1.3, 0.8, rf"$p_{index}(y\mid x)$", "#e4f0e9", 10)
        arrow((1.85, 2.85), (2.45, y + 0.4))
        arrow((4.0, y + 0.4), (4.65, y + 0.4))
        arrow((6.2, y + 0.4), (6.85, y + 0.4))
        arrow((8.15, y + 0.4), (8.65, 2.9))
    box(8.65, 2.35, 1.1, 1.1, "average\nprobabilities", "#d9ecdf", 9)
    axis.text(3.25, 5.65, "row perturbation", ha="center", color=GRAY)
    axis.text(5.42, 5.65, "feature perturbation at splits", ha="center", color=GRAY)
    axis.text(5.0, 0.02,
              "out-of-bag rows: observations omitted from a member's bootstrap sample",
              ha="center", fontsize=9, color=GRAY)
    axis.set_title("Random forest: create diversity, then aggregate", color=NAVY,
                   fontsize=14, pad=10)
    save(figure, "random-forest-mechanism")


def boosting_sequence() -> None:
    x = np.linspace(-2.5, 2.5, 120)
    truth = 1.2 * np.sin(1.4 * x) + 0.35 * x
    stage0 = np.full_like(x, truth.mean())
    corrections = [
        0.75 * np.tanh(1.1 * x),
        -0.35 * np.sign(x + 0.7) + 0.3 * np.sign(x - 0.9),
        0.22 * np.sin(3.1 * x),
    ]
    predictions = [stage0]
    for correction in corrections:
        predictions.append(predictions[-1] + correction)

    figure, axes = plt.subplots(1, 4, figsize=(12, 3.4), sharey=True)
    for stage, axis in enumerate(axes):
        axis.plot(x, truth, color=GRAY, linewidth=2, label="target structure")
        axis.plot(x, predictions[stage], color=NAVY, linewidth=2.2,
                  label="current additive model")
        axis.fill_between(x, predictions[stage], truth, color=GOLD, alpha=0.28)
        axis.set_title(f"stage {stage}")
        axis.set_xlabel("feature $x$")
        axis.grid(alpha=0.15)
        if stage == 0:
            axis.set_ylabel("response / prediction")
        if stage < 3:
            axis.annotate(
                "fit next tree\nto negative gradient",
                xy=(1.03, 0.5), xycoords="axes fraction", ha="left", va="center",
                fontsize=8, color=RED,
            )
    axes[0].legend(frameon=False, fontsize=8, loc="upper left")
    figure.suptitle("Boosting: each weak learner corrects the current function",
                    color=NAVY, fontsize=14)
    figure.tight_layout()
    save(figure, "boosting-stagewise-correction")


def stacking_boundary() -> None:
    figure, axes = plt.subplots(1, 2, figsize=(11, 5.2))
    for axis in axes:
        axis.set_xlim(0, 10)
        axis.set_ylim(0, 7)
        axis.axis("off")

    def panel(axis, safe):
        title = (
            "Leakage-safe out-of-fold stacking"
            if safe
            else "Leaky in-sample stacking"
        )
        axis.set_title(title, color=GREEN if safe else RED, fontsize=12)
        train_color = "#e4f0e9" if safe else "#f6ddd5"
        labels = ["base model A", "base model B", "base model C"]
        ys = [5.4, 3.7, 2.0]
        for label, y in zip(labels, ys, strict=True):
            box = FancyBboxPatch((0.4, y), 2.4, .8, boxstyle="round,pad=.1",
                                 facecolor=train_color, edgecolor=NAVY)
            axis.add_patch(box)
            axis.text(1.6, y + .4, label, ha="center", va="center", fontsize=9)
            source = "other folds" if safe else "all training rows"
            axis.text(
                1.6,
                y - 0.28,
                f"fit on {source}",
                ha="center",
                fontsize=7,
                color=GRAY,
            )
            axis.add_patch(FancyArrowPatch((2.8, y+.4), (4.0, y+.4), arrowstyle="-|>",
                                           mutation_scale=12, color=GRAY))
        matrix = FancyBboxPatch((4.0, 2.35), 2.1, 3.4, boxstyle="round,pad=.1",
                                facecolor="#edf2f7", edgecolor=NAVY)
        axis.add_patch(matrix)
        axis.text(5.05, 4.05, "training\nmeta-features\n(probabilities)",
                  ha="center", va="center", fontsize=9)
        axis.add_patch(FancyArrowPatch((6.1, 4.05), (7.0, 4.05), arrowstyle="-|>",
                                       mutation_scale=12, color=GRAY))
        meta = FancyBboxPatch((7.0, 3.45), 2.4, 1.2, boxstyle="round,pad=.1",
                              facecolor=GOLD, edgecolor=NAVY)
        axis.add_patch(meta)
        axis.text(8.2, 4.05, "meta-learner", ha="center", va="center")
        note = ("each row predicted by\na model that did not fit it" if safe else
                "each row predicted by\na model that already fit it")
        axis.text(5.0, 1.05, note, ha="center", fontsize=9,
                  color=GREEN if safe else RED, weight="bold")

    panel(axes[0], False)
    panel(axes[1], True)
    figure.suptitle("The stacking boundary is a data-provenance requirement",
                    color=NAVY, fontsize=14)
    figure.tight_layout()
    save(figure, "stacking-oof-boundary")


if __name__ == "__main__":
    variance_correlation()
    forest_mechanism()
    boosting_sequence()
    stacking_boundary()
