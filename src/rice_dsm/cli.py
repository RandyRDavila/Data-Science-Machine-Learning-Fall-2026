"""Command-line adapter for the Rice DSM teaching package."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from rice_dsm.knowledge_graph import load_knowledge_graph


def build_parser() -> argparse.ArgumentParser:
    """Build the package command-line parser."""

    parser = argparse.ArgumentParser(
        prog="rice-dsm",
        description="Inspect a scientific knowledge graph stored as JSON and CSV.",
    )
    parser.add_argument("concepts", type=Path, help="path to concept JSON")
    parser.add_argument("relationships", type=Path, help="path to relationship CSV")
    parser.add_argument(
        "--path",
        nargs=2,
        metavar=("START", "END"),
        help="find a shortest directed path between node identifiers",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Load a graph, print a summary or path, and return an exit status.

    Parameters
    ----------
    argv : sequence of str or None, optional
        Arguments excluding the program name. ``None`` reads ``sys.argv``.

    Returns
    -------
    int
        Zero on success, one when a requested path is unreachable, or two when
        input data is invalid or unreadable.
    """

    arguments = build_parser().parse_args(argv)
    try:
        graph = load_knowledge_graph(arguments.concepts, arguments.relationships)
        if arguments.path is None:
            print(f"{len(graph)} nodes; {len(graph.relationships)} relationships")
            return 0
        start_id, end_id = arguments.path
        path = graph.find_path(start_id, end_id)
    except (OSError, KeyError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if path is None:
        print(f"no directed path from {start_id!r} to {end_id!r}")
        return 1
    labels = (graph.get_node(node_id).label for node_id in path)
    print(" -> ".join(labels))
    return 0
