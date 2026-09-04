# ============================================================
# CAUSAL REASONING MODULE
# Causal RAG Agent - TechNova Solutions
# ============================================================

from __future__ import annotations

import re
from typing import Any, Dict, List


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_text(value: Any) -> str:
    """
    Normalize a value into clean text.
    """
    if value is None:
        return ""

    return str(value).strip().rstrip(".").strip()


def normalize_text(value: Any) -> str:
    """
    Normalize text for comparisons.
    """
    return re.sub(
        r"\s+",
        " ",
        str(value or "").strip()
    ).lower()


def normalize_header(value: Any) -> str:
    """
    Normalize section headers.
    """
    text = str(value or "").strip().lower()

    text = text.rstrip(":")

    text = text.replace("_", " ")
    text = text.replace("-", " ")

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def unique_list(
    items: List[Any]
) -> List[str]:
    """
    Remove empty and duplicate values while preserving order.
    """

    result: List[str] = []

    for item in items:

        item = clean_text(item)

        if item and item not in result:

            result.append(item)

    return result


# ============================================================
# 1. EXTRACT CAUSAL INFORMATION
# ============================================================

def extract_causal_information(
    text: str
) -> Dict[str, Any]:

    """
    Extract structured causal information from evidence.

    Supported sections:

        Observation
        Cause
        Primary Cause
        Possible Cause
        Possible Causes
        Intermediate Factors
        Effect
        Evidence Strength
        Alternative Causes
        Causal Status
    """

    if not text:

        return {
            "observation": "",
            "cause": "",
            "intermediate_factors": [],
            "effect": "",
            "evidence_strength": "UNKNOWN",
            "alternative_causes": [],
        }

    text = str(text)

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    observation = ""
    cause = ""
    effect = ""

    evidence_strength = "UNKNOWN"

    intermediate_factors: List[str] = []
    alternative_causes: List[str] = []
    possible_causes: List[str] = []

    cause_details: Dict[str, str] = {}

    current_section = None

    # ========================================================
    # PARSE LINES
    # ========================================================

    for raw_line in lines:

        line = clean_text(raw_line)

        if not line:
            continue

        normalized_line = normalize_text(
            line
        )

        # ----------------------------------------------------
        # RETRIEVED EVIDENCE MARKER
        # ----------------------------------------------------

        if normalized_line in {
            "retrieved evidence",
            "retrieved evidence:",
        }:

            current_section = None
            continue

        # ----------------------------------------------------
        # HEADER + VALUE
        # ----------------------------------------------------

        if ":" in line:

            header, inline_value = line.split(
                ":",
                1
            )

            header = normalize_header(
                header
            )

            inline_value = clean_text(
                inline_value
            )

            # ------------------------------------------------
            # OBSERVATION
            # ------------------------------------------------

            if header == "observation":

                current_section = "observation"

                if inline_value:
                    observation = inline_value

                continue

            # ------------------------------------------------
            # CAUSE
            # ------------------------------------------------

            if header in {
                "cause",
                "primary cause",
                "possible cause",
                "best supported cause",
            }:

                current_section = "cause"

                if inline_value:
                    cause = inline_value

                continue

            # ------------------------------------------------
            # POSSIBLE CAUSES
            # ------------------------------------------------

            if header == "possible causes":

                current_section = (
                    "possible_causes"
                )

                if inline_value:

                    possible_causes.append(
                        inline_value
                    )

                continue

            # ------------------------------------------------
            # CAUSE A/B/C
            # ------------------------------------------------

            if header == "cause a":

                if inline_value:

                    cause_details["A"] = (
                        inline_value
                    )

                current_section = None
                continue

            if header == "cause b":

                if inline_value:

                    cause_details["B"] = (
                        inline_value
                    )

                current_section = None
                continue

            if header == "cause c":

                if inline_value:

                    cause_details["C"] = (
                        inline_value
                    )

                current_section = None
                continue

            # ------------------------------------------------
            # INTERMEDIATE FACTORS
            # ------------------------------------------------

            if header in {
                "intermediate factor",
                "intermediate factors",
            }:

                current_section = (
                    "intermediate"
                )

                if inline_value:

                    # Handles:
                    # Intermediate Factors:
                    # Higher database load. Increased processing time.

                    pieces = re.split(
                        r"[.;]",
                        inline_value
                    )

                    for piece in pieces:

                        cleaned = clean_text(
                            piece
                        )

                        if cleaned:

                            intermediate_factors.append(
                                cleaned
                            )

                continue

            # ------------------------------------------------
            # EFFECT
            # ------------------------------------------------

            if header in {
                "effect",
                "primary effect",
            }:

                current_section = "effect"

                if inline_value:
                    effect = inline_value

                continue

            # ------------------------------------------------
            # EVIDENCE STRENGTH
            # ------------------------------------------------

            if header in {
                "evidence strength",
                "strength",
            }:

                current_section = "strength"

                if inline_value:

                    value = (
                        inline_value
                        .upper()
                        .strip()
                    )

                    if value in {
                        "STRONG",
                        "MODERATE",
                        "WEAK",
                        "INSUFFICIENT",
                    }:

                        evidence_strength = value

                continue

            # ------------------------------------------------
            # ALTERNATIVE CAUSES
            # ------------------------------------------------

            if header in {
                "alternative cause",
                "alternative causes",
                "alternatives",
                "possible alternative causes",
            }:

                current_section = (
                    "alternatives"
                )

                if inline_value:

                    # Split simple sentence-separated alternatives.
                    pieces = re.split(
                        r"[.;]",
                        inline_value
                    )

                    for piece in pieces:

                        cleaned = clean_text(
                            piece
                        )

                        if cleaned:

                            alternative_causes.append(
                                cleaned
                            )

                continue

            # ------------------------------------------------
            # IGNORE OTHER HEADERS
            # ------------------------------------------------

            if header in {
                "event",
                "evidence",
                "causal evidence",
                "causal relationship",
                "causal chain",
                "conclusion",
                "confidence",
                "causal status",
                "possible relationship",
                "scenario",
                "scenario type",
            }:

                current_section = None

                continue

        # ====================================================
        # SECTION VALUES
        # ====================================================

        if current_section == "observation":

            if not observation:

                observation = line

            current_section = None

        elif current_section == "cause":

            if not cause:

                cause = line

            current_section = None

        elif current_section == "possible_causes":

            cleaned = line.lstrip(
                "-•* "
            ).strip()

            if cleaned:

                possible_causes.append(
                    cleaned
                )

        elif current_section == "intermediate":

            cleaned_parts = re.split(
                r"[.;]",
                line.lstrip(
                    "-•* "
                ).strip()
            )

            for part in cleaned_parts:

                cleaned = clean_text(
                    part
                )

                if cleaned:

                    intermediate_factors.append(
                        cleaned
                    )

        elif current_section == "effect":

            if not effect:

                effect = line

            current_section = None

        elif current_section == "strength":

            value = (
                line.upper()
                .strip()
            )

            if value in {
                "STRONG",
                "MODERATE",
                "WEAK",
                "INSUFFICIENT",
            }:

                evidence_strength = value

            current_section = None

        elif current_section == "alternatives":

            cleaned = line.lstrip(
                "-•* "
            ).strip()

            if cleaned:

                alternative_causes.append(
                    cleaned
                )

    # ========================================================
    # FALLBACK CAUSE
    # ========================================================

    if not cause:

        if "A" in cause_details:

            cause = cause_details["A"]

    # ========================================================
    # BUILD ALTERNATIVES
    # ========================================================

    alternatives = list(
        alternative_causes
    )

    for label in ["B", "C"]:

        if label in cause_details:

            alternatives.append(
                cause_details[label]
            )

    for candidate in possible_causes:

        alternatives.append(
            candidate
        )

    alternatives = unique_list(
        alternatives
    )

    # Remove primary cause from alternatives.
    final_alternatives = []

    for alternative in alternatives:

        if (
            cause
            and normalize_text(
                alternative
            )
            == normalize_text(
                cause
            )
        ):

            continue

        final_alternatives.append(
            alternative
        )

    # ========================================================
    # CORRELATION DETECTION
    # ========================================================

    lower_text = normalize_text(
        text
    )

    correlation_only = (
        "correlation_only" in lower_text
        or "correlation only" in lower_text
        or "correlation without strong causation"
        in lower_text
        or "direct causation is not confirmed"
        in lower_text
        or "no direct evidence" in lower_text
        or "relationship is correlational"
        in lower_text
    )

    if correlation_only:

        cause = ""

        if evidence_strength == "UNKNOWN":

            evidence_strength = "MODERATE"

    # ========================================================
    # INSUFFICIENT EVIDENCE
    # ========================================================

    insufficient = (
        "insufficient evidence" in lower_text
        or "no reliable evidence" in lower_text
        or "no reliable cause" in lower_text
        or "causality cannot be confirmed"
        in lower_text
        or "no verified cause" in lower_text
    )

    if (
        insufficient
        and not correlation_only
    ):

        cause = ""

        intermediate_factors = []

        evidence_strength = (
            "INSUFFICIENT"
        )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        "observation":
            clean_text(
                observation
            ),

        "cause":
            clean_text(
                cause
            ),

        "intermediate_factors":
            unique_list(
                intermediate_factors
            ),

        "effect":
            clean_text(
                effect
            ),

        "evidence_strength":
            evidence_strength,

        "alternative_causes":
            unique_list(
                final_alternatives
            ),
    }


# ============================================================
# 2. BUILD CAUSAL CHAIN
# ============================================================

def build_causal_chain(
    causal_information: Dict[str, Any],
    evidence: str = "",
) -> List[str]:

    """
    Build the strongest available causal chain.

    Priority:

        1. Explicit Causal Chain in evidence
        2. Cause + intermediate factors + effect
    """

    if not causal_information:

        return []

    # ========================================================
    # EXPLICIT CAUSAL CHAIN
    # ========================================================

    if evidence:

        evidence = str(
            evidence
        )

        lines = evidence.splitlines()

        for index, raw_line in enumerate(
            lines
        ):

            normalized_header = (
                normalize_header(
                    raw_line
                )
            )

            # ------------------------------------------------
            # Find "Causal Chain"
            # ------------------------------------------------

            if normalized_header == "causal chain":

                # ------------------------------------------------
                # Same-line value
                # ------------------------------------------------

                if ":" in raw_line:

                    chain_text = (
                        raw_line
                        .split(
                            ":",
                            1
                        )[1]
                        .strip()
                    )

                    if chain_text:

                        parts = re.split(
                            r"\s*(?:->|→|➜|=>)\s*",
                            chain_text
                        )

                        parts = [
                            clean_text(part)
                            for part in parts
                        ]

                        parts = [
                            part
                            for part in parts
                            if part
                        ]

                        if len(parts) >= 2:

                            return unique_list(
                                parts
                            )

                # ------------------------------------------------
                # Next-line value
                # ------------------------------------------------

                if index + 1 < len(lines):

                    chain_text = (
                        lines[index + 1]
                        .strip()
                    )

                    parts = re.split(
                        r"\s*(?:->|→|➜|=>)\s*",
                        chain_text
                    )

                    parts = [
                        clean_text(part)
                        for part in parts
                    ]

                    parts = [
                        part
                        for part in parts
                        if part
                    ]

                    if len(parts) >= 2:

                        return unique_list(
                            parts
                        )

    # ========================================================
    # STANDARD CHAIN
    # ========================================================

    cause = clean_text(
        causal_information.get(
            "cause",
            ""
        )
    )

    effect = clean_text(
        causal_information.get(
            "effect",
            ""
        )
    )

    intermediate = (
        causal_information.get(
            "intermediate_factors",
            []
        )
    )

    if not isinstance(
        intermediate,
        list
    ):

        intermediate = []

    chain: List[str] = []

    if cause:

        chain.append(
            cause
        )

    for factor in intermediate:

        factor = clean_text(
            factor
        )

        if (
            factor
            and factor not in chain
        ):

            chain.append(
                factor
            )

    if (
        effect
        and effect not in chain
    ):

        chain.append(
            effect
        )

    return chain


# ============================================================
# 3. EVALUATE EVIDENCE
# ============================================================

def evaluate_evidence(
    causal_information: Dict[str, Any]
) -> Dict[str, Any]:

    """
    Evaluate evidence strength.
    """

    if not causal_information:

        return {
            "strength": "UNKNOWN",
            "confidence": "LOW",
            "causal_conclusion": (
                "NOT_CONFIRMED"
            ),
            "explanation": (
                "No causal information was "
                "available for evaluation."
            ),
        }

    strength = str(
        causal_information.get(
            "evidence_strength",
            "UNKNOWN"
        )
    ).upper().strip()

    if strength == "STRONG":

        return {
            "strength": "STRONG",
            "confidence": "HIGH",
            "causal_conclusion": (
                "SUPPORTED"
            ),
            "explanation": (
                "The available evidence strongly "
                "supports the identified causal "
                "relationship."
            ),
        }

    if strength == "MODERATE":

        return {
            "strength": "MODERATE",
            "confidence": "MEDIUM",
            "causal_conclusion": (
                "NOT_CONFIRMED"
            ),
            "explanation": (
                "The evidence provides moderate "
                "support, but direct causation "
                "cannot be fully confirmed."
            ),
        }

    if strength == "WEAK":

        return {
            "strength": "WEAK",
            "confidence": "LOW",
            "causal_conclusion": (
                "NOT_CONFIRMED"
            ),
            "explanation": (
                "The available evidence is weak, "
                "so direct causation cannot be "
                "confidently confirmed."
            ),
        }

    if strength == "INSUFFICIENT":

        return {
            "strength": "INSUFFICIENT",
            "confidence": "LOW",
            "causal_conclusion": (
                "NOT_CONFIRMED"
            ),
            "explanation": (
                "The available evidence is "
                "insufficient to establish a "
                "reliable causal relationship."
            ),
        }

    return {
        "strength": "UNKNOWN",
        "confidence": "LOW",
        "causal_conclusion": (
            "NOT_CONFIRMED"
        ),
        "explanation": (
            "The evidence strength could not "
            "be determined."
        ),
    }


# ============================================================
# 4. ANALYZE ALTERNATIVE CAUSES
# ============================================================

def analyze_alternative_causes(
    causal_information: Dict[str, Any]
) -> Dict[str, Any]:

    """
    Analyze primary and alternative causes.
    """

    if not causal_information:

        return {
            "primary_cause": "",
            "alternative_causes": [],
            "preferred_cause": "",
            "conclusion": (
                "No causal information was available."
            ),
        }

    primary_cause = clean_text(
        causal_information.get(
            "cause",
            ""
        )
    )

    alternatives = causal_information.get(
        "alternative_causes",
        []
    )

    if not isinstance(
        alternatives,
        list
    ):

        alternatives = []

    cleaned_alternatives = []

    for alternative in alternatives:

        alternative = clean_text(
            alternative
        )

        if not alternative:
            continue

        if (
            primary_cause
            and normalize_text(
                alternative
            )
            == normalize_text(
                primary_cause
            )
        ):

            continue

        if (
            alternative
            not in cleaned_alternatives
        ):

            cleaned_alternatives.append(
                alternative
            )

    if not primary_cause:

        return {
            "primary_cause": "",
            "alternative_causes": (
                cleaned_alternatives
            ),
            "preferred_cause": "",
            "conclusion": (
                "The available evidence is "
                "insufficient to confidently "
                "identify a primary cause."
            ),
        }

    strength = str(
        causal_information.get(
            "evidence_strength",
            "UNKNOWN"
        )
    ).upper().strip()

    if strength == "STRONG":

        return {
            "primary_cause":
                primary_cause,

            "alternative_causes":
                cleaned_alternatives,

            "preferred_cause":
                primary_cause,

            "conclusion":
                (
                    "The primary cause is the "
                    "best-supported explanation "
                    "because the available "
                    "evidence is strong. "
                    "Alternative causes remain "
                    "possible but have weaker "
                    "support."
                ),
        }

    if strength == "MODERATE":

        return {
            "primary_cause":
                primary_cause,

            "alternative_causes":
                cleaned_alternatives,

            "preferred_cause":
                "",

            "conclusion":
                (
                    "The primary cause has "
                    "moderate support, but "
                    "alternative explanations "
                    "cannot be ruled out."
                ),
        }

    return {
        "primary_cause":
            primary_cause,

        "alternative_causes":
            cleaned_alternatives,

        "preferred_cause":
            "",

        "conclusion":
            (
                "The available evidence is "
                "insufficient to confidently "
                "prefer the primary cause over "
                "alternative explanations."
            ),
    }


# ============================================================
# 5. VERIFY CAUSAL CLAIM
# ============================================================

def verify_causal_claim(
    causal_information: Dict[str, Any],
    evidence_evaluation: Dict[str, Any]
) -> Dict[str, Any]:

    """
    Verify whether the evidence supports causation.
    """

    if not causal_information:

        return {
            "verified": False,
            "status": (
                "CAUSALITY_NOT_CONFIRMED"
            ),
            "confidence": "LOW",
            "message": (
                "No causal information was "
                "available."
            ),
        }

    if not evidence_evaluation:

        return {
            "verified": False,
            "status": (
                "CAUSALITY_NOT_CONFIRMED"
            ),
            "confidence": "LOW",
            "message": (
                "The evidence does not confirm "
                "direct causation."
            ),
        }

    strength = str(
        evidence_evaluation.get(
            "strength",
            "UNKNOWN"
        )
    ).upper().strip()

    conclusion = str(
        evidence_evaluation.get(
            "causal_conclusion",
            "NOT_CONFIRMED"
        )
    ).upper().strip()

    cause = clean_text(
        causal_information.get(
            "cause",
            ""
        )
    )

    if strength == "INSUFFICIENT":

        return {
            "verified": False,
            "status": (
                "INSUFFICIENT_EVIDENCE"
            ),
            "confidence": "LOW",
            "message": (
                "The available evidence is "
                "insufficient to establish "
                "causation."
            ),
        }

    if (
        not cause
        and strength == "MODERATE"
    ):

        return {
            "verified": False,
            "status": (
                "CORRELATION_ONLY"
            ),
            "confidence": "MEDIUM",
            "message": (
                "The evidence indicates a "
                "relationship, but direct "
                "causation is not confirmed."
            ),
        }

    if (
        not cause
        and strength == "WEAK"
    ):

        return {
            "verified": False,
            "status": (
                "CAUSALITY_NOT_CONFIRMED"
            ),
            "confidence": "LOW",
            "message": (
                "The evidence is too weak to "
                "establish direct causation."
            ),
        }

    if (
        cause
        and strength == "STRONG"
        and conclusion == "SUPPORTED"
    ):

        return {
            "verified": True,
            "status": (
                "CAUSALITY_SUPPORTED"
            ),
            "confidence": "HIGH",
            "message": (
                "The causal claim is supported "
                "by strong evidence."
            ),
        }

    return {
        "verified": False,
        "status": (
            "CAUSALITY_NOT_CONFIRMED"
        ),
        "confidence": "LOW",
        "message": (
            "The evidence does not confirm "
            "direct causation."
        ),
    }


# ============================================================
# 6. GENERATE REASONING SUMMARY
# ============================================================

def generate_reasoning_summary(
    causal_information: Dict[str, Any],
    causal_chain: List[str],
    evidence_evaluation: Dict[str, Any],
    causal_verification: Dict[str, Any],
    alternative_analysis: Dict[str, Any]
) -> str:

    """
    Generate a human-readable reasoning summary.
    """

    if not causal_information:

        return (
            "No causal information was available."
        )

    cause = clean_text(
        causal_information.get(
            "cause",
            ""
        )
    )

    effect = clean_text(
        causal_information.get(
            "effect",
            ""
        )
    )

    strength = evidence_evaluation.get(
        "strength",
        "UNKNOWN"
    )

    confidence = evidence_evaluation.get(
        "confidence",
        "LOW"
    )

    status = causal_verification.get(
        "status",
        "CAUSALITY_NOT_CONFIRMED"
    )

    # ========================================================
    # INSUFFICIENT
    # ========================================================

    if status == "INSUFFICIENT_EVIDENCE":

        return (
            "The available evidence is "
            "insufficient to establish a "
            "reliable causal relationship. "
            "The system therefore avoids "
            "inventing a cause."
        )

    # ========================================================
    # CORRELATION
    # ========================================================

    if status == "CORRELATION_ONLY":

        if effect:

            return (
                f"The evidence indicates that "
                f"{effect.lower()}, but the available "
                "information does not establish a "
                "direct causal relationship. "
                "The relationship should therefore "
                "be treated as correlational rather "
                "than causal."
            )

        return (
            "The evidence indicates correlation, "
            "but direct causation has not been "
            "established."
        )

    # ========================================================
    # CAUSAL WITH CHAIN
    # ========================================================

    if (
        cause
        and effect
        and causal_chain
    ):

        chain_text = " → ".join(
            causal_chain
        )

        return (
            f"The evidence supports {cause} "
            f"as the primary cause of {effect}. "
            f"The supported causal pathway is: "
            f"{chain_text}. "
            f"Evidence strength is {strength} "
            f"with {confidence} confidence. "
            f"Verification status: {status}."
        )

    # ========================================================
    # CAUSAL WITHOUT CHAIN
    # ========================================================

    if cause and effect:

        return (
            f"The evidence supports {cause} "
            f"as the primary cause of {effect}. "
            f"Evidence strength is {strength} "
            f"with {confidence} confidence. "
            f"Verification status: {status}."
        )

    # ========================================================
    # FALLBACK
    # ========================================================

    return (
        "The available evidence does not "
        "provide enough information for a "
        "reliable causal conclusion."
    )


# ============================================================
# 7. COMPLETE REASONING PIPELINE
# ============================================================

def reason_about_cause(
    evidence: str = "",
    causal_information: Dict[str, Any] | None = None,
    causal_chain: List[str] | None = None,
) -> Dict[str, Any]:

    """
    Complete reasoning pipeline.

    IMPORTANT:
    This function is backward compatible with the old API:

        reason_about_cause(evidence)

    It also supports the richer analyzer API:

        reason_about_cause(
            evidence,
            causal_information,
            causal_chain
        )

    This prevents function-signature mismatches between
    the analyzer and reasoning module.
    """

    evidence = str(
        evidence or ""
    ).strip()

    # ========================================================
    # EMPTY EVIDENCE
    # ========================================================

    if not evidence and not causal_information:

        causal_information = {
            "observation": "",
            "cause": "",
            "intermediate_factors": [],
            "effect": "",
            "evidence_strength": (
                "INSUFFICIENT"
            ),
            "alternative_causes": [],
        }

        evidence_evaluation = (
            evaluate_evidence(
                causal_information
            )
        )

        alternative_analysis = (
            analyze_alternative_causes(
                causal_information
            )
        )

        causal_verification = (
            verify_causal_claim(
                causal_information,
                evidence_evaluation
            )
        )

        return {

            "success": True,

            "causal_information":
                causal_information,

            "causal_chain":
                [],

            "evidence_evaluation":
                evidence_evaluation,

            "alternative_analysis":
                alternative_analysis,

            "causal_verification":
                causal_verification,

            "reasoning_summary":
                (
                    "The available evidence is "
                    "insufficient to establish a "
                    "reliable causal relationship."
                ),
        }

    # ========================================================
    # EXTRACT WHEN INFORMATION WAS NOT SUPPLIED
    # ========================================================

    if not causal_information:

        causal_information = (
            extract_causal_information(
                evidence
            )
        )

    else:

        # Make a copy so we never mutate analyzer data.
        causal_information = dict(
            causal_information
        )

    # ========================================================
    # BUILD CHAIN
    # ========================================================

    if causal_chain is not None:

        chain = [
            clean_text(item)
            for item in causal_chain
            if clean_text(item)
        ]

    else:

        chain = build_causal_chain(
            causal_information,
            evidence
        )

    # ========================================================
    # If evidence contains a richer chain,
    # prefer it over a shortened supplied chain.
    # ========================================================

    if evidence:

        evidence_chain = (
            build_causal_chain(
                causal_information,
                evidence
            )
        )

        if len(evidence_chain) > len(
            chain
        ):

            chain = evidence_chain

    # ========================================================
    # EVIDENCE EVALUATION
    # ========================================================

    evidence_evaluation = (
        evaluate_evidence(
            causal_information
        )
    )

    # ========================================================
    # ALTERNATIVE ANALYSIS
    # ========================================================

    alternative_analysis = (
        analyze_alternative_causes(
            causal_information
        )
    )

    # ========================================================
    # CAUSAL VERIFICATION
    # ========================================================

    causal_verification = (
        verify_causal_claim(
            causal_information,
            evidence_evaluation
        )
    )

    # ========================================================
    # REASONING SUMMARY
    # ========================================================

    reasoning_summary = (
        generate_reasoning_summary(
            causal_information,
            chain,
            evidence_evaluation,
            causal_verification,
            alternative_analysis
        )
    )

    # ========================================================
    # FULL RESULT
    # ========================================================

    return {

        "success": True,

        "causal_information":
            causal_information,

        "causal_chain":
            chain,

        "evidence_evaluation":
            evidence_evaluation,

        "alternative_analysis":
            alternative_analysis,

        "causal_verification":
            causal_verification,

        "reasoning_summary":
            reasoning_summary,

        "reasoning_method":
            "evidence_grounded_deterministic_reasoning",
    }


# ============================================================
# 8. TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print(
        "CAUSAL REASONING MODULE TEST"
    )
    print("=" * 70)

    test_evidence = """

    SCENARIO 2: MULTI-STEP CAUSE

    Event:
    System latency increased and eventually caused request timeouts.

    Observation:
    Average system latency increased from 100 ms to 180 ms.

    Cause:
    Increased database traffic.

    Evidence:
    User requests increased significantly and database query volume increased by approximately 40%.

    Intermediate Factors:
    Higher database load.
    Increased processing time.

    Effect:
    Higher system latency followed by system timeout.

    Causal Chain:
    Increased user requests -> Higher database queries -> Higher database load -> Increased processing time -> Higher system latency -> System timeout.

    Evidence Strength:
    STRONG

    Confidence:
    HIGH

    Alternative Causes:
    Reduced server resources could also contribute to latency.
    Network congestion is another possible factor, but the available evidence is weaker.

    RETRIEVED EVIDENCE:
    """

    result = reason_about_cause(
        test_evidence
    )

    print()
    print(
        "CAUSAL INFORMATION:"
    )

    print(
        result[
            "causal_information"
        ]
    )

    print()
    print(
        "CAUSAL CHAIN:"
    )

    if result[
        "causal_chain"
    ]:

        print(
            " → ".join(
                result[
                    "causal_chain"
                ]
            )
        )

    else:

        print("None")

    print()
    print(
        "EVIDENCE EVALUATION:"
    )

    print(
        result[
            "evidence_evaluation"
        ]
    )

    print()
    print(
        "ALTERNATIVE CAUSES:"
    )

    print(
        result[
            "alternative_analysis"
        ]
    )

    print()
    print(
        "CAUSAL VERIFICATION:"
    )

    print(
        result[
            "causal_verification"
        ]
    )

    print()
    print(
        "REASONING SUMMARY:"
    )

    print(
        result[
            "reasoning_summary"
        ]
    )

    print()
    print("=" * 70)
    print(
        "TEST COMPLETED"
    )
    print("=" * 70)