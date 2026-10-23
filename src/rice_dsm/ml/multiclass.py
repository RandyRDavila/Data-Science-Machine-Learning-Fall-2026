"""Transparent multiclass neural-network components for teaching.

The implementation is deliberately small enough to audit.  It provides the
modern mathematical contract used by a dense classifier--ReLU hidden units,
raw output logits, and fused softmax cross-entropy--without attempting to be a
general deep-learning framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Self

import numpy as np
from numpy.typing import ArrayLike, NDArray

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]


def one_hot(labels: ArrayLike, n_classes: int) -> FloatArray:
    """Encode integer class labels as rows of indicator values.

    Parameters
    ----------
    labels
        One-dimensional integer labels in ``[0, n_classes)``.
    n_classes
        Total number of possible classes, including classes absent from this
        particular batch.
    """

    raw = np.asarray(labels)
    if raw.ndim != 1 or raw.size == 0:
        raise ValueError("labels must be a nonempty one-dimensional array")
    if n_classes <= 1:
        raise ValueError("n_classes must be at least 2")
    if not np.issubdtype(raw.dtype, np.integer):
        raise ValueError("labels must contain integers")
    encoded_labels = raw.astype(np.int64, copy=False)
    if np.any(encoded_labels < 0) or np.any(encoded_labels >= n_classes):
        raise ValueError(f"labels must lie in [0, {n_classes})")

    encoded = np.zeros((len(encoded_labels), n_classes), dtype=float)
    encoded[np.arange(len(encoded_labels)), encoded_labels] = 1.0
    return encoded


def softmax(logits: ArrayLike) -> FloatArray:
    """Convert a matrix of logits to stable categorical probabilities."""

    scores = np.asarray(logits, dtype=float)
    if scores.ndim != 2 or scores.shape[0] == 0 or scores.shape[1] < 2:
        raise ValueError("logits must have shape (n_observations, n_classes)")
    if not np.isfinite(scores).all():
        raise ValueError("logits must contain only finite values")

    shifted = scores - scores.max(axis=1, keepdims=True)
    exponentials = np.exp(shifted)
    return exponentials / exponentials.sum(axis=1, keepdims=True)


def softmax_cross_entropy(
    logits: ArrayLike, targets: ArrayLike
) -> tuple[float, FloatArray]:
    """Return mean softmax cross-entropy and its logit gradient.

    The calculation uses log-sum-exp rather than taking the logarithm of
    rounded probabilities.  ``gradient`` is already divided by batch size, so
    parameter gradients formed from it correspond to the returned mean loss.
    """

    scores = np.asarray(logits, dtype=float)
    expected = np.asarray(targets, dtype=float)
    if scores.ndim != 2 or scores.shape != expected.shape or scores.shape[0] == 0:
        raise ValueError("logits and targets must have the same nonempty 2D shape")
    if not np.isfinite(scores).all() or not np.isfinite(expected).all():
        raise ValueError("logits and targets must contain only finite values")
    if not np.allclose(expected.sum(axis=1), 1.0) or np.any(expected < 0.0):
        raise ValueError("each target row must be a probability distribution")

    maximum = scores.max(axis=1, keepdims=True)
    log_partition = maximum + np.log(
        np.exp(scores - maximum).sum(axis=1, keepdims=True)
    )
    losses = log_partition[:, 0] - np.sum(expected * scores, axis=1)
    probabilities = np.exp(scores - log_partition)
    gradient = (probabilities - expected) / len(scores)
    return float(np.mean(losses)), gradient


def _feature_matrix(features: ArrayLike, n_features: int | None = None) -> FloatArray:
    matrix = np.asarray(features, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] == 0 or matrix.shape[1] == 0:
        raise ValueError("features must have shape (n_observations, n_features)")
    if n_features is not None and matrix.shape[1] != n_features:
        raise ValueError(f"features must contain {n_features} columns")
    if not np.isfinite(matrix).all():
        raise ValueError("features must contain only finite values")
    return matrix


@dataclass
class MultilayerPerceptronClassifier:
    """Fit a small dense multiclass network by mini-batch gradient descent.

    Parameters
    ----------
    layer_widths
        Input width, zero or more hidden widths, and output class count.
    learning_rate
        Positive mini-batch gradient-descent step size.
    random_state
        Seed controlling initialization and epoch shuffling.

    Notes
    -----
    Hidden layers use ReLU and He normal initialization.  The output layer uses
    Xavier normal initialization and emits logits consumed by stable softmax
    cross-entropy.  This is an inspectable teaching model, not a replacement
    for TensorFlow, PyTorch, or JAX.
    """

    layer_widths: tuple[int, ...]
    learning_rate: float = 0.08
    random_state: int = 438
    weights_: list[FloatArray] = field(default_factory=list, init=False)
    biases_: list[FloatArray] = field(default_factory=list, init=False)
    history_: dict[str, list[float]] = field(default_factory=dict, init=False)
    _generator: np.random.Generator = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if len(self.layer_widths) < 2 or any(width <= 0 for width in self.layer_widths):
            raise ValueError("layer_widths needs positive input and output widths")
        if self.layer_widths[-1] < 2:
            raise ValueError("the output layer needs at least two classes")
        if self.learning_rate <= 0:
            raise ValueError("learning_rate must be positive")
        self._generator = np.random.default_rng(self.random_state)
        self._initialize_parameters()

    @property
    def n_features_in_(self) -> int:
        """Number of scalar input features expected by the network."""

        return self.layer_widths[0]

    @property
    def n_classes_(self) -> int:
        """Number of mutually exclusive output classes."""

        return self.layer_widths[-1]

    def _initialize_parameters(self) -> None:
        self.weights_ = []
        self.biases_ = []
        last_connection = len(self.layer_widths) - 2
        for index, (fan_in, fan_out) in enumerate(
            zip(self.layer_widths[:-1], self.layer_widths[1:], strict=True)
        ):
            # ReLU retains roughly half of a symmetric signal, motivating He
            # scale sqrt(2/fan_in).  The linear-logit output uses Xavier scale.
            variance_numerator = 1.0 if index == last_connection else 2.0
            scale = np.sqrt(variance_numerator / fan_in)
            self.weights_.append(
                self._generator.normal(0.0, scale, size=(fan_in, fan_out))
            )
            self.biases_.append(np.zeros(fan_out, dtype=float))

    def forward(
        self, features: ArrayLike, *, retain_cache: bool = False
    ) -> FloatArray | tuple[FloatArray, tuple[list[FloatArray], list[FloatArray]]]:
        """Return output logits, optionally with activations and preactivations."""

        activation = _feature_matrix(features, self.n_features_in_)
        activations = [activation]
        preactivations: list[FloatArray] = []
        for index, (weights, biases) in enumerate(
            zip(self.weights_, self.biases_, strict=True)
        ):
            preactivation = activation @ weights + biases
            preactivations.append(preactivation)
            activation = (
                preactivation
                if index == len(self.weights_) - 1
                else np.maximum(preactivation, 0.0)
            )
            activations.append(activation)
        if retain_cache:
            return activation, (activations, preactivations)
        return activation

    def loss_and_gradients(
        self, features: ArrayLike, labels: ArrayLike
    ) -> tuple[float, list[FloatArray], list[FloatArray]]:
        """Evaluate a batch loss and backpropagate every parameter gradient."""

        matrix = _feature_matrix(features, self.n_features_in_)
        targets = one_hot(labels, self.n_classes_)
        if len(targets) != len(matrix):
            raise ValueError("features and labels must contain equal observations")
        logits, (activations, preactivations) = self.forward(
            matrix, retain_cache=True
        )
        loss, upstream = softmax_cross_entropy(logits, targets)
        weight_gradients = [np.empty_like(weights) for weights in self.weights_]
        bias_gradients = [np.empty_like(biases) for biases in self.biases_]

        for layer_index in range(len(self.weights_) - 1, -1, -1):
            weight_gradients[layer_index] = activations[layer_index].T @ upstream
            bias_gradients[layer_index] = upstream.sum(axis=0)
            if layer_index:
                upstream = upstream @ self.weights_[layer_index].T
                upstream = upstream * (preactivations[layer_index - 1] > 0.0)
        return loss, weight_gradients, bias_gradients

    def fit(
        self,
        features: ArrayLike,
        labels: ArrayLike,
        *,
        epochs: int = 8,
        batch_size: int = 64,
        validation_data: tuple[ArrayLike, ArrayLike] | None = None,
    ) -> Self:
        """Train with shuffled mini-batches and record epoch-level evidence."""

        matrix = _feature_matrix(features, self.n_features_in_)
        label_vector = np.asarray(labels)
        one_hot(label_vector, self.n_classes_)
        if len(label_vector) != len(matrix):
            raise ValueError("features and labels must contain equal observations")
        if epochs <= 0 or batch_size <= 0:
            raise ValueError("epochs and batch_size must be positive")

        validation: tuple[FloatArray, IntArray] | None = None
        if validation_data is not None:
            validation_matrix = _feature_matrix(
                validation_data[0], self.n_features_in_
            )
            validation_labels = np.asarray(validation_data[1])
            one_hot(validation_labels, self.n_classes_)
            if len(validation_matrix) != len(validation_labels):
                raise ValueError("validation features and labels must align")
            validation = (
                validation_matrix,
                validation_labels.astype(np.int64, copy=False),
            )

        self.history_ = {"loss": [], "accuracy": [], "validation_accuracy": []}
        for _ in range(epochs):
            ordering = self._generator.permutation(len(matrix))
            for start in range(0, len(matrix), batch_size):
                batch_indices = ordering[start : start + batch_size]
                _, weight_gradients, bias_gradients = self.loss_and_gradients(
                    matrix[batch_indices], label_vector[batch_indices]
                )
                for index in range(len(self.weights_)):
                    self.weights_[index] -= self.learning_rate * weight_gradients[index]
                    self.biases_[index] -= self.learning_rate * bias_gradients[index]

            epoch_logits = self.forward(matrix)
            epoch_targets = one_hot(label_vector, self.n_classes_)
            epoch_loss, _ = softmax_cross_entropy(epoch_logits, epoch_targets)
            self.history_["loss"].append(epoch_loss)
            self.history_["accuracy"].append(
                float(np.mean(epoch_logits.argmax(axis=1) == label_vector))
            )
            if validation is not None:
                self.history_["validation_accuracy"].append(
                    self.score(*validation)
                )
        return self

    def predict_proba(self, features: ArrayLike) -> FloatArray:
        """Return one normalized probability distribution per observation."""

        return softmax(self.forward(features))

    def predict(self, features: ArrayLike) -> IntArray:
        """Return the largest-probability class label for each observation."""

        return self.predict_proba(features).argmax(axis=1).astype(np.int64)

    def score(self, features: ArrayLike, labels: ArrayLike) -> float:
        """Return classification accuracy."""

        expected = np.asarray(labels)
        if expected.ndim != 1:
            raise ValueError("labels must be one-dimensional")
        prediction = self.predict(features)
        if prediction.shape != expected.shape:
            raise ValueError("features and labels must contain equal observations")
        return float(np.mean(prediction == expected))
