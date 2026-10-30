"""Common contracts for the class-built machine-learning platform.

Algorithm implementations are added only after their mathematical behavior,
public interface, and verification plan have been reviewed.
"""

from rice_dsm.ml.base import Clusterer, SupervisedPredictor, Transformer
from rice_dsm.ml.neighbors import (
    ItemKNNRecommender,
    KNearestNeighborsClassifier,
    KNearestNeighborsRegressor,
    euclidean_distances,
)
from rice_dsm.ml.neural import (
    DenseLayer,
    Identity,
    LinearSVM,
    LogisticCrossEntropy,
    MeanSquaredNetwork,
    ReLU,
    Sigmoid,
    SingleNeuron,
    SquaredErrorRegression,
    half_mean_squared_error,
)

__all__ = [
    "Clusterer",
    "DenseLayer",
    "Identity",
    "ItemKNNRecommender",
    "KNearestNeighborsClassifier",
    "KNearestNeighborsRegressor",
    "LinearSVM",
    "LogisticCrossEntropy",
    "MeanSquaredNetwork",
    "ReLU",
    "Sigmoid",
    "SingleNeuron",
    "SquaredErrorRegression",
    "SupervisedPredictor",
    "Transformer",
    "euclidean_distances",
    "half_mean_squared_error",
]
