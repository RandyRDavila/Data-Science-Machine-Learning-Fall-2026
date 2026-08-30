"""Small dependency-free metrics used to teach testing and numerical contracts."""

from __future__ import annotations

from collections.abc import Iterable
from math import fsum, isfinite, sqrt
from numbers import Real


def _finite_values(values: Iterable[float], *, parameter: str) -> tuple[float, ...]:
    """Validate and materialize one numeric iterable."""

    try:
        raw_values = tuple(values)
    except TypeError as error:
        raise TypeError(f"{parameter} must be an iterable of real numbers") from error

    finite_values: list[float] = []
    for index, value in enumerate(raw_values):
        if isinstance(value, bool) or not isinstance(value, Real):
            raise TypeError(f"{parameter}[{index}] must be a real number")
        converted = float(value)
        if not isfinite(converted):
            raise ValueError(f"{parameter}[{index}] must be finite")
        finite_values.append(converted)
    return tuple(finite_values)


def _paired_values(
    observed: Iterable[float],
    predicted: Iterable[float],
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Validate two equally sized, nonempty numeric iterables."""

    observed_values = _finite_values(observed, parameter="observed")
    predicted_values = _finite_values(predicted, parameter="predicted")
    if not observed_values:
        raise ValueError("observed and predicted must contain at least one value")
    if len(observed_values) != len(predicted_values):
        raise ValueError("observed and predicted must have equal lengths")
    return observed_values, predicted_values


def mean_absolute_error(
    observed: Iterable[float],
    predicted: Iterable[float],
) -> float:
    """Compute the mean absolute prediction error.

    Parameters
    ----------
    observed : iterable of float
        Finite observed values.
    predicted : iterable of float
        Finite predictions aligned one-to-one with ``observed``.

    Returns
    -------
    float
        Arithmetic mean of ``abs(observed - predicted)``. The result is
        nonnegative and has the same physical unit as the inputs.

    Raises
    ------
    TypeError
        If either input is not an iterable of real, non-Boolean values.
    ValueError
        If inputs are empty, unequal in length, or contain non-finite values.

    Examples
    --------
    >>> mean_absolute_error([1.0, 3.0], [2.0, 5.0])
    1.5
    >>> mean_absolute_error([], [])
    Traceback (most recent call last):
        ...
    ValueError: observed and predicted must contain at least one value
    """

    observed_values, predicted_values = _paired_values(observed, predicted)
    total_error = fsum(
        abs(actual - estimate)
        for actual, estimate in zip(observed_values, predicted_values, strict=True)
    )
    return total_error / len(observed_values)


def root_mean_squared_error(
    observed: Iterable[float],
    predicted: Iterable[float],
) -> float:
    """Compute the root mean squared prediction error.

    Parameters
    ----------
    observed : iterable of float
        Finite observed values.
    predicted : iterable of float
        Finite predictions aligned one-to-one with ``observed``.

    Returns
    -------
    float
        Square root of the mean squared error, in the inputs' physical unit.

    Raises
    ------
    TypeError
        If either input is not an iterable of real, non-Boolean values.
    ValueError
        If inputs are empty, unequal in length, or contain non-finite values.

    Examples
    --------
    >>> root_mean_squared_error([0.0, 0.0], [3.0, 4.0])
    3.5355339059327378
    """

    observed_values, predicted_values = _paired_values(observed, predicted)
    squared_error = fsum(
        (actual - estimate) ** 2
        for actual, estimate in zip(observed_values, predicted_values, strict=True)
    )
    return sqrt(squared_error / len(observed_values))
