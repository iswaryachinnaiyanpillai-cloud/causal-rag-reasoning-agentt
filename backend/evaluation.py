# ============================================================
# EVALUATION AND METRICS MODULE
# Causal RAG Agent - TechNova Solutions
# ============================================================

from statistics import mean


# ============================================================
# SAFE HELPERS
# ============================================================

def safe_dict(value):
    """Return a dictionary or an empty dictionary."""

    return value if isinstance(value, dict) else {}


def safe_list(value):
    """Return a list or an empty list."""

    return value if isinstance(value, list) else []


def normalize_status(value):
    """Normalize status text."""

    return str(
        value or ""
    ).upper().strip()


# ============================================================
# 1. EVALUATE CAUSAL ANALYSIS
# ============================================================

def evaluate_causal_analysis(
    causal_information,
    causal_chain,
    evidence_evaluation,
    causal_verification
):
    """
    Evaluate one causal analysis.

    Consistent scoring model:

        STRONG causal case
            Evidence      = 40
            Verification = 40
            Chain         = 20
            Total         = 100

        CORRELATION_ONLY
            Evidence      = 30
            Verification = 30
            Chain         = 0
            Total         = 60

        INSUFFICIENT_EVIDENCE
            Total         = 0

    The function also reports:
        - confidence
        - completeness
        - claim counts
        - evaluation status
    """

    causal_information = safe_dict(
        causal_information
    )

    causal_chain = safe_list(
        causal_chain
    )

    evidence_evaluation = safe_dict(
        evidence_evaluation
    )

    causal_verification = safe_dict(
        causal_verification
    )

    # ========================================================
    # EVIDENCE QUALITY
    # ========================================================

    evidence_strength = normalize_status(
        evidence_evaluation.get(
            "strength",
            causal_information.get(
                "evidence_strength",
                "INSUFFICIENT"
            )
        )
    )

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

    if evidence_strength == "STRONG":
        evidence_quality = "STRONG"

    elif evidence_strength == "MODERATE":
        evidence_quality = "MODERATE"

    elif evidence_strength == "WEAK":
        evidence_quality = "WEAK"

    else:
        evidence_quality = "INSUFFICIENT"

    # ========================================================
    # VERIFICATION
    # ========================================================

    verification_status = normalize_status(
        causal_verification.get(
            "status",
            "INSUFFICIENT_EVIDENCE"
        )
    )

    verification_scores = {
        "CAUSALITY_SUPPORTED": 40,
        "CAUSALITY_NOT_SUPPORTED": 15,
        "CAUSALITY_NOT_CONFIRMED": 10,
        "CORRELATION_ONLY": 30,
        "INSUFFICIENT_EVIDENCE": 0
    }

    verification_score = verification_scores.get(
        verification_status,
        0
    )

    # ========================================================
    # CAUSAL CHAIN
    # ========================================================

    valid_chain = [
        str(item).strip()
        for item in causal_chain
        if str(item).strip()
    ]

    chain_length = len(
        valid_chain
    )

    if verification_status == "INSUFFICIENT_EVIDENCE":
        chain_quality = "INSUFFICIENT"

    elif verification_status == "CORRELATION_ONLY":
        chain_quality = "NOT_APPLICABLE"

    elif chain_length >= 4:
        chain_quality = "EXCELLENT"

    elif chain_length == 3:
        chain_quality = "GOOD"

    elif chain_length == 2:
        chain_quality = "BASIC"

    elif chain_length == 1:
        chain_quality = "WEAK"

    else:
        chain_quality = "INSUFFICIENT"

    chain_scores = {
        "EXCELLENT": 20,
        "GOOD": 20,
        "BASIC": 15,
        "WEAK": 5,
        "INSUFFICIENT": 0,

        # Important:
        # Correlation-only does not receive causal-chain
        # points because there is no causal chain.
        "NOT_APPLICABLE": 0
    }

    chain_score = chain_scores.get(
        chain_quality,
        0
    )

    # ========================================================
    # OVERALL SCORE
    # ========================================================

    if verification_status == "INSUFFICIENT_EVIDENCE":

        overall_score = 0

    elif verification_status == "CORRELATION_ONLY":

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

    overall_score = max(
        0,
        min(
            overall_score,
            100
        )
    )

    # ========================================================
    # CONFIDENCE
    # ========================================================

    evidence_confidence = normalize_status(
        evidence_evaluation.get(
            "confidence",
            "LOW"
        )
    )

    verification_confidence = normalize_status(
        causal_verification.get(
            "confidence",
            "LOW"
        )
    )

    if verification_status == "INSUFFICIENT_EVIDENCE":

        confidence = "LOW"

    elif verification_status == "CORRELATION_ONLY":

        confidence = "MEDIUM"

    elif (
        evidence_confidence == "HIGH"
        and verification_confidence == "HIGH"
        and overall_score >= 80
    ):

        confidence = "HIGH"

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

        confidence = "MEDIUM"

    else:

        confidence = "LOW"

    # ========================================================
    # ANALYSIS COMPLETENESS
    # ========================================================

    if verification_status == "CORRELATION_ONLY":

        completeness = 100

    elif verification_status == "INSUFFICIENT_EVIDENCE":

        completeness = 75

    else:

        completeness_items = [

            bool(
                causal_information.get(
                    "observation"
                )
            ),

            bool(
                causal_information.get(
                    "cause"
                )
                and causal_information.get(
                    "cause"
                ) != "Unknown"
            ),

            bool(
                causal_information.get(
                    "effect"
                )
                and causal_information.get(
                    "effect"
                ) != "Unknown"
            ),

            bool(
                causal_information.get(
                    "intermediate_factors"
                )
            ),

            bool(
                valid_chain
            ),

            bool(
                causal_information.get(
                    "alternative_causes"
                )
            ),

            bool(
                evidence_evaluation
            ),

            bool(
                causal_verification
            )
        ]

        completed = sum(
            1
            for item in completeness_items
            if item
        )

        total_items = len(
            completeness_items
        )

        completeness = round(
            (
                completed
                / total_items
            ) * 100
        ) if total_items else 0

    # ========================================================
    # EVALUATION STATUS
    # ========================================================

    if verification_status == "INSUFFICIENT_EVIDENCE":

        evaluation_status = "SAFE_REFUSAL"

    elif verification_status == "CORRELATION_ONLY":

        evaluation_status = "CORRELATION_ONLY"

    elif overall_score >= 60:

        evaluation_status = "PASS"

    else:

        evaluation_status = "NEEDS_IMPROVEMENT"

    # ========================================================
    # EVALUATION TYPE
    # ========================================================

    if (
        verification_status
        == "CAUSALITY_SUPPORTED"
    ):

        evaluation_type = "CAUSAL_ANALYSIS"

    elif (
        verification_status
        == "CORRELATION_ONLY"
    ):

        evaluation_type = "CORRELATION_ONLY"

    elif (
        verification_status
        == "INSUFFICIENT_EVIDENCE"
    ):

        evaluation_type = "INSUFFICIENT_EVIDENCE"

    else:

        evaluation_type = "UNCONFIRMED"

    # ========================================================
    # SUMMARY
    # ========================================================

    if verification_status == "CAUSALITY_SUPPORTED":

        conclusion = (
            "The available evidence supports the "
            "identified causal relationship."
        )

    elif verification_status == "CORRELATION_ONLY":

        conclusion = (
            "The available evidence indicates correlation "
            "but does not establish direct causation."
        )

    elif verification_status == "INSUFFICIENT_EVIDENCE":

        conclusion = (
            "The available evidence is insufficient to "
            "determine a reliable causal relationship. "
            "The system correctly avoided inventing a cause."
        )

    else:

        conclusion = (
            "The available evidence does not confirm "
            "direct causation."
        )

    evaluation_summary = (

        f"Evidence quality: {evidence_quality}. "

        f"Causal chain quality: {chain_quality}. "

        f"Causal verification: {verification_status}. "

        f"Confidence: {confidence}. "

        f"Analysis completeness: {completeness}%. "

        f"Overall evaluation score: "
        f"{overall_score}/100. "

        f"{conclusion}"
    )

    # ========================================================
    # RETURN
    # ========================================================

    return {

        "success":
            True,

        "overall_score":
            overall_score,

        "evidence_quality":
            evidence_quality,

        "evidence_score":
            evidence_score,

        "causal_chain_quality":
            chain_quality,

        "causal_chain_score":
            chain_score,

        "causal_verification":
            verification_status,

        "verification_score":
            verification_score,

        "confidence":
            confidence,

        "analysis_completeness":
            completeness,

        "chain_length":
            chain_length,

        "claim_count":
            evidence_evaluation.get(
                "claim_count",
                0
            ),

        "causal_claims":
            evidence_evaluation.get(
                "causal_claims",
                0
            ),

        "correlation_claims":
            evidence_evaluation.get(
                "correlation_claims",
                0
            ),

        "unknown_claims":
            evidence_evaluation.get(
                "unknown_claims",
                0
            ),

        "evaluation_status":
            evaluation_status,

        "evaluation_type":
            evaluation_type,

        "evaluation_summary":
            evaluation_summary
    }


# ============================================================
# 2. CREATE EVALUATION SUMMARY
# ============================================================

def create_evaluation_summary(
    evaluation
):
    """
    Create a concise human-readable evaluation summary.
    """

    if not isinstance(
        evaluation,
        dict
    ):

        return (
            "Evaluation could not be completed."
        )

    evidence_quality = evaluation.get(
        "evidence_quality",
        "INSUFFICIENT"
    )

    confidence = evaluation.get(
        "confidence",
        "LOW"
    )

    causal_status = evaluation.get(
        "causal_verification",
        "INSUFFICIENT_EVIDENCE"
    )

    completeness = evaluation.get(
        "analysis_completeness",
        0
    )

    score = evaluation.get(
        "overall_score",
        0
    )

    if causal_status == "CAUSALITY_SUPPORTED":

        conclusion = (
            "The available evidence supports "
            "the identified causal relationship."
        )

    elif causal_status == "CORRELATION_ONLY":

        conclusion = (
            "The evidence supports correlation only; "
            "direct causation was not established."
        )

    elif causal_status == "INSUFFICIENT_EVIDENCE":

        conclusion = (
            "The evidence is insufficient to establish "
            "a reliable causal relationship."
        )

    else:

        conclusion = (
            "The available evidence does not confirm "
            "direct causation."
        )

    return (

        f"Evidence strength: {evidence_quality}. "

        f"Confidence level: {confidence}. "

        f"Causal status: {causal_status}. "

        f"Analysis completeness: {completeness}%. "

        f"Overall evaluation score: {score}/100. "

        f"{conclusion}"
    )


# ============================================================
# 3. EVALUATE DATASET RESULTS
# ============================================================

def evaluate_dataset_results(
    results
):
    """
    Aggregate evaluation metrics across multiple scenarios.
    """

    if not isinstance(
        results,
        list
    ):

        return {

            "success":
                False,

            "total_tests":
                0,

            "message":
                "Results must be a list."
        }

    total_tests = len(
        results
    )

    passed_tests = 0
    failed_tests = 0

    status_matches = 0
    evidence_matches = 0

    causal_supported = 0
    correlation_only = 0
    insufficient_evidence = 0

    scores = []

    for result in results:

        if not isinstance(
            result,
            dict
        ):
            continue

        expected_status = normalize_status(
            result.get(
                "expected_status"
            )
        )

        actual_status = normalize_status(
            result.get(
                "actual_status",
                (
                    result.get(
                        "causal_verification",
                        {}
                    ).get(
                        "status"
                    )
                    if isinstance(
                        result.get(
                            "causal_verification"
                        ),
                        dict
                    )
                    else ""
                )
            )
        )

        expected_evidence = normalize_status(
            result.get(
                "expected_evidence"
            )
        )

        actual_evidence = normalize_status(
            result.get(
                "actual_evidence",
                (
                    result.get(
                        "evidence_evaluation",
                        {}
                    ).get(
                        "strength"
                    )
                    if isinstance(
                        result.get(
                            "evidence_evaluation"
                        ),
                        dict
                    )
                    else ""
                )
            )
        )

        status_ok = (
            not expected_status
            or expected_status == actual_status
        )

        evidence_ok = (
            not expected_evidence
            or expected_evidence == actual_evidence
        )

        if status_ok and evidence_ok:

            passed_tests += 1

        else:

            failed_tests += 1

        if (
            expected_status
            and expected_status
            == actual_status
        ):

            status_matches += 1

        if (
            expected_evidence
            and expected_evidence
            == actual_evidence
        ):

            evidence_matches += 1

        if expected_status == "CAUSALITY_SUPPORTED":

            causal_supported += 1

        elif expected_status == "CORRELATION_ONLY":

            correlation_only += 1

        elif expected_status == "INSUFFICIENT_EVIDENCE":

            insufficient_evidence += 1

        evaluation = result.get(
            "evaluation",
            {}
        )

        if isinstance(
            evaluation,
            dict
        ):

            score = evaluation.get(
                "overall_score"
            )

            if isinstance(
                score,
                (int, float)
            ):

                scores.append(
                    float(score)
                )

    if total_tests > 0:

        pass_rate = round(
            (
                passed_tests
                / total_tests
            ) * 100,
            2
        )

        status_accuracy = round(
            (
                status_matches
                / total_tests
            ) * 100,
            2
        )

        evidence_accuracy = round(
            (
                evidence_matches
                / total_tests
            ) * 100,
            2
        )

    else:

        pass_rate = 0.0
        status_accuracy = 0.0
        evidence_accuracy = 0.0

    if scores:

        average_score = round(
            mean(scores),
            2
        )

    else:

        average_score = None

    return {

        "success":
            True,

        "total_tests":
            total_tests,

        "passed_tests":
            passed_tests,

        "failed_tests":
            failed_tests,

        "pass_rate":
            pass_rate,

        "status_accuracy":
            status_accuracy,

        "evidence_accuracy":
            evidence_accuracy,

        "average_causal_score":
            average_score,

        "causality_supported":
            causal_supported,

        "correlation_only":
            correlation_only,

        "insufficient_evidence":
            insufficient_evidence,

        "metrics": {

            "causal_status_accuracy":
                status_accuracy,

            "evidence_strength_accuracy":
                evidence_accuracy,

            "answer_pass_rate":
                pass_rate,

            "average_causal_score":
                average_score
        }
    }


# ============================================================
# 4. BUILD PROJECT METRICS
# ============================================================

def build_project_metrics(
    results
):
    """
    Build project-level evaluation metrics.

    Metrics:
        - Causal relationship accuracy
        - Evidence strength accuracy
        - Evidence faithfulness
        - Causal hallucination rate
        - Alternative cause coverage
        - Chain quality
    """

    if not isinstance(
        results,
        list
    ):

        return {

            "success":
                False,

            "error":
                "Results must be a list."
        }

    total = len(
        results
    )

    if total == 0:

        return {

            "success":
                False,

            "error":
                "No evaluation results available."
        }

    status_correct = 0
    evidence_correct = 0

    unsupported_cause_count = 0

    chain_scores = []
    faithfulness_scores = []

    # --------------------------------------------------------
    # Alternative-cause metrics
    #
    # Only causal cases where alternative causes are
    # meaningful are included in the denominator.
    # --------------------------------------------------------

    alternative_applicable = 0
    alternative_available = 0

    for result in results:

        if not isinstance(
            result,
            dict
        ):
            continue

        expected_status = normalize_status(
            result.get(
                "expected_status"
            )
        )

        actual_status = normalize_status(
            result.get(
                "actual_status"
            )
        )

        expected_evidence = normalize_status(
            result.get(
                "expected_evidence"
            )
        )

        actual_evidence = normalize_status(
            result.get(
                "actual_evidence"
            )
        )

        # ----------------------------------------------------
        # Status accuracy
        # ----------------------------------------------------

        if (
            expected_status
            and actual_status
            and expected_status
            == actual_status
        ):

            status_correct += 1

        # ----------------------------------------------------
        # Evidence accuracy
        # ----------------------------------------------------

        if (
            expected_evidence
            and actual_evidence
            and expected_evidence
            == actual_evidence
        ):

            evidence_correct += 1

        # ----------------------------------------------------
        # Causal hallucination
        # ----------------------------------------------------

        if (
            expected_status
            in {
                "CORRELATION_ONLY",
                "INSUFFICIENT_EVIDENCE"
            }

            and actual_status
            == "CAUSALITY_SUPPORTED"
        ):

            unsupported_cause_count += 1

        # ----------------------------------------------------
        # Alternative cause coverage
        # ----------------------------------------------------

        if (
            expected_status
            == "CAUSALITY_SUPPORTED"
        ):

            causal_information = result.get(
                "causal_information",
                {}
            )

            if isinstance(
                causal_information,
                dict
            ):

                alternatives = (
                    causal_information.get(
                        "alternative_causes",
                        []
                    )
                )

                # Count only cases where the result actually
                # defines an alternative-cause analysis.
                if (
                    "alternative_causes"
                    in causal_information
                ):

                    alternative_applicable += 1

                    if alternatives:

                        alternative_available += 1

        # ----------------------------------------------------
        # Chain quality
        # ----------------------------------------------------

        evaluation = result.get(
            "evaluation",
            {}
        )

        if isinstance(
            evaluation,
            dict
        ):

            chain_quality = normalize_status(
                evaluation.get(
                    "causal_chain_quality"
                )
            )

            chain_value = {

                "EXCELLENT":
                    100,

                "GOOD":
                    80,

                "BASIC":
                    60,

                "WEAK":
                    40,

                "NOT_APPLICABLE":
                    None,

                "INSUFFICIENT":
                    0
            }.get(
                chain_quality
            )

            if chain_value is not None:

                chain_scores.append(
                    chain_value
                )

        # ----------------------------------------------------
        # Evidence faithfulness
        # ----------------------------------------------------

        retrieved_evidence = result.get(
            "retrieved_evidence",
            ""
        )

        if (
            isinstance(
                retrieved_evidence,
                str
            )

            and retrieved_evidence.strip()

            and actual_status
            in {
                "CAUSALITY_SUPPORTED",
                "CORRELATION_ONLY",
                "INSUFFICIENT_EVIDENCE"
            }
        ):

            faithfulness_scores.append(
                100
            )

        else:

            faithfulness_scores.append(
                0
            )

    # ========================================================
    # FINAL METRICS
    # ========================================================

    causal_relationship_accuracy = round(
        (
            status_correct
            / total
        ) * 100,
        2
    )

    evidence_strength_accuracy = round(
        (
            evidence_correct
            / total
        ) * 100,
        2
    )

    causal_hallucination_rate = round(
        (
            unsupported_cause_count
            / total
        ) * 100,
        2
    )

    causal_hallucination_free_rate = round(
        100
        - causal_hallucination_rate,
        2
    )

    if chain_scores:

        average_chain_quality = round(
            mean(chain_scores),
            2
        )

    else:

        average_chain_quality = None

    if faithfulness_scores:

        evidence_faithfulness = round(
            mean(
                faithfulness_scores
            ),
            2
        )

    else:

        evidence_faithfulness = None

    if alternative_applicable > 0:

        alternative_cause_coverage = round(
            (
                alternative_available
                / alternative_applicable
            ) * 100,
            2
        )

    else:

        alternative_cause_coverage = None

    return {

        "success":
            True,

        "total_cases":
            total,

        "causal_relationship_accuracy":
            causal_relationship_accuracy,

        "evidence_strength_accuracy":
            evidence_strength_accuracy,

        "average_chain_quality":
            average_chain_quality,

        "evidence_faithfulness":
            evidence_faithfulness,

        "causal_hallucination_rate":
            causal_hallucination_rate,

        "causal_hallucination_free_rate":
            causal_hallucination_free_rate,

        "alternative_cause_coverage":
            alternative_cause_coverage,

        "causal_supported_cases":
            sum(
                1
                for result
                in results
                if normalize_status(
                    result.get(
                        "actual_status"
                    )
                )
                == "CAUSALITY_SUPPORTED"
            ),

        "metrics": {

            "causal_relationship_accuracy":
                causal_relationship_accuracy,

            "evidence_strength_accuracy":
                evidence_strength_accuracy,

            "chain_quality":
                average_chain_quality,

            "evidence_faithfulness":
                evidence_faithfulness,

            "causal_hallucination_rate":
                causal_hallucination_rate,

            "alternative_cause_accuracy":
                alternative_cause_coverage
        }
    }


# ============================================================
# 5. CREATE FINAL PROJECT REPORT
# ============================================================

def create_project_evaluation_report(
    results
):
    """
    Create a complete submission-friendly evaluation report.
    """

    dataset_evaluation = (
        evaluate_dataset_results(
            results
        )
    )

    project_metrics = (
        build_project_metrics(
            results
        )
    )

    return {

        "success":
            True,

        "dataset_evaluation":
            dataset_evaluation,

        "project_metrics":
            project_metrics,

        "summary": {

            "total_cases":
                dataset_evaluation.get(
                    "total_tests",
                    0
                ),

            "passed_cases":
                dataset_evaluation.get(
                    "passed_tests",
                    0
                ),

            "failed_cases":
                dataset_evaluation.get(
                    "failed_tests",
                    0
                ),

            "pass_rate":
                dataset_evaluation.get(
                    "pass_rate",
                    0
                ),

            "causal_relationship_accuracy":
                project_metrics.get(
                    "causal_relationship_accuracy"
                ),

            "evidence_strength_accuracy":
                project_metrics.get(
                    "evidence_strength_accuracy"
                ),

            "evidence_faithfulness":
                project_metrics.get(
                    "evidence_faithfulness"
                ),

            "causal_hallucination_rate":
                project_metrics.get(
                    "causal_hallucination_rate"
                ),

            "alternative_cause_coverage":
                project_metrics.get(
                    "alternative_cause_coverage"
                ),

            "average_chain_quality":
                project_metrics.get(
                    "average_chain_quality"
                )
        }
    }


# ============================================================
# 6. TEST MODULE
# ============================================================

if __name__ == "__main__":

    print(
        "\n" + "=" * 75
    )

    print(
        "EVALUATION AND METRICS MODULE"
    )

    print(
        "CAUSAL RAG AGENT - TECHNOVA SOLUTIONS"
    )

    print(
        "=" * 75
    )

    # ========================================================
    # TEST 1 — STRONG CAUSAL
    # ========================================================

    causal_information = {

        "observation":
            "Average system latency increased.",

        "cause":
            "Increased database traffic.",

        "intermediate_factors": [

            "Higher database load.",

            "Increased processing time."
        ],

        "effect":
            "Higher system latency.",

        "evidence_strength":
            "STRONG",

        "alternative_causes": [

            "Reduced server resources."
        ]
    }

    causal_chain = [

        "Increased user requests",

        "Higher database queries",

        "Higher database load",

        "Increased processing time",

        "Higher system latency",

        "System timeout"
    ]

    evidence_evaluation = {

        "strength":
            "STRONG",

        "confidence":
            "HIGH",

        "claim_count":
            5,

        "causal_claims":
            3,

        "correlation_claims":
            0,

        "unknown_claims":
            2
    }

    causal_verification = {

        "status":
            "CAUSALITY_SUPPORTED",

        "confidence":
            "HIGH"
    }

    strong_result = evaluate_causal_analysis(

        causal_information,

        causal_chain,

        evidence_evaluation,

        causal_verification
    )

    print(
        "\n[TEST 1] STRONG CAUSAL ANALYSIS"
    )

    print(
        "Overall Score:",
        strong_result[
            "overall_score"
        ]
    )

    print(
        "Evidence Quality:",
        strong_result[
            "evidence_quality"
        ]
    )

    print(
        "Chain Quality:",
        strong_result[
            "causal_chain_quality"
        ]
    )

    print(
        "Verification:",
        strong_result[
            "causal_verification"
        ]
    )

    print(
        "Confidence:",
        strong_result[
            "confidence"
        ]
    )

    print(
        "Completeness:",
        str(
            strong_result[
                "analysis_completeness"
            ]
        ) + "%"
    )

    print(
        "Status:",
        strong_result[
            "evaluation_status"
        ]
    )

    # ========================================================
    # TEST 2 — CORRELATION ONLY
    # ========================================================

    correlation_result = (
        evaluate_causal_analysis(

            {
                "cause":
                    "Unknown",

                "effect":
                    "Unknown",

                "evidence_strength":
                    "MODERATE"
            },

            [],

            {
                "strength":
                    "MODERATE",

                "confidence":
                    "MEDIUM",

                "claim_count":
                    1,

                "causal_claims":
                    0,

                "correlation_claims":
                    1,

                "unknown_claims":
                    0
            },

            {
                "status":
                    "CORRELATION_ONLY",

                "confidence":
                    "MEDIUM"
            }
        )
    )

    print(
        "\n[TEST 2] CORRELATION ONLY"
    )

    print(
        "Overall Score:",
        correlation_result[
            "overall_score"
        ]
    )

    print(
        "Evidence Quality:",
        correlation_result[
            "evidence_quality"
        ]
    )

    print(
        "Chain Quality:",
        correlation_result[
            "causal_chain_quality"
        ]
    )

    print(
        "Verification:",
        correlation_result[
            "causal_verification"
        ]
    )

    print(
        "Confidence:",
        correlation_result[
            "confidence"
        ]
    )

    print(
        "Completeness:",
        str(
            correlation_result[
                "analysis_completeness"
            ]
        ) + "%"
    )

    # ========================================================
    # TEST 3 — INSUFFICIENT EVIDENCE
    # ========================================================

    insufficient_result = (
        evaluate_causal_analysis(

            {

                "cause":
                    "Unknown",

                "effect":
                    "Unknown",

                "evidence_strength":
                    "INSUFFICIENT"
            },

            [],

            {

                "strength":
                    "INSUFFICIENT",

                "confidence":
                    "LOW",

                "claim_count":
                    1,

                "causal_claims":
                    0,

                "correlation_claims":
                    0,

                "unknown_claims":
                    1
            },

            {

                "status":
                    "INSUFFICIENT_EVIDENCE",

                "confidence":
                    "LOW"
            }
        )
    )

    print(
        "\n[TEST 3] INSUFFICIENT EVIDENCE"
    )

    print(
        "Overall Score:",
        insufficient_result[
            "overall_score"
        ]
    )

    print(
        "Evidence Quality:",
        insufficient_result[
            "evidence_quality"
        ]
    )

    print(
        "Chain Quality:",
        insufficient_result[
            "causal_chain_quality"
        ]
    )

    print(
        "Verification:",
        insufficient_result[
            "causal_verification"
        ]
    )

    print(
        "Confidence:",
        insufficient_result[
            "confidence"
        ]
    )

    print(
        "Completeness:",
        str(
            insufficient_result[
                "analysis_completeness"
            ]
        ) + "%"
    )

    print(
        "Status:",
        insufficient_result[
            "evaluation_status"
        ]
    )

    # ========================================================
    # DEMO DATASET
    # ========================================================

    demo_results = [

        {

            "expected_status":
                "CAUSALITY_SUPPORTED",

            "actual_status":
                "CAUSALITY_SUPPORTED",

            "expected_evidence":
                "STRONG",

            "actual_evidence":
                "STRONG",

            "evaluation":
                strong_result,

            "causal_information":
                causal_information,

            "retrieved_evidence":
                "Evidence supports the causal relationship."
        },

        {

            "expected_status":
                "CORRELATION_ONLY",

            "actual_status":
                "CORRELATION_ONLY",

            "expected_evidence":
                "MODERATE",

            "actual_evidence":
                "MODERATE",

            "evaluation":
                correlation_result,

            "causal_information":
                {
                    "alternative_causes": []
                },

            "retrieved_evidence":
                "The observed variables are correlated."
        },

        {

            "expected_status":
                "INSUFFICIENT_EVIDENCE",

            "actual_status":
                "INSUFFICIENT_EVIDENCE",

            "expected_evidence":
                "INSUFFICIENT",

            "actual_evidence":
                "INSUFFICIENT",

            "evaluation":
                insufficient_result,

            "causal_information":
                {
                    "alternative_causes": []
                },

            "retrieved_evidence":
                "No evidence identifies a specific cause."
        }
    ]

    # ========================================================
    # DATASET EVALUATION
    # ========================================================

    dataset_metrics = (
        evaluate_dataset_results(
            demo_results
        )
    )

    print(
        "\n[DATASET EVALUATION]"
    )

    print(
        "Total Tests:",
        dataset_metrics[
            "total_tests"
        ]
    )

    print(
        "Passed:",
        dataset_metrics[
            "passed_tests"
        ]
    )

    print(
        "Failed:",
        dataset_metrics[
            "failed_tests"
        ]
    )

    print(
        "Pass Rate:",
        str(
            dataset_metrics[
                "pass_rate"
            ]
        ) + "%"
    )

    print(
        "Status Accuracy:",
        str(
            dataset_metrics[
                "status_accuracy"
            ]
        ) + "%"
    )

    print(
        "Evidence Accuracy:",
        str(
            dataset_metrics[
                "evidence_accuracy"
            ]
        ) + "%"
    )

    # ========================================================
    # PROJECT METRICS
    # ========================================================

    project_metrics = build_project_metrics(
        demo_results
    )

    print(
        "\n[PROJECT METRICS]"
    )

    print(
        "Causal Relationship Accuracy:",
        str(
            project_metrics[
                "causal_relationship_accuracy"
            ]
        ) + "%"
    )

    print(
        "Evidence Strength Accuracy:",
        str(
            project_metrics[
                "evidence_strength_accuracy"
            ]
        ) + "%"
    )

    print(
        "Evidence Faithfulness:",
        str(
            project_metrics[
                "evidence_faithfulness"
            ]
        ) + "%"
    )

    print(
        "Causal Hallucination Rate:",
        str(
            project_metrics[
                "causal_hallucination_rate"
            ]
        ) + "%"
    )

    alternative_coverage = project_metrics.get(
        "alternative_cause_coverage"
    )

    if alternative_coverage is None:

        print(
            "Alternative Cause Coverage:",
            "N/A"
        )

    else:

        print(
            "Alternative Cause Coverage:",
            str(
                alternative_coverage
            ) + "%"
        )

    print(
        "\n" + "=" * 75
    )

    print(
        "EVALUATION MODULE TEST COMPLETED"
    )

    print(
        "=" * 75
    )