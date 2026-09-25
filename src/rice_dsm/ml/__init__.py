"""Common contracts for the class-built machine-learning platform.

Algorithm implementations are added only after their mathematical behavior,
public interface, and verification plan have been reviewed.
"""

from rice_dsm.ml.base import Clusterer, SupervisedPredictor, Transformer

__all__ = ["Clusterer", "SupervisedPredictor", "Transformer"]
