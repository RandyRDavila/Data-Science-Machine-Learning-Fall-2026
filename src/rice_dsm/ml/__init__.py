"""Common contracts for the class-built machine-learning platform.

Algorithm implementations are added only after their mathematical behavior,
public interface, and verification plan have been reviewed.
"""

from rice_dsm.ml.base import Clusterer, SupervisedPredictor, Transformer
from rice_dsm.ml.ensembles import (
    RandomForestClassifier,
    SquaredErrorGradientBoostingRegressor,
    bootstrap_indices,
)
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
from rice_dsm.ml.trees import (
    DecisionTreeClassifier,
    DecisionTreeRegressor,
    TreeNode,
    entropy_impurity,
    gini_impurity,
    mean_squared_impurity,
    plot_tree,
)

__all__ = [
    "Clusterer",
    "DenseLayer",
    "DecisionTreeClassifier",
    "DecisionTreeRegressor",
    "Identity",
    "ItemKNNRecommender",
    "KNearestNeighborsClassifier",
    "KNearestNeighborsRegressor",
    "LinearSVM",
    "LogisticCrossEntropy",
    "MeanSquaredNetwork",
    "ReLU",
    "RandomForestClassifier",
    "Sigmoid",
    "SingleNeuron",
    "SquaredErrorRegression",
    "SquaredErrorGradientBoostingRegressor",
    "SupervisedPredictor",
    "Transformer",
    "TreeNode",
    "bootstrap_indices",
    "entropy_impurity",
    "euclidean_distances",
    "gini_impurity",
    "half_mean_squared_error",
    "mean_squared_impurity",
    "plot_tree",
]
