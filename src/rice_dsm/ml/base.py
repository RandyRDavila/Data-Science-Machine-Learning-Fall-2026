"""Structural interfaces for interoperable course algorithms."""

from __future__ import annotations

from typing import Any, Protocol, Self, runtime_checkable

from numpy.typing import ArrayLike, NDArray


@runtime_checkable
class SupervisedPredictor(Protocol):
    """Protocol shared by fitted regression and classification estimators.

    Notes
    -----
    This is a structural interface: an implementation satisfies it by exposing
    compatible ``fit`` and ``predict`` methods. Student algorithms do not need
    to inherit from a course base class. More specific mathematical contracts,
    fitted attributes, randomness, and validation belong to each estimator.
    """

    def fit(self, features: ArrayLike, targets: ArrayLike) -> Self:
        """Fit the estimator and return the fitted object.

        Parameters
        ----------
        features
            Two-dimensional observations-by-features data.
        targets
            One target value or label per observation.

        Returns
        -------
        Self
            The fitted estimator.
        """

        ...
    def predict(self, features: ArrayLike) -> NDArray[Any]:
        """Predict one value or label per observation.

        Parameters
        ----------
        features
            Two-dimensional observations-by-features data.

        Returns
        -------
        numpy.ndarray
            One-dimensional predictions in observation order.
        """

        ...


@runtime_checkable
class Transformer(Protocol):
    """Protocol for fitted preprocessing and representation transformations."""

    def fit(self, features: ArrayLike, targets: ArrayLike | None = None) -> Self:
        """Learn transformation state from training observations."""

        ...

    def transform(self, features: ArrayLike) -> NDArray[Any]:
        """Transform observations using only previously fitted state."""

        ...


@runtime_checkable
class Clusterer(Protocol):
    """Protocol for algorithms that assign observations to learned clusters."""

    def fit(self, features: ArrayLike) -> Self:
        """Learn cluster structure from observations."""

        ...

    def predict(self, features: ArrayLike) -> NDArray[Any]:
        """Assign observations to clusters using fitted state."""

        ...
