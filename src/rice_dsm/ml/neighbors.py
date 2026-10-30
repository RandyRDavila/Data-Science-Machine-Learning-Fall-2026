"""Inspectable nearest-neighbor estimators for teaching and verification.

The implementations favor explicit contracts and readable NumPy over indexing
optimizations.  They are appropriate for small teaching datasets; production
systems should benchmark exact or approximate neighbor-search libraries under
their own latency, memory, and recall requirements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Self

import numpy as np
from numpy.typing import ArrayLike, NDArray

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]
WeightMode = Literal["uniform", "distance"]


def _feature_matrix(features: ArrayLike, n_features: int | None = None) -> FloatArray:
    """Return a finite, nonempty observations-by-features matrix."""

    matrix = np.asarray(features, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] == 0 or matrix.shape[1] == 0:
        raise ValueError("features must have shape (n_observations, n_features)")
    if n_features is not None and matrix.shape[1] != n_features:
        raise ValueError(f"features must contain {n_features} columns")
    if not np.isfinite(matrix).all():
        raise ValueError("features must contain only finite values")
    return matrix


def euclidean_distances(queries: ArrayLike, references: ArrayLike) -> FloatArray:
    """Compute every Euclidean distance from query rows to reference rows.

    Parameters
    ----------
    queries
        Matrix with one query observation per row.
    references
        Matrix with one candidate neighbor per row and the same feature width.

    Returns
    -------
    numpy.ndarray
        Matrix whose entry ``(i, j)`` is ``||queries[i] - references[j]||_2``.
    """

    query_matrix = _feature_matrix(queries)
    reference_matrix = _feature_matrix(references, query_matrix.shape[1])
    differences = query_matrix[:, None, :] - reference_matrix[None, :, :]
    return np.sqrt(np.einsum("qrf,qrf->qr", differences, differences))


def _validate_neighbor_configuration(n_neighbors: int, weights: WeightMode) -> None:
    if isinstance(n_neighbors, bool) or not isinstance(n_neighbors, int):
        raise TypeError("n_neighbors must be an integer")
    if n_neighbors <= 0:
        raise ValueError("n_neighbors must be positive")
    if weights not in {"uniform", "distance"}:
        raise ValueError("weights must be 'uniform' or 'distance'")


@dataclass
class _KNearestNeighborsBase:
    """Shared fitted-state and search behavior for supervised kNN."""

    n_neighbors: int = 5
    weights: WeightMode = "uniform"
    features_: FloatArray | None = field(default=None, init=False, repr=False)
    targets_: NDArray | None = field(default=None, init=False, repr=False)
    n_features_in_: int | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        _validate_neighbor_configuration(self.n_neighbors, self.weights)

    def _fit(self, features: ArrayLike, targets: ArrayLike) -> Self:
        matrix = _feature_matrix(features)
        target_vector = np.asarray(targets)
        if target_vector.ndim != 1 or len(target_vector) != len(matrix):
            raise ValueError("targets must be one-dimensional and align with features")
        if len(matrix) < self.n_neighbors:
            raise ValueError("n_neighbors cannot exceed the number of training rows")
        self.features_ = matrix.copy()
        self.targets_ = target_vector.copy()
        self.n_features_in_ = matrix.shape[1]
        return self

    def _require_fitted(self) -> tuple[FloatArray, NDArray, int]:
        if (
            self.features_ is None
            or self.targets_ is None
            or self.n_features_in_ is None
        ):
            raise RuntimeError(
                "fit must be called before neighbor queries or prediction"
            )
        return self.features_, self.targets_, self.n_features_in_

    def kneighbors(self, features: ArrayLike) -> tuple[FloatArray, IntArray]:
        """Return sorted distances and training-row indices for each query."""

        training_features, _, n_features = self._require_fitted()
        query_matrix = _feature_matrix(features, n_features)
        distances = euclidean_distances(query_matrix, training_features)
        # ``mergesort`` is stable, making equal-distance behavior reproducible.
        neighbor_indices = np.argsort(distances, axis=1, kind="mergesort")[
            :, : self.n_neighbors
        ]
        neighbor_distances = np.take_along_axis(distances, neighbor_indices, axis=1)
        return neighbor_distances, neighbor_indices.astype(np.int64, copy=False)

    def _neighbor_weights(self, distances: FloatArray) -> FloatArray:
        if self.weights == "uniform":
            return np.ones_like(distances)

        weights = np.zeros_like(distances)
        for row_index, row in enumerate(distances):
            exact = row == 0.0
            if exact.any():
                # Exact matches alone vote; distant rows must not dilute them.
                weights[row_index, exact] = 1.0
            else:
                weights[row_index] = 1.0 / row
        return weights


@dataclass
class KNearestNeighborsClassifier(_KNearestNeighborsBase):
    """Classify by uniform or inverse-distance neighbor voting.

    Ties are resolved by the order of ``numpy.unique`` over the training labels,
    which is deterministic and exposed through ``classes_``.
    """

    classes_: NDArray | None = field(default=None, init=False)

    def fit(self, features: ArrayLike, targets: ArrayLike) -> Self:
        """Store training observations and their class labels."""

        self._fit(features, targets)
        assert self.targets_ is not None
        self.classes_ = np.unique(self.targets_)
        if len(self.classes_) < 2:
            raise ValueError("classification requires at least two classes")
        return self

    def predict_proba(self, features: ArrayLike) -> FloatArray:
        """Return normalized weighted vote mass for every fitted class."""

        _, training_targets, _ = self._require_fitted()
        if self.classes_ is None:
            raise RuntimeError("fit must be called before prediction")
        distances, indices = self.kneighbors(features)
        labels = training_targets[indices]
        weights = self._neighbor_weights(distances)
        vote_mass = np.zeros((len(indices), len(self.classes_)), dtype=float)
        for class_index, class_label in enumerate(self.classes_):
            vote_mass[:, class_index] = np.sum(
                weights * (labels == class_label), axis=1
            )
        return vote_mass / vote_mass.sum(axis=1, keepdims=True)

    def predict(self, features: ArrayLike) -> NDArray:
        """Predict the class with the largest normalized vote mass."""

        if self.classes_ is None:
            raise RuntimeError("fit must be called before prediction")
        return self.classes_[np.argmax(self.predict_proba(features), axis=1)]


@dataclass
class KNearestNeighborsRegressor(_KNearestNeighborsBase):
    """Regress by a uniform or inverse-distance average of neighbor targets."""

    def fit(self, features: ArrayLike, targets: ArrayLike) -> Self:
        """Store training observations and finite numeric target values."""

        self._fit(features, targets)
        assert self.targets_ is not None
        try:
            numeric_targets = self.targets_.astype(float)
        except (TypeError, ValueError) as error:
            raise ValueError("regression targets must be numeric") from error
        if not np.isfinite(numeric_targets).all():
            raise ValueError("regression targets must contain only finite values")
        self.targets_ = numeric_targets
        return self

    def predict(self, features: ArrayLike) -> FloatArray:
        """Predict the weighted average target in each query neighborhood."""

        _, training_targets, _ = self._require_fitted()
        distances, indices = self.kneighbors(features)
        weights = self._neighbor_weights(distances)
        neighbor_targets = training_targets[indices].astype(float, copy=False)
        return np.sum(weights * neighbor_targets, axis=1) / weights.sum(axis=1)


@dataclass
class ItemKNNRecommender:
    """Item-item collaborative filtering from explicit user ratings.

    Similarities are cosine similarities of user-mean-centered ratings over
    co-rating users.  Recommendations exclude items already rated by the query
    user and require positive neighbor support.  This small implementation is
    intended to expose the mechanics, not to serve a large catalog.

    Parameters
    ----------
    n_neighbors
        Maximum number of rated neighbor items used to score a candidate.
    min_common_users
        Minimum co-rating count needed before two items receive a similarity.
    """

    n_neighbors: int = 20
    min_common_users: int = 2
    user_ids_: NDArray | None = field(default=None, init=False)
    item_ids_: NDArray | None = field(default=None, init=False)
    ratings_: FloatArray | None = field(default=None, init=False, repr=False)
    user_means_: FloatArray | None = field(default=None, init=False, repr=False)
    similarities_: FloatArray | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.n_neighbors <= 0 or self.min_common_users <= 0:
            raise ValueError("n_neighbors and min_common_users must be positive")

    def fit(
        self, user_ids: ArrayLike, item_ids: ArrayLike, ratings: ArrayLike
    ) -> Self:
        """Build the user-item matrix and item-item similarity matrix."""

        users = np.asarray(user_ids)
        items = np.asarray(item_ids)
        values = np.asarray(ratings, dtype=float)
        if any(vector.ndim != 1 for vector in (users, items, values)):
            raise ValueError("user_ids, item_ids, and ratings must be one-dimensional")
        if not (len(users) == len(items) == len(values)) or len(values) == 0:
            raise ValueError(
                "user_ids, item_ids, and ratings must align and be nonempty"
            )
        if not np.isfinite(values).all():
            raise ValueError("ratings must contain only finite values")
        pairs = list(zip(users.tolist(), items.tolist(), strict=True))
        if len(set(pairs)) != len(pairs):
            raise ValueError("each user-item pair may appear only once")

        self.user_ids_, user_index = np.unique(users, return_inverse=True)
        self.item_ids_, item_index = np.unique(items, return_inverse=True)
        matrix = np.full((len(self.user_ids_), len(self.item_ids_)), np.nan)
        matrix[user_index, item_index] = values
        self.ratings_ = matrix
        self.user_means_ = np.nanmean(matrix, axis=1)
        centered = matrix - self.user_means_[:, None]

        n_items = matrix.shape[1]
        similarities = np.zeros((n_items, n_items), dtype=float)
        for left in range(n_items):
            for right in range(left + 1, n_items):
                common = np.isfinite(centered[:, left]) & np.isfinite(
                    centered[:, right]
                )
                if np.count_nonzero(common) < self.min_common_users:
                    continue
                left_values = centered[common, left]
                right_values = centered[common, right]
                denominator = np.linalg.norm(left_values) * np.linalg.norm(right_values)
                if denominator > 0.0:
                    similarity = float((left_values @ right_values) / denominator)
                    similarities[left, right] = similarities[right, left] = similarity
        self.similarities_ = similarities
        return self

    def _require_fitted(
        self,
    ) -> tuple[NDArray, NDArray, FloatArray, FloatArray, FloatArray]:
        fitted = (
            self.user_ids_,
            self.item_ids_,
            self.ratings_,
            self.user_means_,
            self.similarities_,
        )
        if any(value is None for value in fitted):
            raise RuntimeError("fit must be called before requesting recommendations")
        return fitted  # type: ignore[return-value]

    @staticmethod
    def _lookup(identifier: object, known: NDArray, kind: str) -> int:
        matches = np.flatnonzero(known == identifier)
        if len(matches) != 1:
            raise KeyError(f"unknown {kind}: {identifier!r}")
        return int(matches[0])

    def similar_items(
        self, item_id: object, *, n: int = 5
    ) -> tuple[NDArray, FloatArray]:
        """Return the most positively similar item identifiers and scores."""

        if n <= 0:
            raise ValueError("n must be positive")
        _, item_ids, _, _, similarities = self._require_fitted()
        item_index = self._lookup(item_id, item_ids, "item_id")
        scores = similarities[item_index].copy()
        scores[item_index] = -np.inf
        ordering = np.argsort(-scores, kind="mergesort")
        positive = np.isfinite(scores[ordering]) & (scores[ordering] > 0.0)
        ordering = ordering[positive][:n]
        return item_ids[ordering], scores[ordering]

    def recommend(
        self, user_id: object, *, n: int = 5
    ) -> tuple[NDArray, FloatArray]:
        """Recommend unseen items using positively similar rated neighbors."""

        if n <= 0:
            raise ValueError("n must be positive")
        user_ids, item_ids, ratings, user_means, similarities = self._require_fitted()
        user_index = self._lookup(user_id, user_ids, "user_id")
        rated_indices = np.flatnonzero(np.isfinite(ratings[user_index]))
        candidate_indices = np.flatnonzero(~np.isfinite(ratings[user_index]))
        centered_ratings = ratings[user_index, rated_indices] - user_means[user_index]
        predictions: list[tuple[int, float]] = []

        for candidate_index in candidate_indices:
            candidate_similarities = similarities[candidate_index, rated_indices]
            supported = np.flatnonzero(candidate_similarities > 0.0)
            if len(supported) == 0:
                continue
            strongest = supported[
                np.argsort(-candidate_similarities[supported], kind="mergesort")[
                    : self.n_neighbors
                ]
            ]
            weights = candidate_similarities[strongest]
            prediction = user_means[user_index] + float(
                weights @ centered_ratings[strongest] / np.sum(np.abs(weights))
            )
            predictions.append((candidate_index, prediction))

        predictions.sort(key=lambda pair: (-pair[1], str(item_ids[pair[0]])))
        selected = predictions[:n]
        indices = np.array([pair[0] for pair in selected], dtype=np.int64)
        scores = np.array([pair[1] for pair in selected], dtype=float)
        return item_ids[indices], scores
