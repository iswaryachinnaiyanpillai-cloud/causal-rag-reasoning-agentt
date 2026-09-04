# ============================================================
# CAUSE-EFFECT EXTRACTOR
# Causal RAG Agent
# TechNova Solutions
# ============================================================

import re


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text: str) -> str:
    """
    Clean extracted cause/effect text.
    """

    if not text:
        return ""

    cleaned = str(text).strip()

    # Remove markdown/punctuation from beginning
    cleaned = re.sub(
        r"^[,;:*_\-\s]+",
        "",
        cleaned
    )

    # Remove markdown/punctuation from end
    cleaned = re.sub(
        r"[,;:*_\-\s]+$",
        "",
        cleaned
    )

    # Remove repeated whitespace
    cleaned = re.sub(
        r"\s+",
        " ",
        cleaned
    )

    return cleaned.strip()


# ============================================================
# NORMALIZE CLAIM INPUT
# ============================================================

def normalize_claims(claims):
    """
    Normalize different claim input formats into a
    list of text claims.

    Accepted:
        - string
        - list of strings
        - list of dictionaries
    """

    if not claims:
        return []

    # Single string
    if isinstance(claims, str):
        return [claims]

    # List / iterable
    if isinstance(claims, list):
        normalized = []

        for item in claims:

            if isinstance(item, dict):

                claim_text = item.get(
                    "claim",
                    item.get(
                        "evidence",
                        item.get(
                            "text",
                            ""
                        )
                    )
                )

            else:

                claim_text = str(item)

            claim_text = clean_text(
                claim_text
            )

            if claim_text:
                normalized.append(
                    claim_text
                )

        return normalized

    return [
        clean_text(str(claims))
    ]


# ============================================================
# SINGLE CLAIM EXTRACTION
# ============================================================

def extract_single_cause_effect(claim: str):
    """
    Extract cause-effect relationship from one claim.

    Returns:
        success
        cause
        effect
        relationship
        evidence
        confidence
    """

    if not claim or not str(claim).strip():

        return {
            "success": False,
            "cause": None,
            "effect": None,
            "relationship": "UNKNOWN",
            "evidence": "",
            "confidence": "LOW"
        }

    text = str(claim).strip()

    # ========================================================
    # NECESSITY / STRONG CAUSAL LANGUAGE
    # ========================================================

    necessity_patterns = [

        # X necessarily caused Y
        (
            r"(.+?)\s+necessarily\s+(?:caused|causes)\s+(.+)",
            "NORMAL"
        ),

        # X must have caused Y
        (
            r"(.+?)\s+must\s+have\s+(?:caused|causes)\s+(.+)",
            "NORMAL"
        ),

        # X directly caused Y
        (
            r"(.+?)\s+directly\s+(?:caused|causes)\s+(.+)",
            "NORMAL"
        )
    ]

    for pattern, direction in necessity_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if not match:
            continue

        first = clean_text(
            match.group(1)
        )

        second = clean_text(
            match.group(2)
        )

        if not first or not second:
            continue

        if direction == "NORMAL":

            cause = first
            effect = second

        else:

            effect = first
            cause = second

        return {
            "success": True,
            "cause": cause,
            "effect": effect,
            "relationship": "CAUSAL",
            "evidence": text,
            "confidence": "HIGH"
        }

    # ========================================================
    # DIRECT CAUSAL PATTERNS
    # ========================================================

    causal_patterns = [

        # X caused Y
        (
            r"(.+?)\s+(?:caused|causes)\s+(.+)",
            "NORMAL"
        ),

        # X resulted in Y
        (
            r"(.+?)\s+(?:resulted|results)\s+in\s+(.+)",
            "NORMAL"
        ),

        # X led to Y
        (
            r"(.+?)\s+(?:led|leads)\s+to\s+(.+)",
            "NORMAL"
        ),

        # X triggered Y
        (
            r"(.+?)\s+(?:triggered|triggers)\s+(.+)",
            "NORMAL"
        ),

        # X contributed to Y
        (
            r"(.+?)\s+(?:contributed|contributes)\s+to\s+(.+)",
            "NORMAL"
        ),

        # X caused Y to happen
        (
            r"(.+?)\s+(?:caused|causes)\s+(.+?)\s+to\s+(?:happen|occur)",
            "NORMAL"
        ),

        # X, causing Y
        (
            r"(.+?),\s*(?:causing|which caused|which causes)\s+(.+)",
            "NORMAL"
        ),

        # X was caused by Y
        (
            r"(.+?)\s+(?:was|were)\s+caused\s+by\s+(.+)",
            "REVERSED"
        ),

        # X because Y
        (
            r"(.+?)\s+because\s+(.+)",
            "REVERSED"
        ),

        # X due to Y
        (
            r"(.+?)\s+due\s+to\s+(.+)",
            "REVERSED"
        ),

        # X as a result of Y
        (
            r"(.+?)\s+as\s+a\s+result\s+of\s+(.+)",
            "REVERSED"
        )
    ]

    for pattern, direction in causal_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if not match:
            continue

        first = clean_text(
            match.group(1)
        )

        second = clean_text(
            match.group(2)
        )

        if not first or not second:
            continue

        if direction == "NORMAL":

            cause = first
            effect = second

        else:

            effect = first
            cause = second

        return {
            "success": True,
            "cause": cause,
            "effect": effect,
            "relationship": "CAUSAL",
            "evidence": text,
            "confidence": "HIGH"
        }

    # ========================================================
    # CORRELATION PATTERNS
    # ========================================================

    correlation_patterns = [

        # X is associated with Y
        r"(.+?)\s+(?:is|was|are|were)\s+associated\s+with\s+(.+)",

        # X correlates with Y
        r"(.+?)\s+correlat(?:es|ed|ing)\s+with\s+(.+)",

        # X is related to Y
        r"(.+?)\s+(?:is|was|are|were)\s+related\s+to\s+(.+)",

        # X is linked to Y
        r"(.+?)\s+(?:is|was|are|were)\s+linked\s+to\s+(.+)",

        # X and Y increased/decreased together
        r"(.+?)\s+and\s+(.+?)\s+(?:increased|decreased)\s+together"
    ]

    for pattern in correlation_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if not match:
            continue

        first = clean_text(
            match.group(1)
        )

        second = clean_text(
            match.group(2)
        )

        if not first or not second:
            continue

        return {
            "success": True,
            "cause": first,
            "effect": second,
            "relationship": "CORRELATION",
            "evidence": text,
            "confidence": "MEDIUM"
        }

    # ========================================================
    # NO RELATIONSHIP FOUND
    # ========================================================

    return {
        "success": True,
        "cause": None,
        "effect": None,
        "relationship": "UNKNOWN",
        "evidence": text,
        "confidence": "LOW"
    }


# ============================================================
# MULTIPLE CLAIMS
# ============================================================

def extract_cause_effect(claims):
    """
    Extract cause-effect relationships.

    Accepts:
        - one string
        - list of strings
        - list of dictionaries

    Returns:
        list of structured relationships
    """

    normalized_claims = normalize_claims(
        claims
    )

    if not normalized_claims:
        return []

    results = []

    for claim_text in normalized_claims:

        result = extract_single_cause_effect(
            claim_text
        )

        results.append(result)

    return results


# ============================================================
# ALIAS FOR MULTIPLE CLAIMS
# ============================================================

def extract_cause_effects(claims):
    """
    Alias for extracting multiple cause-effect relationships.
    """

    return extract_cause_effect(
        claims
    )


# ============================================================
# STRUCTURED CAUSAL INFORMATION
# ============================================================

def extract_causal_information(claims):
    """
    Return structured causal information.
    """

    normalized_claims = normalize_claims(
        claims
    )

    relationships = extract_cause_effect(
        normalized_claims
    )

    causal_relationships = [
        item
        for item in relationships
        if item.get(
            "relationship"
        ) == "CAUSAL"
    ]

    correlation_relationships = [
        item
        for item in relationships
        if item.get(
            "relationship"
        ) == "CORRELATION"
    ]

    unknown_relationships = [
        item
        for item in relationships
        if item.get(
            "relationship"
        ) == "UNKNOWN"
    ]

    return {

        "success": True,

        "total_claims": len(
            normalized_claims
        ),

        "causal_count": len(
            causal_relationships
        ),

        "correlation_count": len(
            correlation_relationships
        ),

        "unknown_count": len(
            unknown_relationships
        ),

        "causal_relationships":
            causal_relationships,

        "correlation_relationships":
            correlation_relationships,

        "unknown_relationships":
            unknown_relationships
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_claims = [

        "Database overload caused system failure.",

        "System latency increased because database traffic increased.",

        "Increased database traffic led to higher database load.",

        "Higher database load caused increased processing time.",

        "Increased processing time resulted in higher system latency.",

        "Increased database traffic is associated with higher system latency.",

        "Server performance decreased."
    ]

    print("\n" + "=" * 70)

    print(
        "CAUSE-EFFECT EXTRACTION TEST"
    )

    print("=" * 70)

    results = extract_cause_effect(
        test_claims
    )

    for index, result in enumerate(
        results,
        start=1
    ):

        print(
            f"\nClaim {index}:"
        )

        print(
            "Evidence:",
            result["evidence"]
        )

        print(
            "Cause:",
            result["cause"]
        )

        print(
            "Effect:",
            result["effect"]
        )

        print(
            "Relationship:",
            result["relationship"]
        )

        print(
            "Confidence:",
            result["confidence"]
        )

    # ========================================================
    # STRUCTURED SUMMARY
    # ========================================================

    summary = extract_causal_information(
        test_claims
    )

    print("\n" + "-" * 70)

    print(
        "STRUCTURED SUMMARY"
    )

    print("-" * 70)

    print(
        "Total Claims:",
        summary["total_claims"]
    )

    print(
        "Causal Relationships:",
        summary["causal_count"]
    )

    print(
        "Correlation Relationships:",
        summary["correlation_count"]
    )

    print(
        "Unknown Relationships:",
        summary["unknown_count"]
    )

    print("\n" + "=" * 70)

    print(
        "CAUSE-EFFECT EXTRACTION TEST COMPLETED"
    )

    print("=" * 70)