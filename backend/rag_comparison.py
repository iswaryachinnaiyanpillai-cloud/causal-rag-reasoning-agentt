# ============================================================
# STANDARD RAG vs CAUSAL RAG COMPARISON
# Causal RAG Agent - TechNova Solutions
# ============================================================

import time

from backend.standard_rag import standard_rag_answer
from backend.causal_analyzer import analyze_query


# ============================================================
# SAFE NUMERIC CONVERSION
# ============================================================

def safe_number(value, default=0.0):
    """
    Convert a value into a float safely.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


# ============================================================
# SAFE DICTIONARY
# ============================================================

def safe_dict(value):
    """
    Return a dictionary safely.
    """
    return value if isinstance(value, dict) else {}


# ============================================================
# RUN STANDARD RAG
# ============================================================

def run_standard_rag(question: str):
    """
    Run the Standard RAG baseline.

    Standard RAG retrieves relevant information and generates
    an answer without explicit causal reasoning.
    """

    start_time = time.perf_counter()

    try:
        result = standard_rag_answer(question)

    except Exception as exc:
        result = {
            "success": False,
            "answer": "Standard RAG execution failed.",
            "retrieved_evidence": "",
            "error": str(exc),
        }

    end_time = time.perf_counter()

    response_time_ms = round(
        (end_time - start_time) * 1000,
        2,
    )

    if not isinstance(result, dict):
        result = {
            "success": False,
            "answer": "No Standard RAG result available.",
            "retrieved_evidence": "",
        }

    return {
        "success": result.get(
            "success",
            False,
        ),
        "answer": result.get(
            "answer",
            "",
        ),
        "retrieved_evidence": result.get(
            "retrieved_evidence",
            "",
        ),
        "response_time_ms": response_time_ms,
        "error": result.get(
            "error",
            "",
        ),
    }


# ============================================================
# RUN CAUSAL RAG
# ============================================================

def run_causal_rag(question: str):
    """
    Run the complete Causal RAG pipeline.
    """

    start_time = time.perf_counter()

    try:
        analysis = analyze_query(question)

    except Exception as exc:
        analysis = {
            "success": False,
            "answer": "Causal RAG execution failed.",
            "error": str(exc),
        }

    end_time = time.perf_counter()

    response_time_ms = round(
        (end_time - start_time) * 1000,
        2,
    )

    if not isinstance(analysis, dict):
        analysis = {}

    # --------------------------------------------------------
    # IMPORTANT:
    # causal_analyzer.py uses "overall_evaluation".
    # Older code may use "evaluation".
    # Support both safely.
    # --------------------------------------------------------

    overall_evaluation = analysis.get(
        "overall_evaluation",
        analysis.get(
            "evaluation",
            {},
        ),
    )

    if not isinstance(
        overall_evaluation,
        dict,
    ):
        overall_evaluation = {}

    return {
        "success": analysis.get(
            "success",
            False,
        ),

        "answer": analysis.get(
            "answer",
            "",
        ),

        "retrieved_evidence": analysis.get(
            "retrieved_evidence",
            "",
        ),

        "query_type": analysis.get(
            "query_type",
            "CAUSAL",
        ),

        "causal_information": analysis.get(
            "causal_information",
            {},
        ),

        "claims": analysis.get(
            "claims",
            [],
        ),

        "cause_effect_relationships": analysis.get(
            "cause_effect_relationships",
            [],
        ),

        "causal_chain": analysis.get(
            "causal_chain",
            [],
        ),

        "causal_chain_module": analysis.get(
            "causal_chain_module",
            {},
        ),

        "causal_graph": analysis.get(
            "causal_graph",
            {
                "nodes": [],
                "edges": [],
            },
        ),

        "evidence_evaluation": analysis.get(
            "evidence_evaluation",
            {},
        ),

        "causal_verification": analysis.get(
            "causal_verification",
            {},
        ),

        "causal_reasoning": analysis.get(
            "causal_reasoning",
            {},
        ),

        "reasoning_summary": analysis.get(
            "reasoning_summary",
            "",
        ),

        "overall_evaluation": overall_evaluation,

        # Compatibility alias
        "evaluation": overall_evaluation,

        "response_time_ms": response_time_ms,

        "error": analysis.get(
            "error",
            "",
        ),
    }


# ============================================================
# EXTRACT STANDARD RAG METRICS
# ============================================================

def get_standard_metrics(
    standard_result,
):
    """
    Extract measurable Standard RAG metrics.
    """

    answer = str(
        standard_result.get(
            "answer",
            "",
        )
    )

    evidence = str(
        standard_result.get(
            "retrieved_evidence",
            "",
        )
    )

    return {
        "retrieval_used": bool(
            evidence.strip()
        ),

        "answer_generated": bool(
            answer.strip()
        ),

        "causal_reasoning": False,

        "causal_chain": False,

        "cause_effect_extraction": False,

        "evidence_evaluation": False,

        "causal_verification": False,

        "causal_graph": False,

        "alternative_cause_analysis": False,

        "overall_evaluation": False,

        "response_time_ms": safe_number(
            standard_result.get(
                "response_time_ms",
                0,
            )
        ),
    }


# ============================================================
# EXTRACT CAUSAL RAG METRICS
# ============================================================

def get_causal_metrics(
    causal_result,
):
    """
    Extract measurable Causal RAG metrics.

    This function correctly reads:
        overall_evaluation
        evidence_evaluation
        causal_verification
        causal_information
        causal_chain
        cause_effect_relationships
        causal_graph
    """

    evidence = str(
        causal_result.get(
            "retrieved_evidence",
            "",
        )
    )

    causal_information = safe_dict(
        causal_result.get(
            "causal_information",
            {},
        )
    )

    relationships = causal_result.get(
        "cause_effect_relationships",
        [],
    )

    if not isinstance(
        relationships,
        list,
    ):
        relationships = []

    chain = causal_result.get(
        "causal_chain",
        [],
    )

    if not isinstance(
        chain,
        list,
    ):
        chain = []

    graph = safe_dict(
        causal_result.get(
            "causal_graph",
            {},
        )
    )

    evidence_evaluation = safe_dict(
        causal_result.get(
            "evidence_evaluation",
            {},
        )
    )

    causal_verification = safe_dict(
        causal_result.get(
            "causal_verification",
            {},
        )
    )

    # --------------------------------------------------------
    # IMPORTANT FIX:
    # causal_analyzer returns "overall_evaluation".
    # --------------------------------------------------------

    evaluation = safe_dict(
        causal_result.get(
            "overall_evaluation",
            causal_result.get(
                "evaluation",
                {},
            ),
        )
    )

    # --------------------------------------------------------
    # Alternative causes
    # --------------------------------------------------------

    alternatives = causal_information.get(
        "alternatives",
        [],
    )

    if not isinstance(
        alternatives,
        list,
    ):
        alternatives = []

    # --------------------------------------------------------
    # Score
    # --------------------------------------------------------

    overall_score = evaluation.get(
        "overall_score",
        None,
    )

    # Sometimes score can arrive as a numeric string.
    if isinstance(
        overall_score,
        str,
    ):
        try:
            overall_score = float(
                overall_score
            )
        except ValueError:
            overall_score = None

    # Convert 100.0 -> 100 for clean reporting.
    if isinstance(
        overall_score,
        float,
    ) and overall_score.is_integer():

        overall_score = int(
            overall_score
        )

    # --------------------------------------------------------
    # Evidence quality
    # --------------------------------------------------------

    evidence_quality = evaluation.get(
        "evidence_quality",
        evidence_evaluation.get(
            "evidence_strength",
            evidence_evaluation.get(
                "strength",
                causal_information.get(
                    "evidence_strength",
                    "UNKNOWN",
                ),
            ),
        ),
    )

    # --------------------------------------------------------
    # Chain quality
    # --------------------------------------------------------

    chain_quality = evaluation.get(
        "causal_chain_quality",
        evaluation.get(
            "chain_quality",
            (
                "EXCELLENT"
                if len(chain) >= 3
                else (
                    "GOOD"
                    if len(chain) > 0
                    else "NOT_APPLICABLE"
                )
            ),
        ),
    )

    # --------------------------------------------------------
    # Verification
    # --------------------------------------------------------

    verification_status = causal_verification.get(
        "status",
        causal_verification.get(
            "verification_status",
            evaluation.get(
                "causal_verification",
                causal_information.get(
                    "status",
                    "UNKNOWN",
                ),
            ),
        ),
    )

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    confidence = evaluation.get(
        "confidence",
        causal_verification.get(
            "confidence",
            evidence_evaluation.get(
                "confidence",
                causal_information.get(
                    "confidence",
                    "UNKNOWN",
                ),
            ),
        ),
    )

    # --------------------------------------------------------
    # Completeness
    # --------------------------------------------------------

    analysis_completeness = evaluation.get(
        "analysis_completeness",
        evaluation.get(
            "completeness",
            None,
        ),
    )

    # Deterministic fallback
    if analysis_completeness is None:

        status = causal_information.get(
            "status",
            "",
        )

        if status == "CAUSALITY_SUPPORTED":

            analysis_completeness = 100

        elif status == "CORRELATION_ONLY":

            analysis_completeness = 100

        elif status == "INSUFFICIENT_EVIDENCE":

            analysis_completeness = 75

    # --------------------------------------------------------
    # Feature detection
    # --------------------------------------------------------

    causal_reasoning_used = bool(
        causal_information
    )

    chain_used = bool(
        chain
    )

    cause_effect_used = bool(
        relationships
    )

    evidence_evaluation_used = bool(
        evidence_evaluation
    )

    causal_verification_used = bool(
        causal_verification
    )

    graph_nodes = graph.get(
        "nodes",
        [],
    )

    graph_used = bool(
        graph_nodes
    )

    alternative_cause_used = bool(
        alternatives
    )

    overall_evaluation_used = bool(
        evaluation
    )

    return {
        "retrieval_used": bool(
            evidence.strip()
        ),

        "answer_generated": bool(
            str(
                causal_result.get(
                    "answer",
                    "",
                )
            ).strip()
        ),

        "causal_reasoning": causal_reasoning_used,

        "causal_chain": chain_used,

        "cause_effect_extraction": cause_effect_used,

        "evidence_evaluation": evidence_evaluation_used,

        "causal_verification": causal_verification_used,

        "causal_graph": graph_used,

        "alternative_cause_analysis": alternative_cause_used,

        "overall_evaluation": overall_evaluation_used,

        "response_time_ms": safe_number(
            causal_result.get(
                "response_time_ms",
                0,
            )
        ),

        # ----------------------------------------------------
        # Quality metrics
        # ----------------------------------------------------

        "overall_score": overall_score,

        "evidence_quality": evidence_quality,

        "chain_quality": chain_quality,

        "verification_status": verification_status,

        "confidence": confidence,

        "analysis_completeness": analysis_completeness,

        # ----------------------------------------------------
        # Evidence counts
        # ----------------------------------------------------

        "claim_count": evidence_evaluation.get(
            "claim_count",
            len(
                causal_result.get(
                    "claims",
                    [],
                )
                if isinstance(
                    causal_result.get(
                        "claims",
                        [],
                    ),
                    list,
                )
                else []
            ),
        ),

        "causal_claim_count": evidence_evaluation.get(
            "causal_claims",
            0,
        ),

        "correlation_claim_count": evidence_evaluation.get(
            "correlation_claims",
            0,
        ),

        "alternative_cause_count": len(
            alternatives
        ),

        "causal_chain_length": len(
            chain
        ),

        "cause_effect_relationship_count": len(
            relationships
        ),

        "graph_node_count": len(
            graph_nodes
            if isinstance(
                graph_nodes,
                list,
            )
            else []
        ),

        "graph_edge_count": len(
            graph.get(
                "edges",
                []
            )
            if isinstance(
                graph.get(
                    "edges",
                    [],
                ),
                list,
            )
            else []
        ),
    }


# ============================================================
# FEATURE COMPARISON
# ============================================================

def compare_features(
    standard_metrics,
    causal_metrics,
):
    """
    Compare capabilities of Standard RAG and Causal RAG.
    """

    feature_names = {
        "retrieval_used":
            "Evidence Retrieval",

        "answer_generated":
            "Answer Generation",

        "causal_reasoning":
            "Causal Reasoning",

        "cause_effect_extraction":
            "Cause-Effect Extraction",

        "causal_chain":
            "Causal Chain Construction",

        "evidence_evaluation":
            "Evidence Evaluation",

        "causal_verification":
            "Causal Verification",

        "causal_graph":
            "Causal Graph",

        "alternative_cause_analysis":
            "Alternative Cause Analysis",

        "overall_evaluation":
            "Overall Evaluation",
    }

    comparison = []

    for key, label in feature_names.items():

        standard_value = bool(
            standard_metrics.get(
                key,
                False,
            )
        )

        causal_value = bool(
            causal_metrics.get(
                key,
                False,
            )
        )

        comparison.append(
            {
                "feature": label,
                "standard_rag": standard_value,
                "causal_rag": causal_value,
            }
        )

    return comparison


# ============================================================
# RESPONSE TIME COMPARISON
# ============================================================

def compare_response_time(
    standard_metrics,
    causal_metrics,
):
    """
    Calculate response-time difference.
    """

    standard_time = safe_number(
        standard_metrics.get(
            "response_time_ms",
            0,
        )
    )

    causal_time = safe_number(
        causal_metrics.get(
            "response_time_ms",
            0,
        )
    )

    difference = round(
        causal_time - standard_time,
        2,
    )

    if standard_time > 0:

        overhead_percentage = round(
            (
                difference
                / standard_time
            )
            * 100,
            2,
        )

    else:

        overhead_percentage = 0.0

    if difference > 0:

        interpretation = (
            "Causal RAG requires additional processing "
            "because it performs explicit causal analysis."
        )

    elif difference < 0:

        interpretation = (
            "Causal RAG completed faster for this run; "
            "runtime can vary depending on retrieval and "
            "system conditions."
        )

    else:

        interpretation = (
            "Both systems had approximately the same "
            "response time for this run."
        )

    return {
        "standard_rag_ms": standard_time,
        "causal_rag_ms": causal_time,
        "additional_time_ms": difference,
        "overhead_percentage": overhead_percentage,
        "interpretation": interpretation,
    }


# ============================================================
# CAUSAL QUALITY SUMMARY
# ============================================================

def build_causal_quality_summary(
    causal_metrics,
):
    """
    Build a compact quality summary for Causal RAG.
    """

    return {
        "overall_score":
            causal_metrics.get(
                "overall_score",
                None,
            ),

        "evidence_quality":
            causal_metrics.get(
                "evidence_quality",
                "UNKNOWN",
            ),

        "chain_quality":
            causal_metrics.get(
                "chain_quality",
                "NOT_APPLICABLE",
            ),

        "verification_status":
            causal_metrics.get(
                "verification_status",
                "UNKNOWN",
            ),

        "confidence":
            causal_metrics.get(
                "confidence",
                "UNKNOWN",
            ),

        "analysis_completeness":
            causal_metrics.get(
                "analysis_completeness",
                None,
            ),

        "causal_chain_length":
            causal_metrics.get(
                "causal_chain_length",
                0,
            ),

        "claim_count":
            causal_metrics.get(
                "claim_count",
                0,
            ),

        "causal_claim_count":
            causal_metrics.get(
                "causal_claim_count",
                0,
            ),

        "alternative_cause_count":
            causal_metrics.get(
                "alternative_cause_count",
                0,
            ),
    }


# ============================================================
# ADVANTAGES
# ============================================================

def get_causal_advantages():
    """
    Return the major capabilities added by Causal RAG.
    """

    return [
        "Identifies cause and effect relationships",
        "Extracts structured cause-effect claims",
        "Builds multi-step causal chains",
        "Evaluates evidence strength",
        "Distinguishes causation from correlation",
        "Verifies causal conclusions",
        "Analyzes alternative causes",
        "Constructs causal graph representations",
        "Produces an explicit confidence assessment",
        "Provides an overall causal analysis score",
    ]


# ============================================================
# COMPARISON SUMMARY
# ============================================================

def build_comparison_summary(
    causal_metrics,
    time_comparison,
):
    """
    Generate a readable comparison summary.
    """

    score = causal_metrics.get(
        "overall_score"
    )

    verification_status = causal_metrics.get(
        "verification_status"
    )

    confidence = causal_metrics.get(
        "confidence"
    )

    evidence_quality = causal_metrics.get(
        "evidence_quality"
    )

    chain_quality = causal_metrics.get(
        "chain_quality"
    )

    completeness = causal_metrics.get(
        "analysis_completeness"
    )

    if score is None:
        score_text = "not available"
    else:
        score_text = f"{score}/100"

    completeness_text = (
        f"{completeness}%"
        if completeness is not None
        else "not available"
    )

    summary = (
        "Standard RAG primarily focuses on retrieving "
        "relevant knowledge and generating an answer from "
        "that retrieved information. "

        "Causal RAG extends the retrieval process with "
        "explicit cause-effect extraction, causal chain "
        "construction, evidence evaluation, causal "
        "verification, alternative-cause analysis and "
        "causal graph generation. "

        f"For this query, the Causal RAG evaluation score "
        f"is {score_text}, with evidence quality "
        f"{evidence_quality or 'UNKNOWN'}, chain quality "
        f"{chain_quality or 'UNKNOWN'}, verification status "
        f"{verification_status or 'UNKNOWN'}, confidence "
        f"{confidence or 'UNKNOWN'}, and analysis "
        f"completeness {completeness_text}. "

        f"The measured response-time difference was "
        f"{time_comparison['additional_time_ms']} ms."
    )

    return summary


# ============================================================
# COMPARE STANDARD RAG AND CAUSAL RAG
# ============================================================

def compare_rag_systems(
    question: str,
):
    """
    Compare Standard RAG and Causal RAG using the same
    question and return measurable comparison information.
    """

    question = str(
        question or ""
    ).strip()

    # --------------------------------------------------------
    # Validate question
    # --------------------------------------------------------

    if not question:

        return {
            "success": False,
            "question": "",
            "error": "Please provide a question.",
        }

    # ========================================================
    # RUN STANDARD RAG
    # ========================================================

    standard_result = run_standard_rag(
        question
    )

    # ========================================================
    # RUN CAUSAL RAG
    # ========================================================

    causal_result = run_causal_rag(
        question
    )

    # ========================================================
    # METRICS
    # ========================================================

    standard_metrics = get_standard_metrics(
        standard_result
    )

    causal_metrics = get_causal_metrics(
        causal_result
    )

    # ========================================================
    # FEATURE COMPARISON
    # ========================================================

    feature_comparison = compare_features(
        standard_metrics,
        causal_metrics
    )

    # ========================================================
    # RESPONSE TIME COMPARISON
    # ========================================================

    time_comparison = compare_response_time(
        standard_metrics,
        causal_metrics
    )

    # ========================================================
    # CAUSAL QUALITY
    # ========================================================

    causal_quality = build_causal_quality_summary(
        causal_metrics
    )

    # ========================================================
    # ADVANTAGES
    # ========================================================

    advantages = get_causal_advantages()

    # ========================================================
    # SUMMARY
    # ========================================================

    comparison_summary = build_comparison_summary(
        causal_metrics,
        time_comparison
    )

    # ========================================================
    # RETURN FINAL COMPARISON
    # ========================================================

    return {
        "success": True,

        "question": question,

        # ----------------------------------------------------
        # STANDARD RAG
        # ----------------------------------------------------

        "standard_rag": {
            "answer":
                standard_result.get(
                    "answer",
                    ""
                ),

            "retrieved_evidence":
                standard_result.get(
                    "retrieved_evidence",
                    ""
                ),

            "response_time_ms":
                standard_result.get(
                    "response_time_ms",
                    0
                ),

            "metrics":
                standard_metrics,

            "error":
                standard_result.get(
                    "error",
                    ""
                ),
        },

        # ----------------------------------------------------
        # CAUSAL RAG
        # ----------------------------------------------------

        "causal_rag": {
            "answer":
                causal_result.get(
                    "answer",
                    ""
                ),

            "retrieved_evidence":
                causal_result.get(
                    "retrieved_evidence",
                    ""
                ),

            "query_type":
                causal_result.get(
                    "query_type",
                    "CAUSAL"
                ),

            "causal_information":
                causal_result.get(
                    "causal_information",
                    {}
                ),

            "claims":
                causal_result.get(
                    "claims",
                    []
                ),

            "cause_effect_relationships":
                causal_result.get(
                    "cause_effect_relationships",
                    []
                ),

            "causal_chain":
                causal_result.get(
                    "causal_chain",
                    []
                ),

            "causal_chain_module":
                causal_result.get(
                    "causal_chain_module",
                    {}
                ),

            "causal_graph":
                causal_result.get(
                    "causal_graph",
                    {
                        "nodes": [],
                        "edges": []
                    }
                ),

            "evidence_evaluation":
                causal_result.get(
                    "evidence_evaluation",
                    {}
                ),

            "causal_verification":
                causal_result.get(
                    "causal_verification",
                    {}
                ),

            "causal_reasoning":
                causal_result.get(
                    "causal_reasoning",
                    {}
                ),

            "reasoning_summary":
                causal_result.get(
                    "reasoning_summary",
                    ""
                ),

            # Correct field
            "overall_evaluation":
                causal_result.get(
                    "overall_evaluation",
                    {}
                ),

            # Compatibility alias
            "evaluation":
                causal_result.get(
                    "evaluation",
                    causal_result.get(
                        "overall_evaluation",
                        {}
                    )
                ),

            "response_time_ms":
                causal_result.get(
                    "response_time_ms",
                    0
                ),

            "metrics":
                causal_metrics,

            "error":
                causal_result.get(
                    "error",
                    ""
                ),
        },

        # ----------------------------------------------------
        # COMPARISON
        # ----------------------------------------------------

        "comparison": {
            "feature_comparison":
                feature_comparison,

            "response_time":
                time_comparison,

            "causal_quality":
                causal_quality,

            "standard_rag":
                "Retrieval-based answer generation",

            "causal_rag":
                "Retrieval plus explicit causal reasoning",

            "causal_rag_advantages":
                advantages,

            "summary":
                comparison_summary,
        },
    }


# ============================================================
# MULTI-SCENARIO COMPARISON
# ============================================================

def compare_multiple_questions(
    questions,
):
    """
    Run Standard RAG and Causal RAG comparison over multiple
    questions.
    """

    if not questions:

        return {
            "success": False,
            "questions": [],
            "results": [],
            "summary": "No questions supplied.",
        }

    results = []

    for question in questions:

        question = str(
            question or ""
        ).strip()

        if not question:
            continue

        result = compare_rag_systems(
            question
        )

        results.append(
            result
        )

    # ========================================================
    # AGGREGATE RESPONSE TIME
    # ========================================================

    standard_times = []
    causal_times = []

    causal_scores = []

    supported_count = 0
    correlation_count = 0
    insufficient_count = 0

    total_chain_lengths = []
    strong_evidence_count = 0
    moderate_evidence_count = 0
    insufficient_evidence_count = 0

    for result in results:

        if not result.get(
            "success",
            False,
        ):
            continue

        standard_time = safe_number(
            result[
                "standard_rag"
            ].get(
                "response_time_ms",
                0,
            )
        )

        causal_time = safe_number(
            result[
                "causal_rag"
            ].get(
                "response_time_ms",
                0,
            )
        )

        standard_times.append(
            standard_time
        )

        causal_times.append(
            causal_time
        )

        causal_metrics = result[
            "causal_rag"
        ].get(
            "metrics",
            {},
        )

        # ----------------------------------------------------
        # Score
        # ----------------------------------------------------

        score = causal_metrics.get(
            "overall_score"
        )

        if isinstance(
            score,
            (int, float),
        ):

            causal_scores.append(
                float(score)
            )

        # ----------------------------------------------------
        # Verification status
        # ----------------------------------------------------

        status = causal_metrics.get(
            "verification_status"
        )

        if status == "CAUSALITY_SUPPORTED":

            supported_count += 1

        elif status == "CORRELATION_ONLY":

            correlation_count += 1

        elif status == "INSUFFICIENT_EVIDENCE":

            insufficient_count += 1

        # ----------------------------------------------------
        # Evidence
        # ----------------------------------------------------

        evidence_quality = str(
            causal_metrics.get(
                "evidence_quality",
                "",
            )
        ).upper()

        if evidence_quality == "STRONG":

            strong_evidence_count += 1

        elif evidence_quality in {
            "MODERATE",
            "MEDIUM",
        }:

            moderate_evidence_count += 1

        elif evidence_quality == "INSUFFICIENT":

            insufficient_evidence_count += 1

        # ----------------------------------------------------
        # Chain length
        # ----------------------------------------------------

        chain_length = safe_number(
            causal_metrics.get(
                "causal_chain_length",
                0,
            )
        )

        total_chain_lengths.append(
            chain_length
        )

    # ========================================================
    # AVERAGES
    # ========================================================

    if standard_times:

        average_standard_time = round(
            sum(standard_times)
            / len(standard_times),
            2,
        )

    else:

        average_standard_time = 0.0

    if causal_times:

        average_causal_time = round(
            sum(causal_times)
            / len(causal_times),
            2,
        )

    else:

        average_causal_time = 0.0

    if causal_scores:

        average_causal_score = round(
            sum(causal_scores)
            / len(causal_scores),
            2,
        )

    else:

        average_causal_score = None

    if total_chain_lengths:

        average_chain_length = round(
            sum(total_chain_lengths)
            / len(total_chain_lengths),
            2,
        )

    else:

        average_chain_length = 0.0

    # ========================================================
    # OVERHEAD
    # ========================================================

    additional_time = round(
        average_causal_time
        - average_standard_time,
        2,
    )

    if average_standard_time > 0:

        average_overhead = round(
            (
                additional_time
                / average_standard_time
            )
            * 100,
            2,
        )

    else:

        average_overhead = 0.0

    return {
        "success": True,

        "questions_evaluated":
            len(results),

        "results":
            results,

        "aggregate_metrics": {
            "average_standard_rag_time_ms":
                average_standard_time,

            "average_causal_rag_time_ms":
                average_causal_time,

            "average_additional_time_ms":
                additional_time,

            "average_causal_rag_overhead_percentage":
                average_overhead,

            "average_causal_rag_score":
                average_causal_score,

            "average_causal_chain_length":
                average_chain_length,

            "causality_supported":
                supported_count,

            "correlation_only":
                correlation_count,

            "insufficient_evidence":
                insufficient_count,

            "strong_evidence_cases":
                strong_evidence_count,

            "moderate_evidence_cases":
                moderate_evidence_count,

            "insufficient_evidence_cases":
                insufficient_evidence_count,
        },
    }


# ============================================================
# DEFAULT FINAL-DEMO QUESTIONS
# ============================================================

FINAL_DEMO_QUESTIONS = [

    # Direct cause
    "What caused the system failure?",

    # Multi-step cause
    "Why did system latency increase?",

    # Correlation-only
    "Did increased database traffic cause higher system latency?",

    # Multiple possible causes
    "What factor most likely caused the increase in response time?",

    # Additional causal example
    "Why did the model accuracy decrease?",

    # Insufficient evidence
    "Why did employee productivity decrease?",
]


# ============================================================
# TEST RUNNER
# ============================================================

if __name__ == "__main__":

    print(
        "\n" + "=" * 75
    )

    print(
        "STANDARD RAG vs CAUSAL RAG COMPARISON"
    )

    print(
        "TECHNOVA SOLUTIONS"
    )

    print(
        "=" * 75
    )

    # --------------------------------------------------------
    # Single detailed comparison
    # --------------------------------------------------------

    test_question = (
        "Why did system latency increase?"
    )

    print(
        "\nQuestion:"
    )

    print(
        test_question
    )

    result = compare_rag_systems(
        test_question
    )

    # --------------------------------------------------------
    # Standard RAG
    # --------------------------------------------------------

    print(
        "\n" + "-" * 75
    )

    print(
        "STANDARD RAG"
    )

    print(
        "-" * 75
    )

    standard = result[
        "standard_rag"
    ]

    print(
        "\nAnswer:"
    )

    print(
        standard.get(
            "answer",
            ""
        )
    )

    print(
        "\nResponse Time:"
    )

    print(
        str(
            standard.get(
                "response_time_ms",
                0
            )
        ) + " ms"
    )

    # --------------------------------------------------------
    # Causal RAG
    # --------------------------------------------------------

    print(
        "\n" + "-" * 75
    )

    print(
        "CAUSAL RAG"
    )

    print(
        "-" * 75
    )

    causal = result[
        "causal_rag"
    ]

    print(
        "\nAnswer:"
    )

    print(
        causal.get(
            "answer",
            ""
        )
    )

    print(
        "\nCausal Chain:"
    )

    print(
        causal.get(
            "causal_chain",
            []
        )
    )

    print(
        "\nCause-Effect Relationships:"
    )

    print(
        len(
            causal.get(
                "cause_effect_relationships",
                []
            )
        )
    )

    print(
        "\nEvidence Evaluation:"
    )

    print(
        causal.get(
            "evidence_evaluation",
            {}
        )
    )

    print(
        "\nCausal Verification:"
    )

    print(
        causal.get(
            "causal_verification",
            {}
        )
    )

    print(
        "\nOverall Evaluation:"
    )

    print(
        causal.get(
            "overall_evaluation",
            {}
        )
    )

    print(
        "\nResponse Time:"
    )

    print(
        str(
            causal.get(
                "response_time_ms",
                0
            )
        ) + " ms"
    )

    # --------------------------------------------------------
    # Feature comparison
    # --------------------------------------------------------

    print(
        "\n" + "-" * 75
    )

    print(
        "FEATURE COMPARISON"
    )

    print(
        "-" * 75
    )

    for feature in result[
        "comparison"
    ][
        "feature_comparison"
    ]:

        standard_status = (
            "YES"
            if feature[
                "standard_rag"
            ]
            else "NO"
        )

        causal_status = (
            "YES"
            if feature[
                "causal_rag"
            ]
            else "NO"
        )

        print(
            f"{feature['feature']:<35} "
            f"Standard RAG: {standard_status:<5} "
            f"Causal RAG: {causal_status}"
        )

    # --------------------------------------------------------
    # Response-time comparison
    # --------------------------------------------------------

    print(
        "\n" + "-" * 75
    )

    print(
        "RESPONSE TIME COMPARISON"
    )

    print(
        "-" * 75
    )

    print(
        result[
            "comparison"
        ][
            "response_time"
        ]
    )

    # --------------------------------------------------------
    # Causal quality
    # --------------------------------------------------------

    print(
        "\n" + "-" * 75
    )

    print(
        "CAUSAL QUALITY"
    )

    print(
        "-" * 75
    )

    print(
        result[
            "comparison"
        ][
            "causal_quality"
        ]
    )

    # --------------------------------------------------------
    # Advantages
    # --------------------------------------------------------

    print(
        "\n" + "-" * 75
    )

    print(
        "CAUSAL RAG ADVANTAGES"
    )

    print(
        "-" * 75
    )

    for advantage in result[
        "comparison"
    ][
        "causal_rag_advantages"
    ]:

        print(
            "✓ " + advantage
        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print(
        "\n" + "-" * 75
    )

    print(
        "SUMMARY"
    )

    print(
        "-" * 75
    )

    print(
        result[
            "comparison"
        ][
            "summary"
        ]
    )

    # --------------------------------------------------------
    # Multi-scenario evaluation
    # --------------------------------------------------------

    print(
        "\n" + "=" * 75
    )

    print(
        "MULTI-SCENARIO FINAL DEMO"
    )

    print(
        "=" * 75
    )

    multi_result = compare_multiple_questions(
        FINAL_DEMO_QUESTIONS
    )

    print(
        "\nQuestions Evaluated:",
        multi_result.get(
            "questions_evaluated",
            0,
        )
    )

    print(
        "\nAggregate Metrics:"
    )

    print(
        multi_result.get(
            "aggregate_metrics",
            {},
        )
    )

    print(
        "\n" + "=" * 75
    )

    print(
        "COMPARISON TEST COMPLETED"
    )

    print(
        "=" * 75
    )