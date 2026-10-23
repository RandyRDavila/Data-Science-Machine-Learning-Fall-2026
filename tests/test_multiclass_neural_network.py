"""Contracts for the from-scratch multiclass neural-network lesson."""

import hashlib
from pathlib import Path

import numpy as np
import pytest

from rice_dsm.ml.multiclass import (
    MultilayerPerceptronClassifier,
    one_hot,
    softmax,
    softmax_cross_entropy,
)

PROJECT_ROOT = Path(__file__).parents[1]
MNIST_SAMPLE_SHA256 = (
    "16b57f334fb1b378baf07f5ae79fc9f46261525dd2fddaa6c7a19ac581a7b279"
)


def test_versioned_mnist_sample_is_balanced_and_has_expected_contract() -> None:
    dataset_path = PROJECT_ROOT / "data" / "mnist_teaching_sample.npz"
    with np.load(dataset_path) as archive:
        train_images = archive["x_train"]
        train_labels = archive["y_train"]
        test_images = archive["x_test"]
        test_labels = archive["y_test"]

    assert train_images.shape == (2_400, 28, 28)
    assert test_images.shape == (600, 28, 28)
    assert train_images.dtype == test_images.dtype == np.uint8
    np.testing.assert_array_equal(np.bincount(train_labels), np.full(10, 240))
    np.testing.assert_array_equal(np.bincount(test_labels), np.full(10, 60))


def test_versioned_mnist_sample_matches_reviewed_authentic_artifact() -> None:
    dataset_path = PROJECT_ROOT / "data" / "mnist_teaching_sample.npz"

    digest = hashlib.sha256(dataset_path.read_bytes()).hexdigest()

    assert digest == MNIST_SAMPLE_SHA256


def test_one_hot_preserves_class_identity_and_rejects_invalid_labels() -> None:
    encoded = one_hot(np.array([2, 0, 1]), n_classes=4)

    assert encoded.shape == (3, 4)
    np.testing.assert_array_equal(encoded.argmax(axis=1), [2, 0, 1])
    np.testing.assert_array_equal(encoded.sum(axis=1), np.ones(3))
    with pytest.raises(ValueError, match="integers"):
        one_hot(np.array([0.0, 1.0]), n_classes=2)
    with pytest.raises(ValueError, match=r"\[0, 3\)"):
        one_hot(np.array([0, 3]), n_classes=3)


def test_softmax_is_shift_invariant_and_numerically_stable() -> None:
    logits = np.array([[1_000.0, 1_001.0, 999.0], [-1_000.0, -999.0, -1_002.0]])
    probabilities = softmax(logits)

    assert np.isfinite(probabilities).all()
    np.testing.assert_allclose(probabilities.sum(axis=1), 1.0)
    np.testing.assert_allclose(softmax(logits + 9_999.0), probabilities)


def test_softmax_cross_entropy_gradient_matches_central_differences() -> None:
    logits = np.array([[0.3, -0.2, 0.7], [-0.1, 0.6, 0.2]])
    targets = one_hot(np.array([2, 1]), n_classes=3)
    _, analytical = softmax_cross_entropy(logits, targets)
    numerical = np.zeros_like(logits)
    step = 1e-6

    for index in np.ndindex(logits.shape):
        positive = logits.copy()
        negative = logits.copy()
        positive[index] += step
        negative[index] -= step
        loss_positive, _ = softmax_cross_entropy(positive, targets)
        loss_negative, _ = softmax_cross_entropy(negative, targets)
        numerical[index] = (loss_positive - loss_negative) / (2 * step)

    np.testing.assert_allclose(analytical, numerical, rtol=1e-6, atol=1e-8)


def test_mlp_initialization_matches_fan_in_scaling() -> None:
    model = MultilayerPerceptronClassifier((1_000, 800, 10), random_state=4)

    hidden_standard_deviation = np.std(model.weights_[0])
    output_standard_deviation = np.std(model.weights_[1])
    assert hidden_standard_deviation == pytest.approx(np.sqrt(2 / 1_000), rel=0.03)
    assert output_standard_deviation == pytest.approx(np.sqrt(1 / 800), rel=0.08)
    assert np.count_nonzero(model.biases_[0]) == 0


def test_mlp_backpropagation_gradient_matches_central_differences() -> None:
    features = np.array([[0.2, -0.1], [0.7, 0.4], [-0.4, 0.6]])
    labels = np.array([0, 1, 2])
    model = MultilayerPerceptronClassifier(
        (2, 3, 3), learning_rate=0.1, random_state=8
    )
    _, weight_gradients, _ = model.loss_and_gradients(features, labels)
    step = 1e-6
    numerical = np.zeros_like(model.weights_[0])

    for index in np.ndindex(model.weights_[0].shape):
        original = model.weights_[0][index]
        model.weights_[0][index] = original + step
        loss_positive, _, _ = model.loss_and_gradients(features, labels)
        model.weights_[0][index] = original - step
        loss_negative, _, _ = model.loss_and_gradients(features, labels)
        model.weights_[0][index] = original
        numerical[index] = (loss_positive - loss_negative) / (2 * step)

    np.testing.assert_allclose(
        weight_gradients[0], numerical, rtol=2e-5, atol=1e-7
    )


def test_mlp_learns_a_small_nonlinear_multiclass_problem() -> None:
    features = np.array(
        [
            [-1.1, -0.9],
            [-0.8, -1.2],
            [1.1, -0.9],
            [0.8, -1.1],
            [0.0, 1.1],
            [0.2, 0.8],
        ]
    )
    labels = np.array([0, 0, 1, 1, 2, 2])
    model = MultilayerPerceptronClassifier(
        (2, 8, 3), learning_rate=0.12, random_state=12
    ).fit(features, labels, epochs=120, batch_size=3)

    assert model.history_["loss"][-1] < model.history_["loss"][0]
    assert model.score(features, labels) == pytest.approx(1.0)
    np.testing.assert_allclose(model.predict_proba(features).sum(axis=1), 1.0)
