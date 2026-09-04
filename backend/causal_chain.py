# ============================================================
# CAUSAL CHAIN CONSTRUCTOR
# Causal RAG Agent
# TechNova Solutions
# ============================================================

from typing import List, Dict, Any


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text: str) -> str:
    """Normalize text for reliable comparison."""

    if not text:
        return ""

    return (
        str(text)
        .strip()
        .lower()
        .rstrip(".")
    )


# ============================================================
# BUILD CAUSAL CHAIN
# ============================================================

def build_causal_chain(
    relationships: List[Dict[str, Any]]
):
    """
    Construct ordered causal chains from extracted
    cause-effect relationships.

    Example:

        A -> B
        B -> C
        C -> D

    becomes:

        A -> B -> C -> D
    """

    if not relationships:
        return {
            "success": True,
            "chain": [],
            "chain_length": 0,
            "status": "NO_CAUSAL_RELATIONSHIPS"
        }

    # --------------------------------------------------------
    # Keep only genuine causal relationships
    # --------------------------------------------------------

    causal_relationships = []

    for relationship in relationships:

        if not isinstance(relationship, dict):
            continue

        relationship_type = str(
            relationship.get("relationship", "")
        ).upper().strip()

        cause = relationship.get("cause")
        effect = relationship.get("effect")

        if (
            relationship_type == "CAUSAL"
            and cause
            and effect
        ):
            causal_relationships.append(
                relationship
            )

    if not causal_relationships:
        return {
            "success": True,
            "chain": [],
            "chain_length": 0,
            "status": "NO_CAUSAL_RELATIONSHIPS"
        }

    # --------------------------------------------------------
    # Build adjacency graph
    #
    # One cause can have multiple effects.
    # --------------------------------------------------------

    adjacency = {}

    node_text = {}

    for relationship in causal_relationships:

        cause = str(
            relationship.get("cause")
        ).strip()

        effect = str(
            relationship.get("effect")
        ).strip()

        cause_key = normalize_text(cause)
        effect_key = normalize_text(effect)

        if not cause_key or not effect_key:
            continue

        node_text[cause_key] = cause
        node_text[effect_key] = effect

        if cause_key not in adjacency:
            adjacency[cause_key] = []

        # Avoid duplicate edges
        if effect_key not in adjacency[cause_key]:
            adjacency[cause_key].append(
                effect_key
            )

    # --------------------------------------------------------
    # Find possible starting causes
    #
    # A starting cause does not appear as the effect
    # of another causal relationship.
    # --------------------------------------------------------

    causes = set(adjacency.keys())

    effects = set()

    for effect_list in adjacency.values():
        effects.update(effect_list)

    starting_causes = causes - effects

    # --------------------------------------------------------
    # Deterministic ordering
    # --------------------------------------------------------

    if starting_causes:

        start_keys = sorted(
            starting_causes
        )

    else:

        # Handles cycles or unusual extracted graphs.
        start_keys = [
            normalize_text(
                causal_relationships[0].get("cause")
            )
        ]

    # --------------------------------------------------------
    # Find the longest valid causal path
    # --------------------------------------------------------

    best_chain = []

    for start_key in start_keys:

        candidate = find_longest_path(
            start_key,
            adjacency,
            node_text
        )

        if len(candidate) > len(best_chain):

            best_chain = candidate

    # --------------------------------------------------------
    # Safety fallback
    # --------------------------------------------------------

    if not best_chain:

        first_relationship = (
            causal_relationships[0]
        )

        cause = str(
            first_relationship.get("cause")
        ).strip()

        effect = str(
            first_relationship.get("effect")
        ).strip()

        best_chain = [
            cause,
            effect
        ]

    # --------------------------------------------------------
    # Remove duplicates while preserving order
    # --------------------------------------------------------

    best_chain = remove_duplicate_nodes(
        best_chain
    )

    # --------------------------------------------------------
    # Determine status
    # --------------------------------------------------------

    if len(best_chain) >= 2:

        status = "CHAIN_CONSTRUCTED"

    else:

        status = "SINGLE_CAUSAL_RELATIONSHIP"

    return {
        "success": True,
        "chain": best_chain,
        "chain_length": len(best_chain),
        "status": status
    }


# ============================================================
# FIND LONGEST CAUSAL PATH
# ============================================================

def find_longest_path(
    start_key: str,
    adjacency: Dict[str, List[str]],
    node_text: Dict[str, str]
):
    """
    Find the longest causal path beginning at start_key.

    Uses depth-first search with cycle protection.
    """

    if not start_key:
        return []

    best_path = []

    def dfs(
        current_key: str,
        current_path: List[str],
        visited: set
    ):

        nonlocal best_path

        # ----------------------------------------------------
        # Cycle protection
        # ----------------------------------------------------

        if current_key in visited:
            return

        visited = visited.copy()
        visited.add(current_key)

        current_path = current_path.copy()

        if current_key in node_text:

            current_path.append(
                node_text[current_key]
            )

        # ----------------------------------------------------
        # Update longest path
        # ----------------------------------------------------

        if len(current_path) > len(best_path):

            best_path = current_path

        # ----------------------------------------------------
        # Explore all possible effects
        # ----------------------------------------------------

        next_nodes = adjacency.get(
            current_key,
            []
        )

        for next_key in next_nodes:

            dfs(
                next_key,
                current_path,
                visited
            )

    dfs(
        start_key,
        [],
        set()
    )

    return best_path


# ============================================================
# FIND NODE TEXT
# ============================================================

def get_node_text(
    node_key: str,
    relationships: List[Dict[str, Any]]
):
    """Return original text representation of a node."""

    normalized_key = normalize_text(
        node_key
    )

    for relationship in relationships:

        cause = relationship.get("cause")
        effect = relationship.get("effect")

        if normalize_text(cause) == normalized_key:
            return cause

        if normalize_text(effect) == normalized_key:
            return effect

    return None


# ============================================================
# FIND RELATIONSHIP
# ============================================================

def find_relationship_by_cause(
    cause_key: str,
    relationships: List[Dict[str, Any]]
):
    """
    Return the first causal relationship beginning
    with the requested cause.

    Kept for compatibility with existing modules.
    """

    normalized_key = normalize_text(
        cause_key
    )

    for relationship in relationships:

        relationship_type = str(
            relationship.get("relationship", "")
        ).upper().strip()

        if relationship_type != "CAUSAL":
            continue

        cause = relationship.get("cause")

        if normalize_text(cause) == normalized_key:

            return relationship

    return None


# ============================================================
# REMOVE DUPLICATES
# ============================================================

def remove_duplicate_nodes(
    chain: List[str]
):
    """Remove duplicate nodes while preserving order."""

    result = []
    seen = set()

    for node in chain:

        if not node:
            continue

        key = normalize_text(node)

        if key not in seen:

            result.append(node)
            seen.add(key)

    return result


# ============================================================
# CREATE CAUSAL CHAIN TEXT
# ============================================================

def causal_chain_text(
    chain: List[str]
):
    """Convert chain list into readable arrow notation."""

    if not chain:
        return ""

    return " → ".join(
        str(node)
        for node in chain
    )


# ============================================================
# CREATE CAUSAL CHAIN STRUCTURE
# ============================================================

def construct_causal_chain(
    relationships: List[Dict[str, Any]]
):
    """
    High-level wrapper used by the application.
    """

    result = build_causal_chain(
        relationships
    )

    chain = result.get(
        "chain",
        []
    )

    return {
        "success": result.get(
            "success",
            True
        ),
        "causal_chain": chain,
        "chain_text": causal_chain_text(
            chain
        ),
        "chain_length": result.get(
            "chain_length",
            0
        ),
        "status": result.get(
            "status",
            "UNKNOWN"
        )
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_relationships = [

        {
            "cause": "Increased user requests",
            "effect": "Higher database queries",
            "relationship": "CAUSAL"
        },

        {
            "cause": "Higher database queries",
            "effect": "Higher database load",
            "relationship": "CAUSAL"
        },

        {
            "cause": "Higher database load",
            "effect": "Increased processing time",
            "relationship": "CAUSAL"
        },

        {
            "cause": "Increased processing time",
            "effect": "Higher system latency",
            "relationship": "CAUSAL"
        },

        {
            "cause": "Higher system latency",
            "effect": "System timeout",
            "relationship": "CAUSAL"
        },

        {
            "cause": "Increased user requests",
            "effect": "Higher system latency",
            "relationship": "CORRELATION"
        }
    ]

    print("\n" + "=" * 60)
    print("CAUSAL CHAIN CONSTRUCTION TEST")
    print("=" * 60)

    result = construct_causal_chain(
        test_relationships
    )

    print("\nCausal Chain:")
    print(result["chain_text"])

    print("\nChain Length:")
    print(result["chain_length"])

    print("\nStatus:")
    print(result["status"])

    print("\nFull Result:")
    print(result)

    print("\n" + "=" * 60)