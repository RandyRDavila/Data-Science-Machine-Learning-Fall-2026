"""Small, inspectable neural components used by the teaching laboratories.

The implementation favors visible mathematics and explicit shape contracts over
framework-like generality.  It is intentionally bounded: students can inspect
every derivative before moving to an automatic-differentiation framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, Self

import numpy as np
from numpy.typing import ArrayLike, NDArray

FloatArray = NDArray[np.float64]


class Activation(Protocol):
    """Contract for an elementwise activation function."""

    def forward(self, preactivation: FloatArray) -> FloatArray: ...

    def derivative(self, preactivation: FloatArray) -> FloatArray: ...


@dataclass(frozen=True)
class Identity:
    """Identity activation for unconstrained regression outputs."""

    def forward(self, preactivation: FloatArray) -> FloatArray:
        return preactivation.copy()

    def derivative(self, preactivation: FloatArray) -> FloatArray:
        return np.ones_like(preactivation)


@dataclass(frozen=True)
class Sigmoid:
    """Numerically stable logistic sigmoid activation."""

    def forward(self, preactivation: FloatArray) -> FloatArray:
        positive = preactivation >= 0
        result = np.empty_like(preactivation, dtype=float)
        result[positive] = 1.0 / (1.0 + np.exp(-preactivation[positive]))
        exp_z = np.exp(preactivation[~positive])
        result[~positive] = exp_z / (1.0 + exp_z)
        return result

    def derivative(self, preactivation: FloatArray) -> FloatArray:
        activation = self.forward(preactivation)
        return activation * (1.0 - activation)


@dataclass(frozen=True)
class ReLU:
    """Rectified linear activation with derivative zero at the kink."""

    def forward(self, preactivation: FloatArray) -> FloatArray:
        return np.maximum(preactivation, 0.0)

    def derivative(self, preactivation: FloatArray) -> FloatArray:
        return (preactivation > 0.0).astype(float)


class OutputObjective(Protocol):
    """Coupled output activation and loss for a single neuron."""

    def prediction(self, score: FloatArray) -> FloatArray: ...

    def mean_loss(self, score: FloatArray, target: FloatArray) -> float: ...

    def score_gradient(self, score: FloatArray, target: FloatArray) -> FloatArray: ...


@dataclass(frozen=True)
class SquaredErrorRegression:
    """Identity output with half mean-squared error."""

    def prediction(self, score: FloatArray) -> FloatArray:
        return score.copy()

    def mean_loss(self, score: FloatArray, target: FloatArray) -> float:
        return float(0.5 * np.mean((score - target) ** 2))

    def score_gradient(self, score: FloatArray, target: FloatArray) -> FloatArray:
        return score - target


@dataclass(frozen=True)
class LogisticCrossEntropy:
    """Sigmoid output with stable binary cross-entropy from logits."""

    sigmoid: Sigmoid = field(default_factory=Sigmoid)

    def prediction(self, score: FloatArray) -> FloatArray:
        return self.sigmoid.forward(score)

    def mean_loss(self, score: FloatArray, target: FloatArray) -> float:
        losses = np.logaddexp(0.0, score) - target * score
        return float(np.mean(losses))

    def score_gradient(self, score: FloatArray, target: FloatArray) -> FloatArray:
        return self.prediction(score) - target


def _observation_matrix(features: ArrayLike) -> FloatArray:
    matrix = np.asarray(features, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] == 0 or matrix.shape[1] == 0:
        raise ValueError("features must have shape (n_observations, n_features)")
    if not np.isfinite(matrix).all():
        raise ValueError("features must contain only finite values")
    return matrix


def _target_vector(targets: ArrayLike, n_observations: int) -> FloatArray:
    vector = np.asarray(targets, dtype=float)
    if vector.shape != (n_observations,):
        raise ValueError(f"targets must have shape ({n_observations},)")
    if not np.isfinite(vector).all():
        raise ValueError("targets must contain only finite values")
    return vector


@dataclass
class SingleNeuron:
    """Fit one affine neuron with a configurable output objective.

    Parameters
    ----------
    objective
        Coupled output activation and loss.  Canonical choices make the score
        gradient especially simple: residuals for both identity--squared-error
        regression and sigmoid--cross-entropy classification.
    learning_rate
        Positive full-batch gradient-descent step size.
    epochs
        Positive number of parameter updates.

    Notes
    -----
    This class is an estimator with ``fit`` and ``predict``.  A neuron inside a
    multilayer network is instead a computational component trained jointly
    through the network loss.
    """

    objective: OutputObjective
    learning_rate: float = 0.05
    epochs: int = 1_000
    weights_: FloatArray | None = field(default=None, init=False)
    bias_: float | None = field(default=None, init=False)
    loss_history_: list[float] = field(default_factory=list, init=False)

    def fit(self, features: ArrayLike, targets: ArrayLike) -> Self:
        matrix = _observation_matrix(features)
        target = _target_vector(targets, matrix.shape[0])
        if self.learning_rate <= 0:
            raise ValueError("learning_rate must be positive")
        if self.epochs <= 0:
            raise ValueError("epochs must be positive")
        if isinstance(self.objective, LogisticCrossEntropy) and not np.isin(
            target, [0.0, 1.0]
        ).all():
            raise ValueError("logistic targets must contain only 0 and 1")

        self.weights_ = np.zeros(matrix.shape[1], dtype=float)
        self.bias_ = 0.0
        self.loss_history_ = []
        for _ in range(self.epochs):
            score = matrix @ self.weights_ + self.bias_
            score_gradient = self.objective.score_gradient(score, target)
            self.weights_ -= (
                self.learning_rate * (matrix.T @ score_gradient) / len(matrix)
            )
            self.bias_ -= self.learning_rate * float(np.mean(score_gradient))
            updated_score = matrix @ self.weights_ + self.bias_
            self.loss_history_.append(self.objective.mean_loss(updated_score, target))
        return self

    def decision_function(self, features: ArrayLike) -> FloatArray:
        matrix = _observation_matrix(features)
        if self.weights_ is None or self.bias_ is None:
            raise RuntimeError("SingleNeuron must be fitted before prediction")
        if matrix.shape[1] != len(self.weights_):
            raise ValueError(f"features must contain {len(self.weights_)} columns")
        return matrix @ self.weights_ + self.bias_

    def predict(self, features: ArrayLike) -> FloatArray:
        return self.objective.prediction(self.decision_function(features))


@dataclass
class LinearSVM:
    """Fit a binary linear support vector machine by subgradient descent.

    Parameters
    ----------
    regularization_strength
        Positive coefficient multiplying ``0.5 * ||w||**2``. The bias is not
        regularized.
    learning_rate
        Positive full-batch subgradient step size.
    epochs
        Positive number of parameter updates.

    Notes
    -----
    Targets use the signed convention ``{-1, +1}``. The fitted decision score
    is affine, but the hinge loss and margin regularization distinguish this
    estimator from logistic regression and from other thresholded
    single-neuron classifiers.
    """

    regularization_strength: float = 0.01
    learning_rate: float = 0.01
    epochs: int = 2_000
    weights_: FloatArray | None = field(default=None, init=False)
    bias_: float | None = field(default=None, init=False)
    loss_history_: list[float] = field(default_factory=list, init=False)
    support_mask_: NDArray[np.bool_] | None = field(default=None, init=False)

    def fit(self, features: ArrayLike, targets: ArrayLike) -> Self:
        """Fit the maximum-margin classifier and return the estimator."""

        matrix = _observation_matrix(features)
        target = _target_vector(targets, matrix.shape[0])
        if not np.isin(target, [-1.0, 1.0]).all():
            raise ValueError("SVM targets must contain only -1 and +1")
        if self.regularization_strength <= 0:
            raise ValueError("regularization_strength must be positive")
        if self.learning_rate <= 0:
            raise ValueError("learning_rate must be positive")
        if self.epochs <= 0:
            raise ValueError("epochs must be positive")

        n_observations, n_features = matrix.shape
        self.weights_ = np.zeros(n_features, dtype=float)
        self.bias_ = 0.0
        self.loss_history_ = []

        for _ in range(self.epochs):
            score = matrix @ self.weights_ + self.bias_
            signed_margin = target * score
            active = signed_margin < 1.0

            weight_gradient = self.regularization_strength * self.weights_
            bias_gradient = 0.0
            if active.any():
                weight_gradient -= (
                    matrix[active].T @ target[active]
                ) / n_observations
                bias_gradient = -float(target[active].sum()) / n_observations

            self.weights_ -= self.learning_rate * weight_gradient
            self.bias_ -= self.learning_rate * bias_gradient

            updated_score = matrix @ self.weights_ + self.bias_
            hinge = np.maximum(0.0, 1.0 - target * updated_score)
            objective = 0.5 * self.regularization_strength * float(
                self.weights_ @ self.weights_
            ) + float(np.mean(hinge))
            self.loss_history_.append(objective)

        final_margin = target * (matrix @ self.weights_ + self.bias_)
        self.support_mask_ = final_margin <= 1.0 + 1e-8
        return self

    def decision_function(self, features: ArrayLike) -> FloatArray:
        """Return signed distance scores up to the scale of ``weights_``."""

        matrix = _observation_matrix(features)
        if self.weights_ is None or self.bias_ is None:
            raise RuntimeError("LinearSVM must be fitted before prediction")
        if matrix.shape[1] != len(self.weights_):
            raise ValueError(f"features must contain {len(self.weights_)} columns")
        return matrix @ self.weights_ + self.bias_

    def predict(self, features: ArrayLike) -> NDArray[np.int64]:
        """Return labels in ``{-1, +1}``, assigning score zero to ``+1``."""

        score = self.decision_function(features)
        return np.where(score >= 0.0, 1, -1).astype(np.int64)


@dataclass
class DenseLayer:
    """A vectorized layer of neurons with one shared activation."""

    n_inputs: int
    n_outputs: int
    activation: Activation
    random_state: int = 0
    weights: FloatArray = field(init=False)
    biases: FloatArray = field(init=False)
    weight_gradient: FloatArray | None = field(default=None, init=False)
    bias_gradient: FloatArray | None = field(default=None, init=False)
    _input: FloatArray | None = field(default=None, init=False, repr=False)
    _preactivation: FloatArray | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.n_inputs <= 0 or self.n_outputs <= 0:
            raise ValueError("layer widths must be positive")
        generator = np.random.default_rng(self.random_state)
        scale = np.sqrt(1.0 / self.n_inputs)
        self.weights = generator.normal(0.0, scale, (self.n_outputs, self.n_inputs))
        self.biases = np.zeros(self.n_outputs, dtype=float)

    def forward(self, layer_input: ArrayLike) -> FloatArray:
        matrix = _observation_matrix(layer_input)
        if matrix.shape[1] != self.n_inputs:
            raise ValueError(f"layer input must contain {self.n_inputs} columns")
        self._input = matrix
        self._preactivation = matrix @ self.weights.T + self.biases
        return self.activation.forward(self._preactivation)

    def backward(self, activation_gradient: ArrayLike) -> FloatArray:
        if self._input is None or self._preactivation is None:
            raise RuntimeError("forward must be called before backward")
        upstream = np.asarray(activation_gradient, dtype=float)
        if upstream.shape != self._preactivation.shape:
            raise ValueError(
                f"activation_gradient must have shape {self._preactivation.shape}"
            )
        delta = upstream * self.activation.derivative(self._preactivation)
        self.weight_gradient = delta.T @ self._input
        self.bias_gradient = delta.sum(axis=0)
        return delta @ self.weights

    def step(self, learning_rate: float) -> None:
        if self.weight_gradient is None or self.bias_gradient is None:
            raise RuntimeError("backward must be called before step")
        if learning_rate <= 0:
            raise ValueError("learning_rate must be positive")
        self.weights -= learning_rate * self.weight_gradient
        self.biases -= learning_rate * self.bias_gradient


def half_mean_squared_error(prediction: ArrayLike, target: ArrayLike) -> float:
    """Return mean per-observation half squared Euclidean error."""

    predicted = np.asarray(prediction, dtype=float)
    expected = np.asarray(target, dtype=float)
    if predicted.shape != expected.shape or predicted.ndim != 2:
        raise ValueError("prediction and target must have the same 2D shape")
    return float(0.5 * np.mean(np.sum((predicted - expected) ** 2, axis=1)))


@dataclass
class MeanSquaredNetwork:
    """A small sequential dense network trained with mean-squared error."""

    layers: list[DenseLayer]

    def __post_init__(self) -> None:
        if not self.layers:
            raise ValueError("a network needs at least one layer")
        for left, right in zip(self.layers, self.layers[1:], strict=False):
            if left.n_outputs != right.n_inputs:
                raise ValueError("adjacent layer widths do not match")

    def forward(self, features: ArrayLike) -> FloatArray:
        activation = _observation_matrix(features)
        for layer in self.layers:
            activation = layer.forward(activation)
        return activation

    def train_step(
        self, features: ArrayLike, targets: ArrayLike, learning_rate: float
    ) -> float:
        target = np.asarray(targets, dtype=float)
        prediction = self.forward(features)
        loss = half_mean_squared_error(prediction, target)
        gradient = (prediction - target) / prediction.shape[0]
        for layer in reversed(self.layers):
            gradient = layer.backward(gradient)
        for layer in self.layers:
            layer.step(learning_rate)
        return loss
