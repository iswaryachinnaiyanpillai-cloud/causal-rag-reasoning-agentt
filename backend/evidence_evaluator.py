# ============================================================
# EVIDENCE EVALUATOR
# Causal RAG Agent - TechNova Solutions
# ============================================================

import re


# ============================================================
# HELPERS
# ============================================================

def normalize_value(value):
    """
    Convert a value into a normalized uppercase string.
    """

    if value is None:
        return ""

    return str(value).strip().upper()


def get_claim_text(claim):
    """
    Extract readable claim text from a claim object.
    """

    if isinstance(claim, dict):

        return str(
            claim.get("claim")
            or claim.get("evidence")
            or claim.get("text")
            or ""
        )

    return str(claim or "")


# ============================================================
# CORRELATION DETECTION
# ============================================================

def contains_correlation_language(text):
    """
    Detect explicit evidence that a relationship is
    correlational rather than causally established.
    """

    text = str(text or "").lower()

    correlation_patterns = [

        "correlation_only",
        "correlation only",
        "correlation without strong causation",
        "correlational",
        "correlation",
        "correlated",
        "associated with",
        "association",
        "changed together",
        "increased together",
        "same period",
        "relationship is correlational",
        "relationship is correlation",

        "does not establish direct causation",
        "does not establish causation",

        "direct causation is not established",
        "direct causation was not established",

        "direct causation is not confirmed",
        "direct causation was not confirmed",

        "causation is not established",
        "causation was not established",

        "causation is not confirmed",

        "causal relationship was not established",
        "causal relationship was not confirmed",

        "no direct causal evidence",
        "no direct evidence establishes",
        "no direct evidence confirms",

        "direct causation not confirmed",

        "causal status correlation only",
    ]

    return any(
        pattern in text
        for pattern in correlation_patterns
    )


# ============================================================
# INSUFFICIENT EVIDENCE DETECTION
# ============================================================

def contains_insufficient_language(text):
    """
    Detect explicit statements that the available evidence
    is insufficient to establish a cause.
    """

    text = str(text or "").lower()

    insufficient_patterns = [

        "insufficient evidence",
        "not enough evidence",
        "no reliable cause",
        "unknown cause",

        "cause could not be determined",
        "cannot determine the cause",
        "unable to determine the cause",

        "causality not confirmed",

        "causal relationship cannot be determined",

        "cause cannot be determined",

        "no reliable evidence identifies",

        "no evidence identifies a specific cause",

        "no evidence identifies the cause",
    ]

    return any(
        pattern in text
        for pattern in insufficient_patterns
    )


# ============================================================
# RELATIONSHIP INFERENCE
# ============================================================

def infer_relationship(claim):
    """
    Determine the relationship type of a claim.

    Priority:
        1. Explicit relationship field
        2. Explicit correlation language
        3. Explicit causal wording
        4. UNKNOWN
    """

    if isinstance(claim, dict):

        relationship = normalize_value(
            claim.get(
                "relationship",
                ""
            )
        )

        if relationship in {
            "CAUSAL",
            "CORRELATION",
            "UNKNOWN",
        }:

            return relationship


        for field in [
            "relation",
            "relationship_type",
            "causal_relationship",
            "type",
        ]:

            value = normalize_value(
                claim.get(
                    field,
                    ""
                )
            )

            if value in {
                "CAUSAL",
                "CORRELATION",
                "UNKNOWN",
            }:

                return value


    text = get_claim_text(
        claim
    )

    text_lower = text.lower()


    # --------------------------------------------------------
    # Correlation has priority
    # --------------------------------------------------------

    correlation_patterns = [

        "correlation_only",
        "correlation only",
        "correlational",
        "correlation",
        "correlated",
        "associated with",
        "association",
        "changed together",
        "increased together",
        "same period",
        "relationship is correlational",

        "does not establish direct causation",
        "does not establish causation",

        "direct causation is not established",
        "direct causation was not established",

        "direct causation is not confirmed",
        "direct causation was not confirmed",

        "causation is not established",
        "causation was not established",

        "causation is not confirmed",

        "causal relationship was not established",
        "causal relationship was not confirmed",

        "no direct causal evidence",
        "no direct evidence establishes",
        "no direct evidence confirms",
    ]


    for pattern in correlation_patterns:

        if pattern in text_lower:
            return "CORRELATION"


    # --------------------------------------------------------
    # Causal detection
    # --------------------------------------------------------

    causal_patterns = [

        r"\bcaused\b",
        r"\bcause\b",
        r"\bcausing\b",
        r"\bled to\b",
        r"\blead to\b",
        r"\bresulted in\b",
        r"\bresult in\b",
        r"\bcontributed to\b",
        r"\bdue to\b",
        r"\bbecause\b",
        r"\bresponsible for\b",
        r"\btriggered\b",
        r"\bproduced\b",
        r"\bresulting in\b",
    ]


    for pattern in causal_patterns:

        if re.search(
            pattern,
            text_lower
        ):

            return "CAUSAL"


    return "UNKNOWN"


# ============================================================
# CONFIDENCE INFERENCE
# ============================================================

def infer_confidence(claim):
    """
    Determine confidence level for an individual claim.
    """

    if isinstance(claim, dict):

        confidence = normalize_value(
            claim.get(
                "confidence",
                ""
            )
        )

        if confidence in {
            "HIGH",
            "MEDIUM",
            "LOW",
        }:

            return confidence


        for field in [
            "confidence_level",
            "evidence_confidence",
            "certainty",
        ]:

            value = normalize_value(
                claim.get(
                    field,
                    ""
                )
            )

            if value in {
                "HIGH",
                "MEDIUM",
                "LOW",
            }:

                return value


    relationship = infer_relationship(
        claim
    )


    if relationship == "CAUSAL":
        return "HIGH"

    if relationship == "CORRELATION":
        return "MEDIUM"

    return "LOW"


# ============================================================
# MAIN EVIDENCE EVALUATOR
# ============================================================

def evaluate_evidence(
    claims,
    evidence=""
):
    """
    Evaluate extracted evidence claims.

    The second argument, evidence, is optional so this
    function is compatible with the Causal Analyzer.

    Handles:
        CAUSAL
        CORRELATION
        UNKNOWN

    Uses explicit evidence text to prevent correlation-only
    evidence from being promoted to strong causation.
    """

    # --------------------------------------------------------
    # Normalize inputs
    # --------------------------------------------------------

    if claims is None:
        claims = []

    if not isinstance(
        claims,
        list
    ):

        claims = [
            claims
        ]


    evidence_text = str(
        evidence or ""
    )


    # --------------------------------------------------------
    # Empty claims
    # --------------------------------------------------------

    if not claims:

        # If evidence itself explicitly says correlation,
        # report that rather than pretending there is no
        # evidence at all.
        if contains_correlation_language(
            evidence_text
        ):

            return {

                "success": True,

                "strength": "MODERATE",

                "confidence": "MEDIUM",

                "claim_count": 0,

                "causal_claims": 0,

                "correlation_claims": 0,

                "unknown_claims": 0,

                "high_confidence_claims": 0,

                "medium_confidence_claims": 0,

                "low_confidence_claims": 0,

                "causal_conclusion":
                    "CORRELATION_ONLY",

                "evaluation_summary": (
                    "No structured claims were available, "
                    "but the evidence explicitly supports "
                    "correlation only."
                ),
            }


        if contains_insufficient_language(
            evidence_text
        ):

            return {

                "success": True,

                "strength": "INSUFFICIENT",

                "confidence": "LOW",

                "claim_count": 0,

                "causal_claims": 0,

                "correlation_claims": 0,

                "unknown_claims": 0,

                "high_confidence_claims": 0,

                "medium_confidence_claims": 0,

                "low_confidence_claims": 0,

                "causal_conclusion":
                    "NOT_SUPPORTED",

                "evaluation_summary": (
                    "The available evidence is "
                    "insufficient to establish a "
                    "causal relationship."
                ),
            }


        return {

            "success": True,

            "strength": "INSUFFICIENT",

            "confidence": "LOW",

            "claim_count": 0,

            "causal_claims": 0,

            "correlation_claims": 0,

            "unknown_claims": 0,

            "high_confidence_claims": 0,

            "medium_confidence_claims": 0,

            "low_confidence_claims": 0,

            "causal_conclusion":
                "NOT_SUPPORTED",

            "evaluation_summary": (
                "No evidence claims were available "
                "for evaluation."
            ),
        }


    # --------------------------------------------------------
    # Counters
    # --------------------------------------------------------

    causal_count = 0

    correlation_count = 0

    unknown_count = 0

    high_confidence = 0

    medium_confidence = 0

    low_confidence = 0


    # --------------------------------------------------------
    # Combine claim text + retrieved evidence
    #
    # Including the raw evidence is important because the
    # evidence may explicitly state that causation was not
    # established.
    # --------------------------------------------------------

    claim_text = "\n".join(
        get_claim_text(claim)
        for claim in claims
    )


    all_text = (
        claim_text
        + "\n"
        + evidence_text
    )


    # --------------------------------------------------------
    # Global statuses
    # --------------------------------------------------------

    global_correlation_only = (
        contains_correlation_language(
            all_text
        )
    )


    global_insufficient = (
        contains_insufficient_language(
            all_text
        )
    )


    # --------------------------------------------------------
    # Evaluate every claim
    # --------------------------------------------------------

    for claim in claims:

        relationship = infer_relationship(
            claim
        )


        confidence = infer_confidence(
            claim
        )


        if relationship == "CAUSAL":

            causal_count += 1

        elif relationship == "CORRELATION":

            correlation_count += 1

        else:

            unknown_count += 1


        if confidence == "HIGH":

            high_confidence += 1

        elif confidence == "MEDIUM":

            medium_confidence += 1

        else:

            low_confidence += 1


    # ========================================================
    # GLOBAL CORRELATION OVERRIDE
    # ========================================================

    if global_correlation_only:

        strength = "MODERATE"

        overall_confidence = "MEDIUM"

        causal_conclusion = (
            "CORRELATION_ONLY"
        )


    # ========================================================
    # GLOBAL INSUFFICIENT OVERRIDE
    # ========================================================

    elif global_insufficient:

        strength = "INSUFFICIENT"

        overall_confidence = "LOW"

        causal_conclusion = (
            "NOT_SUPPORTED"
        )


    # ========================================================
    # STRONG CAUSAL EVIDENCE
    # ========================================================

    elif (
        causal_count >= 3
        and high_confidence >= 3
    ):

        strength = "STRONG"

        overall_confidence = "HIGH"

        causal_conclusion = (
            "SUPPORTED"
        )


    elif (
        causal_count >= 1
        and high_confidence >= 1
    ):

        strength = "STRONG"

        overall_confidence = "HIGH"

        causal_conclusion = (
            "SUPPORTED"
        )


    # ========================================================
    # MODERATE CAUSAL EVIDENCE
    # ========================================================

    elif (
        causal_count >= 1
        and medium_confidence >= 1
    ):

        strength = "MODERATE"

        overall_confidence = "MEDIUM"

        causal_conclusion = (
            "SUPPORTED"
        )


    # ========================================================
    # CORRELATION
    # ========================================================

    elif correlation_count >= 1:

        strength = "MODERATE"

        overall_confidence = "MEDIUM"

        causal_conclusion = (
            "CORRELATION_ONLY"
        )


    # ========================================================
    # UNKNOWN
    # ========================================================

    else:

        strength = "INSUFFICIENT"

        overall_confidence = "LOW"

        causal_conclusion = (
            "NOT_SUPPORTED"
        )


    # ========================================================
    # SUMMARY
    # ========================================================

    summary = (
        f"Evaluated {len(claims)} evidence claim(s). "
        f"Causal claims: {causal_count}. "
        f"Correlation claims: {correlation_count}. "
        f"Unknown claims: {unknown_count}. "
        f"Evidence strength: {strength}. "
        f"Confidence: {overall_confidence}."
    )


    if global_correlation_only:

        summary += (
            " The evidence explicitly indicates "
            "that the observed relationship is "
            "correlational and does not establish "
            "direct causation."
        )


    elif global_insufficient:

        summary += (
            " The available evidence is insufficient "
            "to establish a reliable causal relationship."
        )


    # ========================================================
    # RETURN
    # ========================================================

    return {

        "success": True,

        "strength": strength,

        "confidence": overall_confidence,

        "claim_count": len(claims),

        "causal_claims": causal_count,

        "correlation_claims": correlation_count,

        "unknown_claims": unknown_count,

        "high_confidence_claims":
            high_confidence,

        "medium_confidence_claims":
            medium_confidence,

        "low_confidence_claims":
            low_confidence,

        "causal_conclusion":
            causal_conclusion,

        "evaluation_summary":
            summary,
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_claims = [

        {
            "claim": (
                "Database overload directly contributed "
                "to the production system failure."
            ),

            "source":
                "TechNova Solutions",

            "evidence": (
                "Database overload directly contributed "
                "to the production system failure."
            ),

            "entity":
                "Database",

            "event":
                "System failure",

            "time":
                "Not specified",
        },

        {
            "claim": (
                "System latency increased because "
                "database traffic increased."
            ),

            "relationship":
                "CAUSAL",

            "confidence":
                "HIGH",
        },

        {
            "claim": (
                "Increased database traffic led to "
                "higher database load."
            ),

            "relationship":
                "CAUSAL",

            "confidence":
                "HIGH",
        },

        {
            "claim": (
                "Increased database traffic is associated "
                "with higher system latency."
            ),

            "relationship":
                "CORRELATION",

            "confidence":
                "MEDIUM",
        },
    ]


    result = evaluate_evidence(
        test_claims,
        ""
    )


    print()
    print("=" * 60)
    print("EVIDENCE EVALUATION TEST")
    print("=" * 60)


    print(
        "\nEvidence Strength:",
        result["strength"]
    )

    print(
        "\nConfidence:",
        result["confidence"]
    )

    print(
        "\nClaim Count:",
        result["claim_count"]
    )

    print(
        "\nCausal Claims:",
        result["causal_claims"]
    )

    print(
        "\nCorrelation Claims:",
        result["correlation_claims"]
    )

    print(
        "\nUnknown Claims:",
        result["unknown_claims"]
    )

    print(
        "\nCausal Conclusion:",
        result["causal_conclusion"]
    )

    print(
        "\nEvaluation Summary:",
        result["evaluation_summary"]
    )

    print(
        "\n" + "=" * 60
    )