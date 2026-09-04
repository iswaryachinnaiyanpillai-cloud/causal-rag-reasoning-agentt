# ============================================================
# CAUSAL GRAPH MODULE
# Causal RAG Reasoning Agent
# TechNova Solutions
# ============================================================

from __future__ import annotations

from typing import Any, Dict, List, Tuple


# ============================================================
# HELPERS
# ============================================================

def _clean_text(value: Any) -> str:
    """Normalize a value into clean text."""
    if value is None:
        return ""

    return " ".join(
        str(value).strip().split()
    )


def _relationship_values(
    relationship: Any,
) -> Tuple[str, str, str]:
    """
    Extract cause, effect and relationship type.
    """

    if not isinstance(
        relationship,
        dict,
    ):
        return "", "", ""

    cause = _clean_text(
        relationship.get("cause", "")
    )

    effect = _clean_text(
        relationship.get("effect", "")
    )

    relation = _clean_text(
        relationship.get(
            "relationship",
            "causal",
        )
    ).lower()

    return cause, effect, relation


# ============================================================
# CREATE NODES
# ============================================================

def create_nodes(
    relationships: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Create unique nodes from causal relationships.
    """

    nodes: List[Dict[str, Any]] = []
    seen = set()

    for relationship in relationships:

        cause, effect, _ = _relationship_values(
            relationship
        )

        for value in (cause, effect):

            if not value:
                continue

            key = value.lower()

            if key in seen:
                continue

            seen.add(key)

            nodes.append(
                {
                    "id": value,
                    "label": value,
                    "type": "causal_factor",
                }
            )

    return nodes


# ============================================================
# CREATE EDGES
# ============================================================

def create_edges(
    relationships: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Create directed causal edges.
    """

    edges: List[Dict[str, Any]] = []
    seen = set()

    causal_types = {
        "causal",
        "cause",
        "causes",
        "caused",
        "caused_by",
    }

    for relationship in relationships:

        cause, effect, relation = (
            _relationship_values(
                relationship
            )
        )

        if not cause or not effect:
            continue

        if relation not in causal_types:
            continue

        key = (
            cause.lower(),
            effect.lower(),
        )

        if key in seen:
            continue

        seen.add(key)

        edges.append(
            {
                "source": cause,
                "target": effect,
                "label": "causes",
                "relationship": "causal",
            }
        )

    return edges


# ============================================================
# BUILD CAUSAL GRAPH
# ============================================================

def build_causal_graph(
    relationships: Any,
) -> Dict[str, Any]:
    """
    Build a directed causal graph.

    Supports either:

    1. Relationship dictionaries:
       [
           {
               "cause": "Database overload",
               "effect": "System failure",
               "relationship": "causal"
           }
       ]

    2. A simple causal chain:
       [
           "Cause",
           "Intermediate",
           "Effect"
       ]
    """

    if relationships is None:

        return {
            "success": True,
            "graph_type": "DIRECTED_CAUSAL_GRAPH",
            "nodes": [],
            "edges": [],
            "node_count": 0,
            "edge_count": 0,
            "relationship_count": 0,
            "is_empty": True,
        }

    if not isinstance(
        relationships,
        list,
    ):
        relationships = []

    # --------------------------------------------------------
    # CHAIN -> RELATIONSHIPS
    # --------------------------------------------------------

    if relationships and all(
        isinstance(item, str)
        for item in relationships
    ):

        chain = [
            _clean_text(item)
            for item in relationships
            if _clean_text(item)
        ]

        chain_relationships = []

        for index in range(
            len(chain) - 1
        ):

            chain_relationships.append(
                {
                    "cause": chain[index],
                    "effect": chain[
                        index + 1
                    ],
                    "relationship": "causal",
                }
            )

        relationships = chain_relationships

    # --------------------------------------------------------
    # VALID RELATIONSHIPS
    # --------------------------------------------------------

    valid_relationships = []

    for relationship in relationships:

        if not isinstance(
            relationship,
            dict,
        ):
            continue

        cause, effect, relation = (
            _relationship_values(
                relationship
            )
        )

        if not cause or not effect:
            continue

        valid_relationships.append(
            {
                "cause": cause,
                "effect": effect,
                "relationship": relation or "causal",
            }
        )

    # --------------------------------------------------------
    # NODES AND EDGES
    # --------------------------------------------------------

    nodes = create_nodes(
        valid_relationships
    )

    edges = create_edges(
        valid_relationships
    )

    node_index = {
        node["id"]: index
        for index, node in enumerate(nodes)
    }

    for edge in edges:

        edge["source_index"] = node_index.get(
            edge["source"]
        )

        edge["target_index"] = node_index.get(
            edge["target"]
        )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    return {
        "success": True,
        "graph_type": "DIRECTED_CAUSAL_GRAPH",
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "relationship_count": len(
            valid_relationships
        ),
        "is_empty": len(nodes) == 0,
    }


# ============================================================
# BUILD GRAPH FROM CHAIN
# ============================================================

def build_graph_from_chain(
    causal_chain: List[str],
) -> Dict[str, Any]:
    """Build a graph directly from a causal chain."""

    return build_causal_graph(
        causal_chain
    )


# ============================================================
# GET GRAPH DATA
# ============================================================

def get_graph_data(
    data: Any = None,
    *args,
    **kwargs,
) -> Dict[str, Any]:
    """
    Backward-compatible graph API used by main.py.

    This function accepts several possible input forms so older
    versions of the FastAPI backend remain compatible.

    Supported input:

    - Already-built graph dictionary
    - Relationship list
    - Causal chain list
    - Dictionary containing:
        causal_graph
        graph
        causal_chain
        relationships
        cause_effect_relationships
    """

    # --------------------------------------------------------
    # NO INPUT
    # --------------------------------------------------------

    if data is None:

        return {
            "success": True,
            "graph_type": "DIRECTED_CAUSAL_GRAPH",
            "nodes": [],
            "edges": [],
            "node_count": 0,
            "edge_count": 0,
            "relationship_count": 0,
            "is_empty": True,
        }

    # --------------------------------------------------------
    # ALREADY A GRAPH
    # --------------------------------------------------------

    if isinstance(
        data,
        dict,
    ):

        # If it is already a graph
        if (
            "nodes" in data
            and "edges" in data
        ):

            return data

        # Common analyzer result
        if "causal_graph" in data:

            graph = data.get(
                "causal_graph"
            )

            if isinstance(
                graph,
                dict,
            ):

                return graph

        # Alternative key
        if "graph" in data:

            graph = data.get(
                "graph"
            )

            if isinstance(
                graph,
                dict,
            ):

                return graph

        # Causal chain
        if "causal_chain" in data:

            return build_causal_graph(
                data.get(
                    "causal_chain",
                    [],
                )
            )

        # Relationships
        if "cause_effect_relationships" in data:

            return build_causal_graph(
                data.get(
                    "cause_effect_relationships",
                    [],
                )
            )

        if "relationships" in data:

            return build_causal_graph(
                data.get(
                    "relationships",
                    [],
                )
            )

    # --------------------------------------------------------
    # LIST INPUT
    # --------------------------------------------------------

    if isinstance(
        data,
        list,
    ):

        return build_causal_graph(
            data
        )

    # --------------------------------------------------------
    # TRY EXTRA POSITIONAL ARGUMENTS
    # --------------------------------------------------------

    for item in args:

        if isinstance(
            item,
            list,
        ):

            return build_causal_graph(
                item
            )

        if isinstance(
            item,
            dict,
        ):

            return get_graph_data(
                item
            )

    # --------------------------------------------------------
    # EMPTY FALLBACK
    # --------------------------------------------------------

    return {
        "success": True,
        "graph_type": "DIRECTED_CAUSAL_GRAPH",
        "nodes": [],
        "edges": [],
        "node_count": 0,
        "edge_count": 0,
        "relationship_count": 0,
        "is_empty": True,
    }


# ============================================================
# GRAPH SUMMARY
# ============================================================

def graph_summary(
    graph: Dict[str, Any],
) -> Dict[str, Any]:
    """Return a compact graph summary."""

    if not isinstance(
        graph,
        dict,
    ):

        return {
            "node_count": 0,
            "edge_count": 0,
            "is_empty": True,
        }

    return {
        "node_count": graph.get(
            "node_count",
            len(
                graph.get(
                    "nodes",
                    [],
                )
            ),
        ),
        "edge_count": graph.get(
            "edge_count",
            len(
                graph.get(
                    "edges",
                    [],
                )
            ),
        ),
        "is_empty": graph.get(
            "is_empty",
            True,
        ),
    }


# ============================================================
# GRAPH TO TEXT
# ============================================================

def graph_to_text(
    graph: Dict[str, Any],
) -> str:
    """Convert graph edges into readable text."""

    if not isinstance(
        graph,
        dict,
    ):

        return "No causal graph available."

    edges = graph.get(
        "edges",
        [],
    )

    if not edges:
        return "No causal graph available."

    lines = []

    for edge in edges:

        source = edge.get(
            "source",
            "",
        )

        target = edge.get(
            "target",
            "",
        )

        if source and target:

            lines.append(
                f"{source} → {target}"
            )

    if not lines:

        return "No causal graph available."

    return "\n".join(
        lines
    )


# ============================================================
# GRAPH VALIDATION
# ============================================================

def validate_graph(
    graph: Dict[str, Any],
) -> Dict[str, Any]:
    """Validate the generated graph."""

    errors: List[str] = []

    if not isinstance(
        graph,
        dict,
    ):

        return {
            "valid": False,
            "errors": [
                "Graph must be a dictionary."
            ],
        }

    nodes = graph.get(
        "nodes",
        [],
    )

    edges = graph.get(
        "edges",
        [],
    )

    if not isinstance(
        nodes,
        list,
    ):

        errors.append(
            "nodes must be a list."
        )

    if not isinstance(
        edges,
        list,
    ):

        errors.append(
            "edges must be a list."
        )

    node_ids = set()

    if isinstance(
        nodes,
        list,
    ):

        for node in nodes:

            if not isinstance(
                node,
                dict,
            ):

                errors.append(
                    "Every node must be a dictionary."
                )

                continue

            node_id = node.get(
                "id"
            )

            if not node_id:

                errors.append(
                    "A node is missing its id."
                )

                continue

            if node_id in node_ids:

                errors.append(
                    f"Duplicate node: {node_id}"
                )

            node_ids.add(
                node_id
            )

    if isinstance(
        edges,
        list,
    ):

        for edge in edges:

            if not isinstance(
                edge,
                dict,
            ):

                errors.append(
                    "Every edge must be a dictionary."
                )

                continue

            source = edge.get(
                "source"
            )

            target = edge.get(
                "target"
            )

            if not source or not target:

                errors.append(
                    "An edge is missing source or target."
                )

                continue

            if source not in node_ids:

                errors.append(
                    f"Edge source not found: {source}"
                )

            if target not in node_ids:

                errors.append(
                    f"Edge target not found: {target}"
                )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }


# ============================================================
# BACKWARD COMPATIBILITY ALIASES
# ============================================================

def create_causal_graph(
    relationships: Any,
) -> Dict[str, Any]:

    return build_causal_graph(
        relationships
    )


def generate_causal_graph(
    relationships: Any,
) -> Dict[str, Any]:

    return build_causal_graph(
        relationships
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("CAUSAL GRAPH TEST")
    print("=" * 70)

    test_chain = [
        "Increased user requests",
        "Higher database queries",
        "Higher database load",
        "Increased processing time",
        "Higher system latency",
        "System timeout",
    ]

    graph = build_causal_graph(
        test_chain
    )

    print("\nNodes:")

    for node in graph["nodes"]:

        print(
            f"  - {node['label']}"
        )

    print("\nEdges:")

    for edge in graph["edges"]:

        print(
            f"  {edge['source']} "
            f"→ "
            f"{edge['target']}"
        )

    print("\nGraph Summary:")

    print(
        graph_summary(
            graph
        )
    )

    print("\nGraph Text:")

    print(
        graph_to_text(
            graph
        )
    )

    print("\nValidation:")

    print(
        validate_graph(
            graph
        )
    )

    print("\nCompatibility Test:")

    compatibility_graph = get_graph_data(
        {
            "causal_chain": test_chain
        }
    )

    print(
        graph_summary(
            compatibility_graph
        )
    )

    print("\n" + "=" * 70)
    print("CAUSAL GRAPH TEST COMPLETE")
    print("=" * 70)