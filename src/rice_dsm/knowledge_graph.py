"""Validated scientific knowledge-graph models and native-file loaders."""

from __future__ import annotations

import csv
import json
from collections import deque
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from pathlib import Path

RELATIONSHIP_FIELDS = (
    "source_id",
    "predicate",
    "target_id",
    "confidence",
    "evidence",
)


def _is_identifier(value: str) -> bool:
    """Return whether a value follows the graph's identifier policy."""

    return bool(value) and value.isidentifier() and value == value.lower()


def _require_string(record: Mapping[str, object], key: str) -> str:
    """Return one required, nonblank string field."""

    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key!r} must be a nonblank string")
    return value


@dataclass(frozen=True, slots=True)
class KnowledgeNode:
    """A validated concept in a scientific knowledge graph.

    Parameters
    ----------
    identifier : str
        Stable lowercase identifier.
    label : str
        Human-readable concept name.
    category : str
        Broad domain category.
    description : str
        Concise explanation of the concept.
    aliases : tuple of str, optional
        Alternative names.

    Raises
    ------
    TypeError
        If a field has the wrong runtime type.
    ValueError
        If a string is blank or the identifier policy is violated.
    """

    identifier: str
    label: str
    category: str
    description: str
    aliases: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Validate one node after dataclass initialization."""

        text_fields = (self.identifier, self.label, self.category, self.description)
        if not all(isinstance(value, str) for value in text_fields):
            raise TypeError("node text fields must be strings")
        if not _is_identifier(self.identifier):
            raise ValueError(f"invalid node identifier: {self.identifier!r}")
        if not all(value.strip() for value in text_fields[1:]):
            raise ValueError("node label, category, and description cannot be blank")
        if not isinstance(self.aliases, tuple) or not all(
            isinstance(alias, str) and alias.strip() for alias in self.aliases
        ):
            raise TypeError("aliases must be a tuple of nonblank strings")


@dataclass(frozen=True, slots=True)
class Relationship:
    """A directed, labeled fact connecting two knowledge nodes.

    Parameters
    ----------
    source_id : str
        Identifier where the directed edge begins.
    predicate : str
        Uppercase relationship label.
    target_id : str
        Identifier where the directed edge ends.
    confidence : float
        Editorial confidence in the closed interval ``[0, 1]``.
    evidence : str
        Brief rationale for including the relationship.

    Raises
    ------
    TypeError
        If a field has the wrong runtime type.
    ValueError
        If an endpoint, predicate, confidence, or evidence value is invalid.
    """

    source_id: str
    predicate: str
    target_id: str
    confidence: float
    evidence: str

    def __post_init__(self) -> None:
        """Validate one relationship after dataclass initialization."""

        text_fields = (self.source_id, self.predicate, self.target_id, self.evidence)
        if not all(isinstance(value, str) for value in text_fields):
            raise TypeError("relationship text fields must be strings")
        if not _is_identifier(self.source_id) or not _is_identifier(self.target_id):
            raise ValueError("relationship endpoints must be valid node identifiers")
        predicate_is_upper = self.predicate == self.predicate.upper()
        if not self.predicate.isidentifier() or not predicate_is_upper:
            raise ValueError("predicate must use UPPER_SNAKE_CASE")
        if not isinstance(self.confidence, float):
            raise TypeError("confidence must be a float")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if not self.evidence.strip():
            raise ValueError("evidence cannot be blank")


class KnowledgeGraph:
    """A directed knowledge graph with validated nodes and relationships.

    Parameters
    ----------
    nodes : iterable of KnowledgeNode, optional
        Nodes added in iteration order.
    relationships : iterable of Relationship, optional
        Relationships added after all nodes.

    Raises
    ------
    TypeError
        If an item has the wrong domain type.
    ValueError
        If identifiers, endpoints, or relationship triples violate graph invariants.
    """

    def __init__(
        self,
        nodes: Iterable[KnowledgeNode] = (),
        relationships: Iterable[Relationship] = (),
    ) -> None:
        """Initialize a graph while preserving input order."""

        self._nodes: dict[str, KnowledgeNode] = {}
        self._outgoing: dict[str, list[Relationship]] = {}
        self._triples: set[tuple[str, str, str]] = set()
        for node in nodes:
            self.add_node(node)
        for relationship in relationships:
            self.add_relationship(relationship)

    def __len__(self) -> int:
        """Return the number of nodes."""

        return len(self._nodes)

    def __contains__(self, node_id: object) -> bool:
        """Return whether a node identifier is present."""

        return node_id in self._nodes

    @property
    def nodes(self) -> tuple[KnowledgeNode, ...]:
        """Return an immutable node snapshot in insertion order."""

        return tuple(self._nodes.values())

    @property
    def relationships(self) -> tuple[Relationship, ...]:
        """Return an immutable relationship snapshot in insertion order."""

        return tuple(edge for edges in self._outgoing.values() for edge in edges)

    def add_node(self, node: KnowledgeNode) -> None:
        """Add a unique node.

        Parameters
        ----------
        node : KnowledgeNode
            Validated node to add.

        Raises
        ------
        TypeError
            If ``node`` is not a ``KnowledgeNode``.
        ValueError
            If its identifier is already present.
        """

        if not isinstance(node, KnowledgeNode):
            raise TypeError("node must be a KnowledgeNode")
        if node.identifier in self._nodes:
            raise ValueError(f"duplicate node identifier: {node.identifier!r}")
        self._nodes[node.identifier] = node
        self._outgoing[node.identifier] = []

    def add_relationship(self, relationship: Relationship) -> None:
        """Add a relationship after checking graph-level invariants.

        Parameters
        ----------
        relationship : Relationship
            Validated directed relationship.

        Raises
        ------
        TypeError
            If the value is not a ``Relationship``.
        ValueError
            If an endpoint is absent or the triple is duplicated.
        """

        if not isinstance(relationship, Relationship):
            raise TypeError("relationship must be a Relationship")
        missing = [
            node_id
            for node_id in (relationship.source_id, relationship.target_id)
            if node_id not in self._nodes
        ]
        if missing:
            raise ValueError(f"relationship references unknown nodes: {missing}")
        triple = (
            relationship.source_id,
            relationship.predicate,
            relationship.target_id,
        )
        if triple in self._triples:
            raise ValueError(f"duplicate relationship triple: {triple}")
        self._outgoing[relationship.source_id].append(relationship)
        self._triples.add(triple)

    def get_node(self, node_id: str) -> KnowledgeNode:
        """Return a node by identifier.

        Parameters
        ----------
        node_id : str
            Stable node identifier.

        Returns
        -------
        KnowledgeNode
            Matching node.

        Raises
        ------
        KeyError
            If no matching node exists.
        """

        try:
            return self._nodes[node_id]
        except KeyError as error:
            raise KeyError(f"unknown node: {node_id!r}") from error

    def relationships_from(
        self,
        node_id: str,
        *,
        predicate: str | None = None,
    ) -> tuple[Relationship, ...]:
        """Return outgoing relationships, optionally filtered by predicate.

        Parameters
        ----------
        node_id : str
            Source node identifier.
        predicate : str or None, optional
            Exact relationship label to retain.

        Returns
        -------
        tuple of Relationship
            Matching relationships in insertion order.

        Raises
        ------
        KeyError
            If the source node is unknown.
        """

        self.get_node(node_id)
        edges = self._outgoing[node_id]
        if predicate is None:
            return tuple(edges)
        return tuple(edge for edge in edges if edge.predicate == predicate)

    def neighbors(
        self,
        node_id: str,
        *,
        predicate: str | None = None,
    ) -> tuple[KnowledgeNode, ...]:
        """Return distinct target nodes reached by outgoing relationships.

        Parameters
        ----------
        node_id : str
            Source node identifier.
        predicate : str or None, optional
            Exact relationship label to retain.

        Returns
        -------
        tuple of KnowledgeNode
            Target nodes with duplicates removed in edge order.
        """

        seen: set[str] = set()
        result: list[KnowledgeNode] = []
        for edge in self.relationships_from(node_id, predicate=predicate):
            if edge.target_id not in seen:
                result.append(self._nodes[edge.target_id])
                seen.add(edge.target_id)
        return tuple(result)

    def find_path(self, start_id: str, end_id: str) -> tuple[str, ...] | None:
        """Find a shortest directed path using breadth-first search.

        Parameters
        ----------
        start_id : str
            Identifier at which traversal begins.
        end_id : str
            Desired destination identifier.

        Returns
        -------
        tuple of str or None
            Node identifiers along a shortest path, or ``None`` if unreachable.

        Raises
        ------
        KeyError
            If either endpoint is unknown.
        """

        self.get_node(start_id)
        self.get_node(end_id)
        queue: deque[tuple[str, ...]] = deque([(start_id,)])
        visited = {start_id}

        while queue:
            path = queue.popleft()
            current = path[-1]
            if current == end_id:
                return path
            for neighbor in self.neighbors(current):
                if neighbor.identifier not in visited:
                    visited.add(neighbor.identifier)
                    queue.append((*path, neighbor.identifier))
        return None

    def to_mapping(self) -> dict[str, object]:
        """Return a JSON-serializable graph representation."""

        return {
            "schema_version": 1,
            "nodes": [asdict(node) for node in self.nodes],
            "relationships": [asdict(edge) for edge in self.relationships],
        }


def node_from_mapping(record: Mapping[str, object]) -> KnowledgeNode:
    """Convert a parsed JSON mapping into a knowledge node.

    Parameters
    ----------
    record : mapping of str to object
        One concept from the JSON document.

    Returns
    -------
    KnowledgeNode
        Validated immutable node.

    Raises
    ------
    ValueError
        If a required field or alias violates the schema.
    """

    raw_aliases = record.get("aliases", [])
    if not isinstance(raw_aliases, list) or not all(
        isinstance(alias, str) for alias in raw_aliases
    ):
        raise ValueError("'aliases' must be a list of strings")
    return KnowledgeNode(
        identifier=_require_string(record, "id"),
        label=_require_string(record, "label"),
        category=_require_string(record, "category"),
        description=_require_string(record, "description"),
        aliases=tuple(raw_aliases),
    )


def relationship_from_mapping(record: Mapping[str, object]) -> Relationship:
    """Convert one parsed CSV row into a relationship.

    Parameters
    ----------
    record : mapping of str to object
        Row produced by ``csv.DictReader``.

    Returns
    -------
    Relationship
        Validated immutable relationship.

    Raises
    ------
    ValueError
        If a field is missing or cannot be converted.
    """

    confidence_text = _require_string(record, "confidence")
    try:
        confidence = float(confidence_text)
    except ValueError as error:
        raise ValueError("'confidence' must contain a decimal number") from error
    return Relationship(
        source_id=_require_string(record, "source_id"),
        predicate=_require_string(record, "predicate"),
        target_id=_require_string(record, "target_id"),
        confidence=confidence,
        evidence=_require_string(record, "evidence"),
    )


def load_knowledge_graph(
    concepts_file: Path,
    relationships_file: Path,
) -> KnowledgeGraph:
    """Load a validated knowledge graph from JSON concepts and CSV relationships.

    Parameters
    ----------
    concepts_file : Path
        JSON document containing a ``concepts`` array.
    relationships_file : Path
        CSV file containing the exact relationship schema.

    Returns
    -------
    KnowledgeGraph
        Fully validated graph.

    Raises
    ------
    OSError
        If either file cannot be read.
    json.JSONDecodeError
        If the JSON syntax is invalid.
    ValueError
        If a schema or graph invariant is violated.
    """

    with concepts_file.open(mode="r", encoding="utf-8") as handle:
        document = json.load(handle)
    if not isinstance(document, dict):
        raise ValueError(f"{concepts_file.name}: root must be a JSON object")
    raw_nodes = document.get("concepts")
    if document.get("schema_version") != 1 or not isinstance(raw_nodes, list):
        raise ValueError(f"{concepts_file.name}: unsupported concept schema")

    graph = KnowledgeGraph()
    for index, raw_node in enumerate(raw_nodes):
        if not isinstance(raw_node, dict):
            message = f"{concepts_file.name}: concepts[{index}] must be an object"
            raise ValueError(message)
        try:
            graph.add_node(node_from_mapping(raw_node))
        except (TypeError, ValueError) as error:
            message = f"{concepts_file.name}: concepts[{index}]: {error}"
            raise ValueError(message) from error

    with relationships_file.open(
        mode="r", encoding="utf-8", newline=""
    ) as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != RELATIONSHIP_FIELDS:
            raise ValueError(f"{relationships_file.name}: unexpected CSV headers")
        for line_number, row in enumerate(reader, start=2):
            try:
                graph.add_relationship(relationship_from_mapping(row))
            except (TypeError, ValueError) as error:
                message = f"{relationships_file.name}: line {line_number}: {error}"
                raise ValueError(message) from error
    return graph
