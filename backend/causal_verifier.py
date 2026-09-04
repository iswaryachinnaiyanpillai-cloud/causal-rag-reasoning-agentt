# ============================================================
# CAUSAL VERIFIER
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


def infer_relationship(claim):
    """
    Determine the relationship type of a claim.

    Priority:
    1. Explicit relationship field
    2. Alternate relationship fields
    3. Causal wording
    4. Correlation wording
    5. UNKNOWN
    """

    if isinstance(claim, dict):

        # ----------------------------------------------------
        # Explicit relationship
        # ----------------------------------------------------

        relationship = normalize_value(
            claim.get("relationship", "")
        )

        if relationship in {
            "CAUSAL",
            "CORRELATION",
            "UNKNOWN"
        }:
            return relationship

        # ----------------------------------------------------
        # Alternate relationship fields
        # ----------------------------------------------------

        for field in [
            "relation",
            "relationship_type",
            "causal_relationship",
            "type"
        ]:

            value = normalize_value(
                claim.get(field, "")
            )

            if value in {
                "CAUSAL",
                "CORRELATION",
                "UNKNOWN"
            }:
                return value

        text = str(
            claim.get("claim", "")
        )

    else:

        text = str(claim or "")

    text = text.lower()

    # --------------------------------------------------------
    # CORRELATION
    # --------------------------------------------------------

    correlation_patterns = [
        "correlation",
        "correlated",
        "associated with",
        "association",
        "changed together",
        "increased together",
        "same period",
        "relationship is correlational",
        "does not establish direct causation",
        "direct causation is not established",
        "causation is not established"
    ]

    for pattern in correlation_patterns:

        if pattern in text:
            return "CORRELATION"

    # --------------------------------------------------------
    # CAUSAL
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
        r"\bdirectly contributed\b"
    ]

    for pattern in causal_patterns:

        if re.search(
            pattern,
            text
        ):
            return "CAUSAL"

    return "UNKNOWN"


def infer_confidence(claim):
    """
    Determine confidence level of a claim.

    Priority:
    1. Explicit confidence field
    2. Alternate confidence fields
    3. Infer from relationship
    """

    if isinstance(claim, dict):

        confidence = normalize_value(
            claim.get("confidence", "")
        )

        if confidence in {
            "HIGH",
            "MEDIUM",
            "LOW"
        }:
            return confidence

        for field in [
            "confidence_level",
            "evidence_confidence",
            "certainty"
        ]:

            value = normalize_value(
                claim.get(field, "")
            )

            if value in {
                "HIGH",
                "MEDIUM",
                "LOW"
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
# MAIN VERIFIER
# ============================================================

def verify_causality(
    cause_effect_claims,
    evidence_evaluation=None
):
    """
    Verify whether the available evidence supports
    the extracted causal relationships.

    Possible results:
        CAUSALITY_SUPPORTED
        CAUSALITY_NOT_SUPPORTED
        INSUFFICIENT_EVIDENCE

    The verifier can handle claims with or without explicit
    relationship and confidence fields.
    """

    # --------------------------------------------------------
    # HANDLE EMPTY CLAIMS
    # --------------------------------------------------------

    if not cause_effect_claims:

        return {
            "success": True,
            "status": "INSUFFICIENT_EVIDENCE",
            "confidence": "LOW",
            "verified_claims": 0,
            "unsupported_claims": 0,
            "correlation_claims": 0,
            "unknown_claims": 0,
            "verification_summary": (
                "No cause-effect claims were available "
                "for causal verification."
            )
        }

    # --------------------------------------------------------
    # COUNTERS
    # --------------------------------------------------------

    verified_claims = 0
    unsupported_claims = 0
    correlation_claims = 0
    unknown_claims = 0

    # --------------------------------------------------------
    # EVALUATE EACH CLAIM
    # --------------------------------------------------------

    for claim in cause_effect_claims:

        relationship = infer_relationship(
            claim
        )

        confidence_level = infer_confidence(
            claim
        )

        # ----------------------------------------------------
        # CAUSAL RELATIONSHIP
        # ----------------------------------------------------

        if relationship == "CAUSAL":

            if confidence_level in (
                "HIGH",
                "MEDIUM"
            ):

                verified_claims += 1

            else:

                unsupported_claims += 1

        # ----------------------------------------------------
        # CORRELATION
        # Correlation does NOT mean causation.
        # ----------------------------------------------------

        elif relationship == "CORRELATION":

            correlation_claims += 1

        # ----------------------------------------------------
        # UNKNOWN
        # ----------------------------------------------------

        else:

            unknown_claims += 1

    # ========================================================
    # DETERMINE VERIFICATION STATUS
    # ========================================================

    if verified_claims > 0:

        if (
            unsupported_claims == 0
            and correlation_claims == 0
            and unknown_claims == 0
        ):

            status = "CAUSALITY_SUPPORTED"
            verification_confidence = "HIGH"

        else:

            status = "CAUSALITY_SUPPORTED"
            verification_confidence = "MEDIUM"

    elif correlation_claims > 0:

        status = "CAUSALITY_NOT_SUPPORTED"
        verification_confidence = "LOW"

    else:

        status = "INSUFFICIENT_EVIDENCE"
        verification_confidence = "LOW"

    # ========================================================
    # VERIFICATION SUMMARY
    # ========================================================

    summary = (
        f"Verified causal claims: {verified_claims}. "
        f"Unsupported causal claims: {unsupported_claims}. "
        f"Correlation claims: {correlation_claims}. "
        f"Unknown claims: {unknown_claims}. "
        f"Causal verification status: {status}. "
        f"Confidence: {verification_confidence}."
    )

    # ========================================================
    # RETURN RESULT
    # ========================================================

    return {
        "success": True,
        "status": status,
        "confidence": verification_confidence,
        "verified_claims": verified_claims,
        "unsupported_claims": unsupported_claims,
        "correlation_claims": correlation_claims,
        "unknown_claims": unknown_claims,
        "verification_summary": summary
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
            "source": "TechNova Solutions",
            "evidence": (
                "Database overload directly contributed "
                "to the production system failure."
            ),
            "entity": "Database",
            "event": "System failure",
            "time": "Not specified"
        },

        {
            "claim": (
                "Increased database traffic led to "
                "higher database load."
            ),
            "relationship": "CAUSAL",
            "confidence": "HIGH"
        },

        {
            "claim": (
                "Increased database traffic is associated "
                "with higher system latency."
            ),
            "relationship": "CORRELATION",
            "confidence": "MEDIUM"
        },

        {
            "claim": (
                "Server performance decreased."
            ),
            "relationship": "UNKNOWN",
            "confidence": "LOW"
        }
    ]

    result = verify_causality(
        test_claims
    )

    print("\n" + "=" * 60)
    print("CAUSAL VERIFICATION TEST")
    print("=" * 60)

    print("\nVerification Status:")
    print(result["status"])

    print("\nConfidence:")
    print(result["confidence"])

    print("\nVerified Claims:")
    print(result["verified_claims"])

    print("\nUnsupported Claims:")
    print(result["unsupported_claims"])

    print("\nCorrelation Claims:")
    print(result["correlation_claims"])

    print("\nUnknown Claims:")
    print(result["unknown_claims"])

    print("\nVerification Summary:")
    print(result["verification_summary"])

    print("\n" + "=" * 60)