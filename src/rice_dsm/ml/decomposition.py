"""Inspectable dimensionality-reduction tools used in Lecture 16."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray


class PrincipalComponentProjector:
    """Project centered observations onto leading principal directions.

    Parameters
    ----------
    n_components
        Number of principal directions to retain. It must be between one and
        ``min(n_samples, n_features)`` when :meth:`fit` is called.

    Notes
    -----
    Rows are observations and columns are numerical features. The class centers
    but does not standardize features; scaling is a separate scientific choice.
    It uses the singular value decomposition of the centered design matrix and
    fixes each component's otherwise arbitrary sign for reproducible teaching
    output.
    """

    def __init__(self, n_components: int):
        if isinstance(n_components, bool) or not isinstance(n_components, int):
            raise TypeError("n_components must be an integer.")
        if n_components < 1:
            raise ValueError("n_components must be at least one.")
        self.n_components = n_components

    @staticmethod
    def _validated_matrix(observations: ArrayLike) -> NDArray[np.float64]:
        matrix = np.asarray(observations, dtype=float)
        if matrix.ndim != 2:
            raise ValueError("observations must be a two-dimensional matrix.")
        if matrix.shape[0] < 2 or matrix.shape[1] < 1:
            raise ValueError(
                "observations must contain at least two rows and one feature."
            )
        if not np.isfinite(matrix).all():
            raise ValueError("observations must contain only finite values.")
        return matrix

    def fit(self, observations: ArrayLike) -> PrincipalComponentProjector:
        """Learn principal directions from observations.

        Parameters
        ----------
        observations
            Matrix with shape ``(n_samples, n_features)``.

        Returns
        -------
        PrincipalComponentProjector
            The fitted projector.

        Raises
        ------
        ValueError
            If the requested rank exceeds the available matrix rank bound.
        """

        matrix = self._validated_matrix(observations)
        rank_bound = min(matrix.shape)
        if self.n_components > rank_bound:
            raise ValueError(
                "n_components cannot exceed min(n_samples, n_features)."
            )

        self.n_features_in_ = matrix.shape[1]
        self.mean_ = matrix.mean(axis=0)
        centered = matrix - self.mean_
        _, singular_values, right_vectors = np.linalg.svd(
            centered, full_matrices=False
        )

        # A singular vector and its negative describe the same axis. Choose the
        # sign whose largest-magnitude loading is positive for stable displays.
        for row in right_vectors:
            pivot = int(np.argmax(np.abs(row)))
            if row[pivot] < 0:
                row *= -1

        all_variances = singular_values**2 / (matrix.shape[0] - 1)
        total_variance = all_variances.sum()
        self.components_ = right_vectors[: self.n_components].copy()
        self.singular_values_ = singular_values[: self.n_components].copy()
        self.explained_variance_ = all_variances[: self.n_components].copy()
        self.explained_variance_ratio_ = (
            self.explained_variance_ / total_variance
        )
        return self

    def _require_fitted(self) -> None:
        if not hasattr(self, "components_"):
            raise RuntimeError("Call fit before using this projector.")

    def transform(self, observations: ArrayLike) -> NDArray[np.float64]:
        """Map observations into principal-component coordinates."""

        self._require_fitted()
        matrix = self._validated_matrix(observations)
        if matrix.shape[1] != self.n_features_in_:
            raise ValueError(
                f"Expected {self.n_features_in_} features; received "
                f"{matrix.shape[1]}."
            )
        return (matrix - self.mean_) @ self.components_.T

    def fit_transform(self, observations: ArrayLike) -> NDArray[np.float64]:
        """Fit the projector and return component coordinates."""

        return self.fit(observations).transform(observations)

    def inverse_transform(self, scores: ArrayLike) -> NDArray[np.float64]:
        """Reconstruct feature-space observations from component scores."""

        self._require_fitted()
        matrix = np.asarray(scores, dtype=float)
        if matrix.ndim != 2 or matrix.shape[1] != self.n_components:
            raise ValueError(
                f"scores must have shape (n_samples, {self.n_components})."
            )
        if not np.isfinite(matrix).all():
            raise ValueError("scores must contain only finite values.")
        return matrix @ self.components_ + self.mean_

    def reconstruction_error(self, observations: ArrayLike) -> float:
        """Return mean squared reconstruction error per matrix entry."""

        matrix = self._validated_matrix(observations)
        reconstructed = self.inverse_transform(self.transform(matrix))
        return float(np.mean((matrix - reconstructed) ** 2))
