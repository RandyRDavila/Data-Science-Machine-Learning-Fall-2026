"""Unit, property, metamorphic, and doctest contracts for scientific metrics."""

import doctest
from math import sqrt

import pytest

from rice_dsm import mean_absolute_error, metrics, root_mean_squared_error


def test_mean_absolute_error_matches_hand_calculation() -> None:
    assert mean_absolute_error([1.0, 3.0], [2.0, 5.0]) == 1.5


def test_root_mean_squared_error_matches_hand_calculation() -> None:
    assert root_mean_squared_error([0.0, 0.0], [3.0, 4.0]) == pytest.approx(
        sqrt(12.5)
    )


@pytest.mark.parametrize("metric", [mean_absolute_error, root_mean_squared_error])
def test_metric_is_zero_for_identical_values(metric: object) -> None:
    assert callable(metric)
    assert metric([1.0, -2.0, 4.5], [1.0, -2.0, 4.5]) == 0.0


@pytest.mark.parametrize("metric", [mean_absolute_error, root_mean_squared_error])
def test_metric_accepts_one_pass_iterables(metric: object) -> None:
    assert callable(metric)
    observed = (value for value in [1.0, 2.0])
    predicted = (value for value in [2.0, 4.0])

    assert metric(observed, predicted) > 0.0


@pytest.mark.parametrize("metric", [mean_absolute_error, root_mean_squared_error])
def test_metric_rejects_empty_inputs(metric: object) -> None:
    assert callable(metric)
    with pytest.raises(ValueError, match="at least one"):
        metric([], [])


@pytest.mark.parametrize("metric", [mean_absolute_error, root_mean_squared_error])
def test_metric_rejects_unequal_lengths(metric: object) -> None:
    assert callable(metric)
    with pytest.raises(ValueError, match="equal lengths"):
        metric([1.0], [1.0, 2.0])


@pytest.mark.parametrize("invalid_value", [float("nan"), float("inf")])
def test_metric_rejects_nonfinite_observations(invalid_value: float) -> None:
    with pytest.raises(ValueError, match=r"observed\[0\] must be finite"):
        mean_absolute_error([invalid_value], [0.0])


def test_mean_absolute_error_is_symmetric() -> None:
    observed = [-2.0, 1.0, 8.0]
    predicted = [0.0, 4.0, 7.0]

    assert mean_absolute_error(observed, predicted) == mean_absolute_error(
        predicted, observed
    )


def test_mean_absolute_error_is_translation_invariant() -> None:
    observed = [-2.0, 1.0, 8.0]
    predicted = [0.0, 4.0, 7.0]
    offset = 1_000.0

    baseline = mean_absolute_error(observed, predicted)
    translated = mean_absolute_error(
        [value + offset for value in observed],
        [value + offset for value in predicted],
    )

    assert translated == baseline


def test_metric_docstring_examples_execute() -> None:
    results = doctest.testmod(metrics)

    assert results.failed == 0
    assert results.attempted >= 3
