# ============================================================
# CLAIM EXTRACTOR
# Causal RAG Agent
# TechNova Solutions
# ============================================================

import re


# ============================================================
# CLAIM EXTRACTION
# ============================================================

def extract_claims(evidence: str, source: str = "TechNova Solutions"):
    """
    Extract structured claims from retrieved evidence.

    Each claim contains:
        - claim
        - source
        - evidence
        - entity
        - event
        - time

    The extractor is deterministic and does not generate
    unsupported information.
    """

    if not evidence or not evidence.strip():
        return []

    evidence = evidence.strip()

    # --------------------------------------------------------
    # Split retrieved evidence into meaningful sentences
    # --------------------------------------------------------

    sentences = re.split(
        r"(?<=[.!?])\s+|\n+",
        evidence
    )

    sentences = [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]

    claims = []

    # --------------------------------------------------------
    # Extract information from each sentence
    # --------------------------------------------------------

    for sentence in sentences:

        claim = sentence

        entity = extract_entity(sentence, source)

        event = extract_event(sentence)

        time = extract_time(sentence)

        claims.append({
            "claim": claim,
            "source": source,
            "evidence": sentence,
            "entity": entity,
            "event": event,
            "time": time
        })

    return claims


# ============================================================
# ENTITY EXTRACTION
# ============================================================

def extract_entity(text: str, default_source: str):
    """
    Identify the main entity mentioned in the evidence.
    """

    text_lower = text.lower()

    # --------------------------------------------------------
    # Known TechNova entity
    # --------------------------------------------------------

    if "technova solutions" in text_lower:
        return "TechNova Solutions"

    # --------------------------------------------------------
    # Common technical entities
    # --------------------------------------------------------

    entity_patterns = [
        r"\b(?:database|server|system|model|training data|"
        r"training-data|user activity|network|application|"
        r"website|software|cloud|AI|analytics)\b"
    ]

    for pattern in entity_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(0)

    return default_source


# ============================================================
# EVENT EXTRACTION
# ============================================================

def extract_event(text: str):
    """
    Identify the main event described in the evidence.
    """

    text_lower = text.lower()

    # --------------------------------------------------------
    # Known project events
    # --------------------------------------------------------

    event_patterns = [

        (
            r"system failure|system failed|system failure occurred",
            "System failure"
        ),

        (
            r"latency increased|increase in system latency|"
            r"higher system latency",
            "System latency increase"
        ),

        (
            r"database overload|database overloaded|"
            r"database load increased",
            "Database overload"
        ),

        (
            r"accuracy decreased|accuracy decrease|"
            r"model accuracy decreased",
            "Model accuracy decrease"
        ),

        (
            r"training data.*noise|noise.*training data",
            "Training-data noise increase"
        ),

        (
            r"user activity increased|increased user activity",
            "User activity increase"
        ),

        (
            r"server performance decreased|"
            r"server performance decrease",
            "Server performance decrease"
        )
    ]

    for pattern, event_name in event_patterns:

        if re.search(
            pattern,
            text_lower
        ):
            return event_name

    # --------------------------------------------------------
    # Generic event detection
    # --------------------------------------------------------

    generic_patterns = [
        (
            r"\b(increased|increase|higher)\b",
            "Increase"
        ),

        (
            r"\b(decreased|decrease|lower)\b",
            "Decrease"
        ),

        (
            r"\b(failed|failure)\b",
            "Failure"
        ),

        (
            r"\b(overload|overloaded)\b",
            "Overload"
        )
    ]

    for pattern, event_name in generic_patterns:

        if re.search(
            pattern,
            text_lower
        ):
            return event_name

    return "Unknown"


# ============================================================
# TIME EXTRACTION
# ============================================================

def extract_time(text: str):
    """
    Extract an explicitly mentioned time expression.

    Returns 'Not specified' when the evidence does not
    contain a time reference.
    """

    time_patterns = [

        # Dates
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",

        # Years
        r"\b(?:19|20)\d{2}\b",

        # Months
        r"\b(?:January|February|March|April|May|June|July|"
        r"August|September|October|November|December)"
        r"(?:\s+\d{4})?\b",

        # Relative time
        r"\b(?:today|yesterday|tomorrow|"
        r"recently|previously|currently|"
        r"earlier|later|during peak usage|"
        r"peak usage|during deployment)\b",

        # Time periods
        r"\b(?:morning|afternoon|evening|night|"
        r"week|month|year|quarter)\b"
    ]

    for pattern in time_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(0)

    return "Not specified"


# ============================================================
# CLAIM EXTRACTION RESULT
# ============================================================

def extract_claim_information(
    evidence: str,
    source: str = "TechNova Solutions"
):
    """
    Wrapper function used by the application.

    Returns a consistent structure that can later be
    consumed by the causal reasoning and graph modules.
    """

    claims = extract_claims(
        evidence=evidence,
        source=source
    )

    return {
        "success": True,
        "claim_count": len(claims),
        "claims": claims
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_evidence = (
        "System latency increased because database traffic "
        "increased during peak usage."
    )

    result = extract_claim_information(
        test_evidence
    )

    print("\n" + "=" * 60)
    print("CLAIM EXTRACTION TEST")
    print("=" * 60)

    print("\nInput Evidence:")
    print(test_evidence)

    print("\nExtracted Claims:")

    for index, claim in enumerate(
        result["claims"],
        start=1
    ):

        print(f"\nClaim {index}:")
        print("Claim:", claim["claim"])
        print("Source:", claim["source"])
        print("Evidence:", claim["evidence"])
        print("Entity:", claim["entity"])
        print("Event:", claim["event"])
        print("Time:", claim["time"])

    print("\n" + "=" * 60)