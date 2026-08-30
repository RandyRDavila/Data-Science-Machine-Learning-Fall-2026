"""Behavioral contracts for the package knowledge graph and CLI."""

from pathlib import Path

import pytest

from rice_dsm import (
    KnowledgeGraph,
    KnowledgeNode,
    Relationship,
    load_knowledge_graph,
)
from rice_dsm.cli import main

PROJECT_ROOT = Path(__file__).parents[1]
DATA_DIRECTORY = (
    PROJECT_ROOT / "notebooks" / "lecture-02-python-foundations-ii" / "data"
)
CONCEPTS_PATH = DATA_DIRECTORY / "scientific_concepts.json"
RELATIONSHIPS_PATH = DATA_DIRECTORY / "scientific_relationships.csv"


def node(identifier: str) -> KnowledgeNode:
    """Create a compact valid node for unit tests."""

    return KnowledgeNode(
        identifier=identifier,
        label=identifier.replace("_", " ").title(),
        category="test",
        description=f"Test concept {identifier}.",
    )


def edge(source_id: str, target_id: str, predicate: str = "LEADS_TO") -> Relationship:
    """Create a compact valid relationship for unit tests."""

    return Relationship(
        source_id=source_id,
        predicate=predicate,
        target_id=target_id,
        confidence=1.0,
        evidence="Unit-test relationship.",
    )


def test_graph_rejects_duplicate_nodes() -> None:
    graph = KnowledgeGraph([node("alpha")])

    with pytest.raises(ValueError, match="duplicate node identifier"):
        graph.add_node(node("alpha"))


def test_graph_rejects_unknown_endpoints_and_duplicate_triples() -> None:
    graph = KnowledgeGraph([node("alpha"), node("beta")])

    with pytest.raises(ValueError, match="unknown nodes"):
        graph.add_relationship(edge("alpha", "missing"))

    graph.add_relationship(edge("alpha", "beta"))
    with pytest.raises(ValueError, match="duplicate relationship"):
        graph.add_relationship(edge("alpha", "beta"))


def test_neighbors_filter_by_predicate_without_exposing_internal_lists() -> None:
    graph = KnowledgeGraph(
        [node("alpha"), node("beta"), node("gamma")],
        [edge("alpha", "beta", "USES"), edge("alpha", "gamma", "MODELS")],
    )

    assert tuple(item.identifier for item in graph.neighbors("alpha")) == (
        "beta",
        "gamma",
    )
    assert tuple(
        item.identifier for item in graph.neighbors("alpha", predicate="USES")
    ) == ("beta",)
    assert isinstance(graph.relationships, tuple)


def test_breadth_first_search_returns_a_shortest_directed_path() -> None:
    graph = KnowledgeGraph(
        [node(name) for name in ("alpha", "beta", "gamma", "delta")],
        [
            edge("alpha", "beta"),
            edge("beta", "gamma"),
            edge("alpha", "delta"),
            edge("delta", "gamma"),
        ],
    )

    assert graph.find_path("alpha", "gamma") == ("alpha", "beta", "gamma")
    assert graph.find_path("gamma", "alpha") is None


def test_native_file_loader_builds_the_course_graph() -> None:
    graph = load_knowledge_graph(CONCEPTS_PATH, RELATIONSHIPS_PATH)

    assert len(graph) == 20
    assert len(graph.relationships) == 25
    assert graph.find_path("diffusion_model", "scientific_measurement") == (
        "diffusion_model",
        "markov_chain",
        "probability_distribution",
        "scientific_measurement",
    )


def test_cli_prints_summary_and_path(capsys: pytest.CaptureFixture[str]) -> None:
    base_arguments = [str(CONCEPTS_PATH), str(RELATIONSHIPS_PATH)]

    assert main(base_arguments) == 0
    assert "20 nodes; 25 relationships" in capsys.readouterr().out

    path_arguments = [
        *base_arguments,
        "--path",
        "diffusion_model",
        "scientific_measurement",
    ]
    assert main(path_arguments) == 0
    assert "Diffusion model -> Markov chain" in capsys.readouterr().out


def test_cli_returns_nonzero_for_invalid_input(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    missing_file = tmp_path / "missing.json"

    assert main([str(missing_file), str(RELATIONSHIPS_PATH)]) == 2
    assert "error:" in capsys.readouterr().err
