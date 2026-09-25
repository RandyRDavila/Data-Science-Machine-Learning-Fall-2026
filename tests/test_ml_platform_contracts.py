"""Executable examples for the shared machine-learning interfaces."""

from typing import Self

import numpy as np
from numpy.typing import ArrayLike, NDArray

from rice_dsm.ml import Clusterer, SupervisedPredictor, Transformer


class MeanRegressor:
    """Small test double satisfying the supervised-predictor protocol."""

    def fit(self, features: ArrayLike, targets: ArrayLike) -> Self:
        array = np.asarray(features, dtype=float)
        target_array = np.asarray(targets, dtype=float)
        if array.ndim != 2 or target_array.shape != (array.shape[0],):
            raise ValueError("features and targets have incompatible shapes")
        self.mean_ = float(np.mean(target_array))
        return self

    def predict(self, features: ArrayLike) -> NDArray[np.float64]:
        if not hasattr(self, "mean_"):
            raise RuntimeError("fit must be called before predict")
        rows = np.asarray(features).shape[0]
        return np.full(rows, self.mean_)


class Centerer:
    """Small test double satisfying the transformer protocol."""

    def fit(self, features: ArrayLike, targets: ArrayLike | None = None) -> Self:
        del targets
        self.center_ = np.asarray(features, dtype=float).mean(axis=0)
        return self

    def transform(self, features: ArrayLike) -> NDArray[np.float64]:
        return np.asarray(features, dtype=float) - self.center_


class ThresholdClusterer:
    """Small test double satisfying the clusterer protocol."""

    def fit(self, features: ArrayLike) -> Self:
        self.threshold_ = float(np.asarray(features, dtype=float)[:, 0].mean())
        return self

    def predict(self, features: ArrayLike) -> NDArray[np.int64]:
        values = np.asarray(features, dtype=float)[:, 0]
        return (values >= self.threshold_).astype(np.int64)


def test_supervised_algorithm_satisfies_protocol_by_behavior() -> None:
    estimator = MeanRegressor().fit([[0.0], [1.0]], [2.0, 4.0])

    assert isinstance(estimator, SupervisedPredictor)
    np.testing.assert_array_equal(estimator.predict([[2.0], [3.0]]), [3.0, 3.0])


def test_transformer_satisfies_protocol_without_framework_inheritance() -> None:
    transformer = Centerer().fit([[1.0, 3.0], [3.0, 7.0]])

    assert isinstance(transformer, Transformer)
    np.testing.assert_array_equal(
        transformer.transform([[2.0, 5.0]]), [[0.0, 0.0]]
    )


def test_clusterer_satisfies_protocol_by_behavior() -> None:
    clusterer = ThresholdClusterer().fit([[0.0], [2.0]])

    assert isinstance(clusterer, Clusterer)
    np.testing.assert_array_equal(clusterer.predict([[0.5], [1.5]]), [0, 1])
