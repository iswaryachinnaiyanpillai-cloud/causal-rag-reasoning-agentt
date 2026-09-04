# ============================================================
# CAUSAL ANALYSIS EVALUATOR
# Causal RAG Agent - TechNova Solutions
# ============================================================


# ============================================================
# HELPERS
# ============================================================

def _clean_list(values):
    """
    Convert a list-like value into a clean string list.
    """

    if values is None:
        return []

    if not isinstance(values, list):
        values = [values]

    result = []

    for value in values:

        if value is None:
            continue

        text = str(value).strip()

        if text:
            result.append(text)

    return result


def _get_chain_from_information(
    causal_information
):
    """
    Try to recover a richer causal chain from the
    causal_information object when available.
    """

    if not isinstance(
        causal_information,
        dict
    ):
        return []

    possible_keys = [
        "chain",
        "causal_chain",
        "reasoning_chain",
        "causal_path"
    ]

    for key in possible_keys:

        value = causal_information.get(
            key
        )

        chain = _clean_list(value)

        if chain:
            return chain

    return []


def _get_intermediate_factors(
    causal_information
):
    """
    Read intermediate factors from the causal information.
    Supports all naming styles used in the project.
    """

    if not isinstance(
        causal_information,
        dict
    ):
        return []

    possible_keys = [
        "factors",
        "intermediate_factors",
        "intermediateFactors"
    ]

    for key in possible_keys:

        value = causal_information.get(
            key
        )

        factors = _clean_list(value)

        if factors:
            return factors

    return []


# ============================================================
# MAIN EVALUATOR
# ============================================================

def evaluate_analysis(
    causal_information,
    causal_chain,
    evidence_evaluation,
    causal_verification
):
    """
    Evaluate the overall quality of the causal analysis.

    Handles:

    1. Strong causal evidence
    2. Moderate/weak evidence
    3. Correlation-only evidence
    4. Insufficient evidence
    5. Multi-step causal chains
    """

    # ========================================================
    # NORMALIZE INPUTS
    # ========================================================

    if not isinstance(
        causal_information,
        dict
    ):
        causal_information = {}

    if not isinstance(
        causal_chain,
        list
    ):
        causal_chain = []

    if not isinstance(
        evidence_evaluation,
        dict
    ):
        evidence_evaluation = {}

    if not isinstance(
        causal_verification,
        dict
    ):
        causal_verification = {}

    # ========================================================
    # CLEAN CAUSAL CHAIN
    # ========================================================

    valid_chain = _clean_list(
        causal_chain
    )

    # ========================================================
    # FALLBACK CHAIN
    #
    # Sometimes the analyzer may expose the full chain
    # inside causal_information even when the direct
    # causal_chain field is shorter.
    # ========================================================

    information_chain = (
        _get_chain_from_information(
            causal_information
        )
    )

    if (
        len(information_chain)
        > len(valid_chain)
    ):

        valid_chain = information_chain

    # ========================================================
    # READ INTERMEDIATE FACTORS
    # ========================================================

    intermediate_factors = (
        _get_intermediate_factors(
            causal_information
        )
    )

    # ========================================================
    # READ EVIDENCE INFORMATION
    # ========================================================

    evidence_strength = str(
        evidence_evaluation.get(
            "strength",
            evidence_evaluation.get(
                "evidence_strength",
                "INSUFFICIENT"
            )
        )
    ).upper().strip()

    evidence_confidence = str(
        evidence_evaluation.get(
            "confidence",
            "LOW"
        )
    ).upper().strip()

    # ========================================================
    # READ VERIFICATION
    # ========================================================

    verification_status = str(
        causal_verification.get(
            "status",
            "INSUFFICIENT_EVIDENCE"
        )
    ).upper().strip()

    verification_confidence = str(
        causal_verification.get(
            "confidence",
            "LOW"
        )
    ).upper().strip()

    # ========================================================
    # STATUS FROM CAUSAL INFORMATION
    # ========================================================

    information_status = str(
        causal_information.get(
            "status",
            ""
        )
    ).upper().strip()

    # ========================================================
    # INSUFFICIENT EVIDENCE
    # ========================================================

    insufficient_evidence = (
        verification_status
        == "INSUFFICIENT_EVIDENCE"
        or evidence_strength
        == "INSUFFICIENT"
        or information_status
        == "INSUFFICIENT_EVIDENCE"
    )

    # ========================================================
    # CORRELATION ONLY
    # ========================================================

    correlation_only = (
        not insufficient_evidence
        and (
            verification_status
            in {
                "CORRELATION_ONLY",
                "CAUSALITY_NOT_SUPPORTED"
            }
            or information_status
            == "CORRELATION_ONLY"
            or (
                evidence_evaluation.get(
                    "causal_conclusion",
                    ""
                )
                == "CORRELATION_ONLY"
            )
        )
    )

    # ========================================================
    # NORMALIZE INSUFFICIENT
    # ========================================================

    if insufficient_evidence:

        verification_status = (
            "INSUFFICIENT_EVIDENCE"
        )

        evidence_strength = (
            "INSUFFICIENT"
        )

        evidence_confidence = "LOW"

        verification_confidence = "LOW"

    # ========================================================
    # NORMALIZE CORRELATION
    # ========================================================

    elif correlation_only:

        verification_status = (
            "CORRELATION_ONLY"
        )

        if evidence_strength not in {
            "STRONG",
            "MODERATE",
            "WEAK"
        }:

            evidence_strength = "MODERATE"

        evidence_confidence = "MEDIUM"

        verification_confidence = "MEDIUM"

    # ========================================================
    # CAUSAL CHAIN QUALITY
    # ========================================================

    if insufficient_evidence:

        chain_quality = "INSUFFICIENT"

    elif correlation_only:

        chain_quality = "NOT_APPLICABLE"

    else:

        # ----------------------------------------------------
        # A 4+ node chain is clearly multi-step.
        # ----------------------------------------------------

        if len(valid_chain) >= 4:

            chain_quality = "EXCELLENT"

        elif len(valid_chain) == 3:

            chain_quality = "GOOD"

        elif len(valid_chain) == 2:

            # ------------------------------------------------
            # IMPORTANT:
            #
            # If a 2-node chain is accompanied by multiple
            # intermediate factors, it represents a richer
            # causal pathway than a simple basic relation.
            # ------------------------------------------------

            if len(intermediate_factors) >= 2:

                chain_quality = "EXCELLENT"

            elif len(intermediate_factors) == 1:

                chain_quality = "GOOD"

            else:

                chain_quality = "BASIC"

        elif len(valid_chain) == 1:

            chain_quality = "WEAK"

        else:

            # ------------------------------------------------
            # A causal analysis can still have a valid
            # relationship even when the explicit chain
            # field is missing.
            # ------------------------------------------------

            if len(intermediate_factors) >= 2:

                chain_quality = "EXCELLENT"

            elif len(intermediate_factors) == 1:

                chain_quality = "GOOD"

            else:

                chain_quality = "INSUFFICIENT"

    # ========================================================
    # EVIDENCE SCORE
    # ========================================================

    evidence_scores = {
        "STRONG": 40,
        "MODERATE": 30,
        "WEAK": 15,
        "INSUFFICIENT": 0
    }

    evidence_score = evidence_scores.get(
        evidence_strength,
        0
    )

    # ========================================================
    # VERIFICATION SCORE
    # ========================================================

    verification_scores = {
        "CAUSALITY_SUPPORTED": 40,
        "CAUSALITY_NOT_SUPPORTED": 0,
        "CAUSALITY_NOT_CONFIRMED": 0,
        "CORRELATION_ONLY": 30,
        "INSUFFICIENT_EVIDENCE": 0
    }

    verification_score = (
        verification_scores.get(
            verification_status,
            0
        )
    )

    # ========================================================
    # CHAIN SCORE
    # ========================================================

    chain_scores = {
        "EXCELLENT": 20,
        "GOOD": 20,
        "BASIC": 15,
        "WEAK": 5,
        "INSUFFICIENT": 0,
        "NOT_APPLICABLE": 0
    }

    chain_score = chain_scores.get(
        chain_quality,
        0
    )

    # ========================================================
    # OVERALL SCORE
    # ========================================================

    if insufficient_evidence:

        overall_score = 0

    elif correlation_only:

        # Correlation-only is intentionally not treated
        # as a fully confirmed causal analysis.
        overall_score = (
            evidence_score
            + verification_score
        )

    else:

        overall_score = (
            evidence_score
            + verification_score
            + chain_score
        )

    # Keep score between 0 and 100.

    overall_score = max(
        0,
        min(
            overall_score,
            100
        )
    )

    # ========================================================
    # OVERALL CONFIDENCE
    # ========================================================

    if insufficient_evidence:

        overall_confidence = "LOW"

    elif correlation_only:

        overall_confidence = "MEDIUM"

    elif (
        evidence_confidence == "HIGH"
        and verification_confidence == "HIGH"
        and overall_score >= 80
    ):

        overall_confidence = "HIGH"

    elif (
        evidence_confidence in {
            "HIGH",
            "MEDIUM"
        }
        and verification_confidence in {
            "HIGH",
            "MEDIUM"
        }
        and overall_score >= 50
    ):

        overall_confidence = "MEDIUM"

    else:

        overall_confidence = "LOW"

    # ========================================================
    # ANALYSIS COMPLETENESS
    # ========================================================

    completeness = 0

    # Evidence evaluation
    if evidence_evaluation:

        completeness += 25

    # Verification
    if causal_verification:

        completeness += 25

    # Chain / factors
    if valid_chain:

        completeness += 25

    elif intermediate_factors:

        completeness += 25

    # Causal information
    if causal_information:

        completeness += 25

    if insufficient_evidence:

        # The system correctly refuses to invent a cause.
        completeness = max(
            completeness,
            75
        )

    elif correlation_only:

        completeness = 100

    completeness = min(
        completeness,
        100
    )

    # ========================================================
    # EVALUATION TYPE
    # ========================================================

    if insufficient_evidence:

        evaluation_type = (
            "INSUFFICIENT_EVIDENCE"
        )

    elif correlation_only:

        evaluation_type = (
            "CORRELATION_ONLY"
        )

    else:

        evaluation_type = (
            "CAUSAL_ANALYSIS"
        )

    # ========================================================
    # EVALUATION SUMMARY
    # ========================================================

    if insufficient_evidence:

        summary = (
            "Evidence quality: INSUFFICIENT. "
            "Causal chain quality: INSUFFICIENT. "
            "Causal verification: INSUFFICIENT_EVIDENCE. "
            "Confidence: LOW. "
            f"Analysis completeness: {completeness}%. "
            "The system correctly avoided inventing "
            "an unsupported causal relationship. "
            f"Overall evaluation score: "
            f"{overall_score}/100."
        )

    elif correlation_only:

        summary = (
            f"Evidence quality: {evidence_strength}. "
            "The available evidence supports correlation "
            "but does not confirm direct causation. "
            "No causal chain was treated as confirmed. "
            "Confidence: MEDIUM. "
            f"Analysis completeness: {completeness}%. "
            f"Overall evaluation score: "
            f"{overall_score}/100."
        )

    else:

        summary = (
            f"Evidence quality: {evidence_strength}. "
            f"Causal chain quality: {chain_quality}. "
            f"Causal verification: {verification_status}. "
            f"Confidence: {overall_confidence}. "
            f"Analysis completeness: {completeness}%. "
            f"Overall evaluation score: "
            f"{overall_score}/100."
        )

    # ========================================================
    # RETURN RESULT
    # ========================================================

    return {

        "success": True,

        "overall_score": overall_score,

        "evidence_quality": evidence_strength,

        "causal_chain_quality": chain_quality,

        "causal_verification": verification_status,

        "confidence": overall_confidence,

        "analysis_completeness": completeness,

        "evidence_score": evidence_score,

        "verification_score": verification_score,

        "chain_score": chain_score,

        "chain_length": len(
            valid_chain
        ),

        "intermediate_factor_count": len(
            intermediate_factors
        ),

        "evaluation_type": evaluation_type,

        "evaluation_summary": summary
    }


# ============================================================
# TEST 1 — STRONG MULTI-STEP CAUSAL ANALYSIS
# ============================================================

def test_strong_causal_analysis():

    causal_information = {
        "cause": "Increased database traffic",
        "effect": "System timeout",
        "factors": [
            "Increased user requests",
            "Higher database queries",
            "Higher database load",
            "Increased processing time",
            "Higher system latency"
        ],
        "status": "CAUSALITY_SUPPORTED"
    }

    evidence_evaluation = {
        "strength": "STRONG",
        "confidence": "HIGH",
        "claim_count": 6,
        "causal_claims": 6,
        "correlation_claims": 0,
        "unknown_claims": 0
    }

    causal_verification = {
        "status": "CAUSALITY_SUPPORTED",
        "confidence": "HIGH",
        "verified_claims": 6,
        "unsupported_claims": 0,
        "correlation_claims": 0,
        "unknown_claims": 0
    }

    causal_chain = [
        "Increased user requests",
        "Higher database queries",
        "Higher database load",
        "Increased processing time",
        "Higher system latency",
        "System timeout"
    ]

    return evaluate_analysis(
        causal_information,
        causal_chain,
        evidence_evaluation,
        causal_verification
    )


# ============================================================
# TEST 2 — CORRELATION ONLY
# ============================================================

def test_correlation_analysis():

    causal_information = {
        "status": "CORRELATION_ONLY",
        "cause": "Increased database traffic",
        "effect": "Higher system latency"
    }

    evidence_evaluation = {
        "strength": "MODERATE",
        "confidence": "MEDIUM",
        "claim_count": 1,
        "causal_claims": 0,
        "correlation_claims": 1,
        "unknown_claims": 0,
        "causal_conclusion": "CORRELATION_ONLY"
    }

    causal_verification = {
        "status": "CORRELATION_ONLY",
        "confidence": "MEDIUM",
        "verified_claims": 0,
        "unsupported_claims": 0,
        "correlation_claims": 1,
        "unknown_claims": 0
    }

    causal_chain = []

    return evaluate_analysis(
        causal_information,
        causal_chain,
        evidence_evaluation,
        causal_verification
    )


# ============================================================
# TEST 3 — INSUFFICIENT EVIDENCE
# ============================================================

def test_insufficient_analysis():

    causal_information = {
        "status": "INSUFFICIENT_EVIDENCE"
    }

    evidence_evaluation = {
        "strength": "INSUFFICIENT",
        "confidence": "LOW",
        "claim_count": 1,
        "causal_claims": 0,
        "correlation_claims": 0,
        "unknown_claims": 1
    }

    causal_verification = {
        "status": "INSUFFICIENT_EVIDENCE",
        "confidence": "LOW",
        "verified_claims": 0,
        "unsupported_claims": 0,
        "correlation_claims": 0,
        "unknown_claims": 1
    }

    causal_chain = []

    return evaluate_analysis(
        causal_information,
        causal_chain,
        evidence_evaluation,
        causal_verification
    )


# ============================================================
# TEST 4 — TWO-NODE CAUSE WITH MULTIPLE FACTORS
# ============================================================

def test_two_node_with_factors():

    causal_information = {
        "cause": "Increased database traffic",
        "effect": "System timeout",
        "factors": [
            "Increased user requests",
            "Higher database queries",
            "Higher database load",
            "Increased processing time",
            "Higher system latency"
        ],
        "status": "CAUSALITY_SUPPORTED"
    }

    evidence_evaluation = {
        "strength": "STRONG",
        "confidence": "HIGH",
        "claim_count": 6,
        "causal_claims": 6
    }

    causal_verification = {
        "status": "CAUSALITY_SUPPORTED",
        "confidence": "HIGH",
        "verified_claims": 6
    }

    # Simulates the situation where the analyzer exposes
    # only the endpoints directly in causal_chain.
    causal_chain = [
        "Increased database traffic",
        "System timeout"
    ]

    return evaluate_analysis(
        causal_information,
        causal_chain,
        evidence_evaluation,
        causal_verification
    )


# ============================================================
# TEST RUNNER
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)

    print(
        "CAUSAL ANALYSIS EVALUATOR TEST"
    )

    print("=" * 70)

    # --------------------------------------------------------
    # TEST 1
    # --------------------------------------------------------

    print(
        "\n[TEST 1] STRONG MULTI-STEP CAUSAL ANALYSIS"
    )

    result_1 = (
        test_strong_causal_analysis()
    )

    print(
        "\nOverall Score:",
        result_1[
            "overall_score"
        ]
    )

    print(
        "Evidence Quality:",
        result_1[
            "evidence_quality"
        ]
    )

    print(
        "Chain Quality:",
        result_1[
            "causal_chain_quality"
        ]
    )

    print(
        "Verification:",
        result_1[
            "causal_verification"
        ]
    )

    print(
        "Confidence:",
        result_1[
            "confidence"
        ]
    )

    print(
        "Completeness:",
        str(
            result_1[
                "analysis_completeness"
            ]
        ) + "%"
    )

    # --------------------------------------------------------
    # TEST 2
    # --------------------------------------------------------

    print(
        "\n[TEST 2] CORRELATION ONLY"
    )

    result_2 = (
        test_correlation_analysis()
    )

    print(
        "\nOverall Score:",
        result_2[
            "overall_score"
        ]
    )

    print(
        "Evidence Quality:",
        result_2[
            "evidence_quality"
        ]
    )

    print(
        "Chain Quality:",
        result_2[
            "causal_chain_quality"
        ]
    )

    print(
        "Verification:",
        result_2[
            "causal_verification"
        ]
    )

    print(
        "Confidence:",
        result_2[
            "confidence"
        ]
    )

    print(
        "Completeness:",
        str(
            result_2[
                "analysis_completeness"
            ]
        ) + "%"
    )

    # --------------------------------------------------------
    # TEST 3
    # --------------------------------------------------------

    print(
        "\n[TEST 3] INSUFFICIENT EVIDENCE"
    )

    result_3 = (
        test_insufficient_analysis()
    )

    print(
        "\nOverall Score:",
        result_3[
            "overall_score"
        ]
    )

    print(
        "Evidence Quality:",
        result_3[
            "evidence_quality"
        ]
    )

    print(
        "Chain Quality:",
        result_3[
            "causal_chain_quality"
        ]
    )

    print(
        "Verification:",
        result_3[
            "causal_verification"
        ]
    )

    print(
        "Confidence:",
        result_3[
            "confidence"
        ]
    )

    print(
        "Completeness:",
        str(
            result_3[
                "analysis_completeness"
            ]
        ) + "%"
    )

    # --------------------------------------------------------
    # TEST 4
    # --------------------------------------------------------

    print(
        "\n[TEST 4] TWO-NODE CHAIN WITH MULTIPLE FACTORS"
    )

    result_4 = (
        test_two_node_with_factors()
    )

    print(
        "\nOverall Score:",
        result_4[
            "overall_score"
        ]
    )

    print(
        "Evidence Quality:",
        result_4[
            "evidence_quality"
        ]
    )

    print(
        "Chain Quality:",
        result_4[
            "causal_chain_quality"
        ]
    )

    print(
        "Verification:",
        result_4[
            "causal_verification"
        ]
    )

    print(
        "Confidence:",
        result_4[
            "confidence"
        ]
    )

    print(
        "Completeness:",
        str(
            result_4[
                "analysis_completeness"
            ]
        ) + "%"
    )

    # ========================================================
    # END
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "EVALUATOR TESTS COMPLETED"
    )

    print(
        "=" * 70
    )