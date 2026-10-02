"""Executable contracts for the inspectable neuron and network API."""

import numpy as np
import pytest

from rice_dsm.ml.neural import (
    DenseLayer,
    Identity,
    LinearSVM,
    LogisticCrossEntropy,
    MeanSquaredNetwork,
    Sigmoid,
    SingleNeuron,
    SquaredErrorRegression,
    half_mean_squared_error,
)


def test_sigmoid_is_stable_and_its_derivative_matches_finite_differences() -> None:
    sigmoid = Sigmoid()
    scores = np.array([-1_000.0, -1.3, 0.0, 2.1, 1_000.0])
    values = sigmoid.forward(scores)

    assert np.isfinite(values).all()
    assert values[0] == pytest.approx(0.0)
    assert values[-1] == pytest.approx(1.0)

    interior = scores[1:-1]
    step = 1e-6
    finite_difference = (
        sigmoid.forward(interior + step) - sigmoid.forward(interior - step)
    ) / (2 * step)
    np.testing.assert_allclose(
        sigmoid.derivative(interior), finite_difference, rtol=1e-6
    )


def test_canonical_single_neuron_objectives_share_residual_score_gradient() -> None:
    regression = SquaredErrorRegression()
    classification = LogisticCrossEntropy()
    regression_score = np.array([1.5, -0.5])
    regression_target = np.array([1.0, 0.0])
    classification_score = np.array([0.0, np.log(3.0)])
    classification_target = np.array([0.0, 1.0])

    np.testing.assert_allclose(
        regression.score_gradient(regression_score, regression_target),
        regression.prediction(regression_score) - regression_target,
    )
    np.testing.assert_allclose(
        classification.score_gradient(classification_score, classification_target),
        classification.prediction(classification_score) - classification_target,
    )


def test_single_neuron_fits_regression_and_classification_through_one_loop() -> None:
    regression_features = np.arange(6, dtype=float).reshape(-1, 1)
    regression_targets = 2.0 * regression_features[:, 0] - 1.0
    regressor = SingleNeuron(
        SquaredErrorRegression(), learning_rate=0.02, epochs=2_000
    ).fit(regression_features, regression_targets)
    mean_squared_error = np.mean(
        (regressor.predict(regression_features) - regression_targets) ** 2
    )
    assert mean_squared_error < 1e-6

    classification_features = np.array([[-2.0], [-1.0], [1.0], [2.0]])
    classification_targets = np.array([0.0, 0.0, 1.0, 1.0])
    classifier = SingleNeuron(
        LogisticCrossEntropy(), learning_rate=0.1, epochs=1_000
    ).fit(classification_features, classification_targets)
    assert np.array_equal(
        classifier.predict(classification_features) >= 0.5,
        classification_targets,
    )


def test_dense_layer_gradients_match_central_differences() -> None:
    layer = DenseLayer(2, 2, Sigmoid(), random_state=4)
    features = np.array([[0.2, -0.4], [1.1, 0.3]])
    target = np.array([[1.0, 0.0], [0.0, 1.0]])
    prediction = layer.forward(features)
    layer.backward((prediction - target) / len(features))
    analytical = layer.weight_gradient.copy()
    numerical = np.zeros_like(layer.weights)
    step = 1e-6

    for index in np.ndindex(layer.weights.shape):
        original = layer.weights[index]
        layer.weights[index] = original + step
        loss_plus = half_mean_squared_error(layer.forward(features), target)
        layer.weights[index] = original - step
        loss_minus = half_mean_squared_error(layer.forward(features), target)
        layer.weights[index] = original
        numerical[index] = (loss_plus - loss_minus) / (2 * step)

    np.testing.assert_allclose(analytical, numerical, rtol=1e-5, atol=1e-7)


def test_three_two_two_network_reduces_loss() -> None:
    features = np.array(
        [[0.0, 0.0, 1.0], [0.0, 1.0, 1.0], [1.0, 0.0, 1.0], [1.0, 1.0, 1.0]]
    )
    targets = np.array([[1.0, 0.0], [0.0, 1.0], [0.0, 1.0], [1.0, 0.0]])
    network = MeanSquaredNetwork(
        [DenseLayer(3, 2, Sigmoid(), 1), DenseLayer(2, 2, Sigmoid(), 2)]
    )
    initial = half_mean_squared_error(network.forward(features), targets)
    for _ in range(2_000):
        network.train_step(features, targets, learning_rate=1.0)
    final = half_mean_squared_error(network.forward(features), targets)

    assert final < 0.6 * initial


def test_shape_and_call_order_failures_are_actionable() -> None:
    layer = DenseLayer(2, 1, Identity())
    with pytest.raises(RuntimeError, match="forward must be called"):
        layer.backward(np.ones((1, 1)))
    with pytest.raises(ValueError, match="2 columns"):
        layer.forward(np.ones((3, 4)))


def test_linear_svm_learns_a_margin_classifier() -> None:
    features = np.array(
        [[-2.0, -1.0], [-1.0, -1.5], [1.0, 1.2], [2.0, 0.8]]
    )
    targets = np.array([-1.0, -1.0, 1.0, 1.0])
    classifier = LinearSVM(
        regularization_strength=0.01,
        learning_rate=0.05,
        epochs=2_000,
    ).fit(features, targets)

    assert np.array_equal(classifier.predict(features), targets)
    assert classifier.loss_history_[-1] < classifier.loss_history_[0]
    assert classifier.support_mask_.shape == targets.shape
    assert np.all(targets * classifier.decision_function(features) > 0)


def test_linear_svm_validates_labels_and_fitted_state() -> None:
    classifier = LinearSVM()
    with pytest.raises(RuntimeError, match="fitted"):
        classifier.predict(np.ones((2, 1)))
    with pytest.raises(ValueError, match=r"only -1 and \+1"):
        classifier.fit(np.ones((3, 1)), [0, 1, 1])
