"""Build the small, versioned MNIST sample used by Lecture 12 notebook 02.

The upstream archive is the standard ``mnist.npz`` distributed by Keras at
https://storage.googleapis.com/tensorflow/tf-keras-datasets/mnist.npz.  The
builder deterministically retains an equal number of examples from each class,
so CI can execute the complete from-scratch training story without network
access or a large data checkout.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from rice_dsm.paths import find_project_root


def balanced_indices(labels: np.ndarray, per_class: int, seed: int) -> np.ndarray:
    """Return shuffled indices with exactly ``per_class`` examples per class."""

    generator = np.random.default_rng(seed)
    selected = []
    for label in range(10):
        candidates = np.flatnonzero(labels == label)
        if len(candidates) < per_class:
            raise ValueError(f"class {label} has fewer than {per_class} examples")
        selected.extend(generator.choice(candidates, per_class, replace=False))
    return generator.permutation(np.asarray(selected, dtype=np.int64))


def build_sample(source: Path, destination: Path) -> None:
    """Create a deterministic 2,400/600 observation MNIST archive."""

    with np.load(source) as archive:
        train_images = archive["x_train"]
        train_labels = archive["y_train"]
        test_images = archive["x_test"]
        test_labels = archive["y_test"]

    train_indices = balanced_indices(train_labels, per_class=240, seed=438)
    test_indices = balanced_indices(test_labels, per_class=60, seed=577)
    destination.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        destination,
        x_train=train_images[train_indices].astype(np.uint8),
        y_train=train_labels[train_indices].astype(np.uint8),
        x_test=test_images[test_indices].astype(np.uint8),
        y_test=test_labels[test_indices].astype(np.uint8),
    )


def main() -> None:
    """Parse command-line arguments and write the course data artifact."""

    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="path to the upstream mnist.npz")
    parser.add_argument(
        "--destination",
        type=Path,
        default=find_project_root() / "data" / "mnist_teaching_sample.npz",
    )
    arguments = parser.parse_args()
    build_sample(arguments.source, arguments.destination)


if __name__ == "__main__":
    main()
