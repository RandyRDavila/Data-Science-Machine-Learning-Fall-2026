"""Mathematical, interface, and failure contracts for Lecture 15 ensembles."""

import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier as SklearnRandomForest

from rice_dsm.ml.ensembles import (
    RandomForestClassifier,
    SquaredErrorGradientBoostingRegressor,
    bootstrap_indices,
)


def test_bootstrap_indices_are_reproducible_and_allow_repetition() -> None:
    first = bootstrap_indices(20, random_state=438)
    second = bootstrap_indices(20, random_state=438)

    np.testing.assert_array_equal(first, second)
    assert first.shape == (20,)
    assert first.min() >= 0 and first.max() < 20
    assert np.unique(first).size < first.size


def test_bootstrap_rejects_an_empty_population() -> None:
    with pytest.raises(ValueError, match="positive"):
        bootstrap_indices(0)


def test_forest_averages_probabilities_and_computes_oob_evidence() -> None:
    features = np.array([[0, 0], [0, 1], [1, 0], [1, 1]] * 12, dtype=float)
    labels = (features[:, 0] > 0).astype(int)
    model = RandomForestClassifier(
        n_estimators=25, max_depth=3, random_state=438
    ).fit(features, labels)

    probabilities = model.predict_proba(features)
    assert probabilities.shape == (48, 2)
    np.testing.assert_allclose(probabilities.sum(axis=1), 1.0)
    assert np.mean(model.predict(features) == labels) > 0.95
    assert np.all(model.oob_counts_ > 0)
    assert model.oob_score_ > 0.9
    assert model.feature_importances_.sum() == pytest.approx(1.0)


def test_forest_is_reproducible_and_agrees_with_trusted_behavior() -> None:
    generator = np.random.default_rng(577)
    features = generator.normal(size=(120, 4))
    labels = (features[:, 0] - 0.4 * features[:, 1] > 0).astype(int)
    ours_a = RandomForestClassifier(n_estimators=40, random_state=12).fit(
        features, labels
    )
    ours_b = RandomForestClassifier(n_estimators=40, random_state=12).fit(
        features, labels
    )
    trusted = SklearnRandomForest(
        n_estimators=40, max_features="sqrt", random_state=12
    ).fit(features, labels)

    np.testing.assert_allclose(
        ours_a.predict_proba(features), ours_b.predict_proba(features)
    )
    assert np.mean(ours_a.predict(features) == trusted.predict(features)) > 0.95


def test_squared_error_boosting_fits_successive_residuals() -> None:
    features = np.arange(10, dtype=float).reshape(-1, 1)
    targets = np.where(features[:, 0] < 5, 2.0, 8.0)
    model = SquaredErrorGradientBoostingRegressor(
        n_estimators=8, learning_rate=0.5, max_depth=1
    ).fit(features, targets)

    staged = list(model.staged_predict(features))
    assert model.initial_prediction_ == pytest.approx(5.0)
    assert len(staged) == 8
    assert model.training_loss_[-1] < model.training_loss_[0]
    assert np.mean((targets - model.predict(features)) ** 2) < 0.01


@pytest.mark.parametrize(
    "estimator",
    [RandomForestClassifier(), SquaredErrorGradientBoostingRegressor()],
)
def test_prediction_before_fit_has_a_clear_error(estimator) -> None:
    with pytest.raises(RuntimeError, match="fit must be called"):
        estimator.predict([[0.0]])


@pytest.mark.parametrize(
    "constructor, message",
    [
        (lambda: RandomForestClassifier(n_estimators=0), "positive"),
        (
            lambda: SquaredErrorGradientBoostingRegressor(learning_rate=0),
            "learning_rate",
        ),
        (
            lambda: SquaredErrorGradientBoostingRegressor(max_depth=0),
            "depth",
        ),
    ],
)
def test_hyperparameter_contracts_fail_early(constructor, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        constructor()
