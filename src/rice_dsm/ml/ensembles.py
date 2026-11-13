"""Inspectable ensemble estimators for Lecture 15.

These implementations expose the mechanics that production libraries optimize:
bootstrap resampling, randomized trees, probability averaging, out-of-bag
prediction, and stagewise residual fitting.  They intentionally favor a small,
auditable API over every optimization offered by mature libraries.
"""

from __future__ import annotations

from typing import Literal

import numpy as np
from numpy.typing import ArrayLike, NDArray
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.tree import DecisionTreeClassifier

from rice_dsm.ml.trees import DecisionTreeRegressor

MaxFeatures = int | float | Literal["sqrt", "log2"] | None


def bootstrap_indices(
    n_samples: int, *, random_state: int | None = None
) -> NDArray[np.int64]:
    """Draw ``n_samples`` row indices uniformly with replacement.

    Parameters
    ----------
    n_samples
        Number of observations in the training set and in the bootstrap draw.
    random_state
        Seed controlling the pseudo-random draw.

    Returns
    -------
    numpy.ndarray
        Integer indices with shape ``(n_samples,)``. Repeated and omitted rows
        are expected features of a bootstrap sample.
    """

    if n_samples < 1:
        raise ValueError("n_samples must be positive")
    generator = np.random.default_rng(random_state)
    return generator.integers(0, n_samples, size=n_samples, dtype=np.int64)


def _feature_matrix(features: ArrayLike) -> NDArray[np.float64]:
    matrix = np.asarray(features, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] == 0 or matrix.shape[1] == 0:
        raise ValueError("features must be a nonempty two-dimensional array")
    if not np.isfinite(matrix).all():
        raise ValueError("features must contain only finite values")
    return matrix


class RandomForestClassifier(ClassifierMixin, BaseEstimator):
    """A transparent bootstrap-and-random-subspace classifier.

    Each member is a CART classifier trained on a bootstrap sample. At every
    split, scikit-learn's verified tree implementation considers only a random
    subset of features. The course class owns the ensemble logic so students
    can inspect sampling, aggregation, and out-of-bag evidence directly.
    """

    def __init__(
        self,
        *,
        n_estimators: int = 100,
        max_features: MaxFeatures = "sqrt",
        max_depth: int | None = None,
        min_samples_leaf: int = 1,
        random_state: int | None = None,
    ) -> None:
        if n_estimators < 1:
            raise ValueError("n_estimators must be positive")
        if max_depth is not None and max_depth < 1:
            raise ValueError("max_depth must be positive or None")
        if min_samples_leaf < 1:
            raise ValueError("min_samples_leaf must be positive")
        self.n_estimators = n_estimators
        self.max_features = max_features
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf
        self.random_state = random_state

    def fit(self, features: ArrayLike, targets: ArrayLike) -> RandomForestClassifier:
        """Fit randomized trees and compute out-of-bag probabilities."""

        x = _feature_matrix(features)
        y = np.asarray(targets)
        if y.ndim != 1 or y.shape[0] != x.shape[0]:
            raise ValueError("targets must be one-dimensional and match features")
        self.classes_ = np.unique(y)
        if self.classes_.size < 2:
            raise ValueError("classification requires at least two classes")
        self.n_features_in_ = x.shape[1]

        generator = np.random.default_rng(self.random_state)
        self.estimators_: list[DecisionTreeClassifier] = []
        self.bootstrap_indices_: list[NDArray[np.int64]] = []
        oob_probability_sum = np.zeros((x.shape[0], self.classes_.size))
        oob_counts = np.zeros(x.shape[0], dtype=int)

        for _ in range(self.n_estimators):
            sample = generator.integers(0, x.shape[0], size=x.shape[0])
            tree_seed = int(generator.integers(0, np.iinfo(np.int32).max))
            tree = DecisionTreeClassifier(
                max_features=self.max_features,
                max_depth=self.max_depth,
                min_samples_leaf=self.min_samples_leaf,
                random_state=tree_seed,
            ).fit(x[sample], y[sample])
            self.estimators_.append(tree)
            self.bootstrap_indices_.append(sample.astype(np.int64))

            # A row is out-of-bag when this tree's bootstrap sample omitted it.
            in_bag = np.zeros(x.shape[0], dtype=bool)
            in_bag[np.unique(sample)] = True
            oob_rows = np.flatnonzero(~in_bag)
            if oob_rows.size:
                oob_probability_sum[oob_rows] += self._aligned_probabilities(
                    tree, x[oob_rows]
                )
                oob_counts[oob_rows] += 1

        self.oob_counts_ = oob_counts
        self.oob_decision_function_ = np.full_like(oob_probability_sum, np.nan)
        covered = oob_counts > 0
        self.oob_decision_function_[covered] = (
            oob_probability_sum[covered] / oob_counts[covered, None]
        )
        if covered.any():
            oob_predictions = self.classes_[
                np.argmax(self.oob_decision_function_[covered], axis=1)
            ]
            self.oob_score_ = float(np.mean(oob_predictions == y[covered]))
        else:
            self.oob_score_ = float("nan")
        self.feature_importances_ = np.mean(
            [tree.feature_importances_ for tree in self.estimators_], axis=0
        )
        return self

    def _aligned_probabilities(
        self, tree: DecisionTreeClassifier, features: NDArray[np.float64]
    ) -> NDArray[np.float64]:
        probabilities = np.zeros((features.shape[0], self.classes_.size))
        positions = np.searchsorted(self.classes_, tree.classes_)
        probabilities[:, positions] = tree.predict_proba(features)
        return probabilities

    def _prediction_features(self, features: ArrayLike) -> NDArray[np.float64]:
        if not hasattr(self, "estimators_"):
            raise RuntimeError("fit must be called before prediction")
        matrix = _feature_matrix(features)
        if matrix.shape[1] != self.n_features_in_:
            raise ValueError(
                f"expected {self.n_features_in_} features; received {matrix.shape[1]}"
            )
        return matrix

    def predict_proba(self, features: ArrayLike) -> NDArray[np.float64]:
        """Average class probabilities over the fitted trees."""

        matrix = self._prediction_features(features)
        probabilities = [
            self._aligned_probabilities(tree, matrix) for tree in self.estimators_
        ]
        return np.mean(probabilities, axis=0)

    def predict(self, features: ArrayLike) -> NDArray[np.object_]:
        """Return the class with greatest mean forest probability."""

        probabilities = self.predict_proba(features)
        return self.classes_[np.argmax(probabilities, axis=1)]


class SquaredErrorGradientBoostingRegressor:
    """Stagewise regression-tree boosting for squared-error loss."""

    def __init__(
        self,
        *,
        n_estimators: int = 100,
        learning_rate: float = 0.1,
        max_depth: int = 2,
        min_samples_leaf: int = 1,
    ) -> None:
        if n_estimators < 1:
            raise ValueError("n_estimators must be positive")
        if not 0.0 < learning_rate <= 1.0:
            raise ValueError("learning_rate must lie in (0, 1]")
        if max_depth < 1 or min_samples_leaf < 1:
            raise ValueError("tree depth and leaf size must be positive")
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf

    def fit(
        self, features: ArrayLike, targets: ArrayLike
    ) -> SquaredErrorGradientBoostingRegressor:
        """Fit each tree to the current negative loss gradient (residual)."""

        x = _feature_matrix(features)
        y = np.asarray(targets, dtype=float)
        if y.ndim != 1 or y.shape[0] != x.shape[0]:
            raise ValueError("targets must be one-dimensional and match features")
        if not np.isfinite(y).all():
            raise ValueError("targets must contain only finite values")

        self.n_features_in_ = x.shape[1]
        self.initial_prediction_ = float(y.mean())
        running_prediction = np.full(y.shape, self.initial_prediction_)
        self.estimators_: list[DecisionTreeRegressor] = []
        self.training_loss_: list[float] = []

        for _ in range(self.n_estimators):
            negative_gradient = y - running_prediction
            tree = DecisionTreeRegressor(
                max_depth=self.max_depth,
                min_samples_leaf=self.min_samples_leaf,
            ).fit(x, negative_gradient)
            running_prediction += self.learning_rate * tree.predict(x)
            self.estimators_.append(tree)
            self.training_loss_.append(float(np.mean((y - running_prediction) ** 2)))
        return self

    def _prediction_features(self, features: ArrayLike) -> NDArray[np.float64]:
        if not hasattr(self, "estimators_"):
            raise RuntimeError("fit must be called before prediction")
        matrix = _feature_matrix(features)
        if matrix.shape[1] != self.n_features_in_:
            raise ValueError(
                f"expected {self.n_features_in_} features; received {matrix.shape[1]}"
            )
        return matrix

    def staged_predict(self, features: ArrayLike):
        """Yield predictions after each boosting stage."""

        matrix = self._prediction_features(features)
        prediction = np.full(matrix.shape[0], self.initial_prediction_)
        for tree in self.estimators_:
            prediction = prediction + self.learning_rate * tree.predict(matrix)
            yield prediction.copy()

    def predict(self, features: ArrayLike) -> NDArray[np.float64]:
        """Return the complete additive model's predictions."""

        staged_predictions = self.staged_predict(features)
        prediction = next(staged_predictions)
        for later_prediction in staged_predictions:
            prediction = later_prediction
        return prediction
