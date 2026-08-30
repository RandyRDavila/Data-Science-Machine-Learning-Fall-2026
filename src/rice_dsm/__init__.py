"""Reusable teaching examples for CMOR 438 / INDE 577."""

from rice_dsm.knowledge_graph import (
    KnowledgeGraph,
    KnowledgeNode,
    Relationship,
    load_knowledge_graph,
)
from rice_dsm.metrics import mean_absolute_error, root_mean_squared_error
from rice_dsm.records import StudentRecord, summarize_scores

__all__ = [
    "KnowledgeGraph",
    "KnowledgeNode",
    "Relationship",
    "StudentRecord",
    "load_knowledge_graph",
    "mean_absolute_error",
    "root_mean_squared_error",
    "summarize_scores",
]
__version__ = "0.1.0"
