import json
import time
import re
from pathlib import Path

from backend.causal_analyzer import analyze_query


# ============================================================
# DATASET CONFIGURATION
# ============================================================

DATASET_PATH = Path(__file__).parent / "causal_test_dataset.json"


# ============================================================
# TEXT HELPERS
# ============================================================

def normalize_text(value):
    if value is None:
        return ""

    if isinstance(value, list):
        return " ".join(
            normalize_text(item)
            for item in value
        )

    if isinstance(value, dict):
        return " ".join(
            normalize_text(item)
            for item in value.values()
        )

    return str(value).strip()


def clean_text(value):
    text = normalize_text(value).lower()

    text = text.replace("_", " ")
    text = text.replace("-", " ")

    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def is_unknown_value(value):
    text = clean_text(value)

    return text in {
        "",
        "unknown",
        "none",
        "null",
        "not available",
        "not identified",
        "not confirmed",
        "insufficient evidence",
        "no cause identified",
        "cause not identified",
    }


# ============================================================
# RECURSIVE FIELD FINDER
# ============================================================

def find_field(data, names):

    if not isinstance(data, dict):
        return None

    candidates = {
        str(name)
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
        for name in names
    }

    for key, value in data.items():

        normalized_key = (
            str(key)
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )

        if normalized_key in candidates:
            return value

    for value in data.values():

        if isinstance(value, dict):

            result = find_field(
                value,
                names
            )

            if result is not None:
                return result

        elif isinstance(value, list):

            for item in value:

                if isinstance(item, dict):

                    result = find_field(
                        item,
                        names
                    )

                    if result is not None:
                        return result

    return None


# ============================================================
# EXPECTED VALUES
# ============================================================

def get_expected_relationship(scenario):

    value = find_field(
        scenario,
        [
            "expected_causal_status",
            "expected_relationship",
            "expected_relation",
            "causal_status",
        ]
    )

    text = clean_text(value)

    if "correlation" in text:
        return "CORRELATION"

    if "causal" in text:
        return "CAUSAL"

    scenario_type = clean_text(
        find_field(
            scenario,
            [
                "scenario_type",
                "type",
            ]
        )
    )

    if scenario_type in {
        "direct cause",
        "multi step cause",
        "multiple possible causes",
    }:
        return "CAUSAL"

    if scenario_type == "correlation only":
        return "CORRELATION"

    if scenario_type == "insufficient evidence":
        return "UNKNOWN"

    return "UNKNOWN"


def get_expected_confidence(scenario):

    value = find_field(
        scenario,
        [
            "expected_confidence",
            "confidence",
            "expected_causal_confidence",
        ]
    )

    text = clean_text(value)

    if "high" in text:
        return "HIGH"

    if "medium" in text or "moderate" in text:
        return "MEDIUM"

    return "LOW"


def get_expected_strength(scenario):

    value = find_field(
        scenario,
        [
            "evidence_strength",
            "expected_evidence_strength",
            "expected_strength",
        ]
    )

    text = clean_text(value)

    if "strong" in text:
        return "STRONG"

    if "moderate" in text or "medium" in text:
        return "MODERATE"

    if "weak" in text:
        return "WEAK"

    return "INSUFFICIENT"


def get_expected_cause(scenario):

    return normalize_text(
        scenario.get(
            "expected_cause",
            ""
        )
    )


def get_expected_effect(scenario):

    return normalize_text(
        scenario.get(
            "expected_effect",
            ""
        )
    )


def get_expected_chain(scenario):

    value = scenario.get(
        "expected_chain",
        []
    )

    if isinstance(value, list):

        return [
            normalize_text(item)
            for item in value
            if normalize_text(item)
        ]

    text = normalize_text(value)

    if "->" in text:

        return [
            item.strip()
            for item in text.split("->")
            if item.strip()
        ]

    if "→" in text:

        return [
            item.strip()
            for item in text.split("→")
            if item.strip()
        ]

    return [text] if text else []


def get_expected_alternatives(scenario):

    value = scenario.get(
        "alternative_causes",
        []
    )

    if value is None:
        return []

    if isinstance(value, list):

        return [
            normalize_text(item)
            for item in value
            if normalize_text(item)
        ]

    return [
        normalize_text(value)
    ]


# ============================================================
# ACTUAL VALUES
# ============================================================

def get_actual_relationship(result):

    value = find_field(
        result,
        [
            "causal_status",
            "causal_relationship",
            "relationship",
            "relation",
            "status",
        ]
    )

    text = clean_text(value)

    if "correlation" in text:
        return "CORRELATION"

    if "causal" in text:
        return "CAUSAL"

    return "UNKNOWN"


def get_actual_confidence(result):

    value = find_field(
        result,
        [
            "confidence",
            "causal_confidence",
        ]
    )

    text = clean_text(value)

    if "high" in text:
        return "HIGH"

    if "medium" in text or "moderate" in text:
        return "MEDIUM"

    return "LOW"


def get_actual_strength(result):

    value = find_field(
        result,
        [
            "evidence_strength",
            "strength",
        ]
    )

    text = clean_text(value)

    if "strong" in text:
        return "STRONG"

    if "moderate" in text or "medium" in text:
        return "MODERATE"

    if "weak" in text:
        return "WEAK"

    return "INSUFFICIENT"


def get_actual_cause(result):

    value = find_field(
        result,
        [
            "primary_cause",
            "cause",
            "causal_factor",
        ]
    )

    if is_unknown_value(value):
        return ""

    return normalize_text(value)


def get_actual_effect(result):

    value = find_field(
        result,
        [
            "primary_effect",
            "effect",
        ]
    )

    if is_unknown_value(value):
        return ""

    return normalize_text(value)


def get_actual_answer(result):

    value = find_field(
        result,
        [
            "answer",
            "final_answer",
            "explanation",
            "response",
        ]
    )

    return normalize_text(value)


def get_actual_chain(result):

    value = find_field(
        result,
        [
            "causal_chain",
            "chain",
        ]
    )

    if value is None:
        return []

    if isinstance(value, list):

        output = []

        for item in value:

            text = normalize_text(item)

            if text and not is_unknown_value(text):
                output.append(text)

        return output

    if isinstance(value, dict):

        nested = find_field(
            value,
            [
                "chain",
                "steps",
                "causal_chain",
            ]
        )

        if nested is not None:

            return get_actual_chain(
                {
                    "causal_chain": nested
                }
            )

        return []

    text = normalize_text(value)

    if not text:
        return []

    if "->" in text:

        return [
            item.strip()
            for item in text.split("->")
            if item.strip()
        ]

    if "→" in text:

        return [
            item.strip()
            for item in text.split("→")
            if item.strip()
        ]

    return [text]


def get_actual_alternatives(result):

    value = find_field(
        result,
        [
            "alternative_causes",
            "alternatives",
            "possible_alternative_causes",
        ]
    )

    if value is None:
        return []

    if isinstance(value, list):

        return [
            normalize_text(item)
            for item in value
            if normalize_text(item)
            and not is_unknown_value(item)
        ]

    if isinstance(value, dict):

        nested = find_field(
            value,
            [
                "alternative_causes",
                "alternatives",
                "possible_alternative_causes",
            ]
        )

        if nested is not None:

            return get_actual_alternatives(
                {
                    "alternative_causes": nested
                }
            )

        return []

    text = normalize_text(value)

    if not text or is_unknown_value(text):
        return []

    return [text]


# ============================================================
# BUILD EVIDENCE
# ============================================================

def build_evidence(scenario):

    parts = []

    fields = [
        "event",
        "observation",
        "evidence",
        "causal_evidence",
        "cause",
        "effect",
        "intermediate_factors",
        "causal_chain",
        "alternative_causes",
        "conclusion",
    ]

    for field in fields:

        value = scenario.get(field)

        if value is None:
            continue

        if isinstance(value, list):

            for item in value:

                if item:

                    parts.append(
                        f"{field}: {normalize_text(item)}"
                    )

        else:

            text = normalize_text(value)

            if text:

                parts.append(
                    f"{field}: {text}"
                )

    return "\n".join(parts)


# ============================================================
# CAUSAL CONCEPTS
# ============================================================

CONCEPTS = {

    "DATABASE_TRAFFIC": [
        "database traffic",
        "db traffic",
    ],

    "DATABASE_QUERIES": [
        "database query",
        "database queries",
        "database query volume",
        "db query",
        "db queries",
        "db query volume",
    ],

    "DATABASE_LOAD": [
        "database load",
        "db load",
    ],

    "DATABASE_CONNECTION": [
        "database connection",
        "database connections",
        "connection overload",
    ],

    "USER_REQUESTS": [
        "user requests",
        "increased user requests",
        "user request",
    ],

    "USER_TRAFFIC": [
        "user traffic",
        "increased user traffic",
    ],

    "USER_ACTIVITY": [
        "user activity",
        "increased user activity",
    ],

    "APPLICATION_WORKLOAD": [
        "application workload",
        "application processing",
        "application load",
    ],

    "CPU": [
        "cpu utilization",
        "high cpu",
        "cpu increased",
        "raised cpu",
    ],

    "PROCESSING_TIME": [
        "processing time",
        "query processing time",
        "increased processing time",
        "longer query processing time",
        "longer query processing",
    ],

    "PROCESSING_DELAY": [
        "processing delay",
        "processing delays",
        "increased processing delay",
    ],

    "SYSTEM_LATENCY": [
        "system latency",
        "higher system latency",
        "latency increase",
        "increased system latency",
    ],

    "RESPONSE_TIME": [
        "response time",
        "higher response time",
        "response time increase",
        "increased response time",
    ],

    "SLOW_APPLICATION": [
        "slower application response",
        "application became slow",
        "application slow",
    ],

    "REQUEST_TIMEOUT": [
        "request timeout",
        "request timeouts",
        "requests timed out",
        "timed out",
    ],

    "SERVER_RESOURCES": [
        "server resource exhaustion",
        "reduced server resources",
        "insufficient server resources",
        "server resource limitations",
    ],

    "SERVER_LOAD": [
        "server load",
        "increased server load",
    ],

    "NETWORK": [
        "network congestion",
        "network instability",
        "network traffic",
    ],

    "SYSTEM_FAILURE": [
        "system failure",
    ],
}


def get_concept(text):

    text = clean_text(text)

    for concept, phrases in CONCEPTS.items():

        for phrase in phrases:

            if phrase in text:
                return concept

    return None


def concept_match(
    expected,
    actual
):

    expected_clean = clean_text(
        expected
    )

    actual_clean = clean_text(
        actual
    )

    if not expected_clean or not actual_clean:
        return False

    if expected_clean in actual_clean:
        return True

    if actual_clean in expected_clean:
        return True

    expected_concept = get_concept(
        expected_clean
    )

    actual_concept = get_concept(
        actual_clean
    )

    if (
        expected_concept
        and actual_concept
        and expected_concept
        == actual_concept
    ):
        return True

    expected_tokens = {
        token
        for token in expected_clean.split()
        if len(token) >= 4
    }

    actual_tokens = {
        token
        for token in actual_clean.split()
        if len(token) >= 4
    }

    if not expected_tokens:
        return False

    overlap = len(
        expected_tokens
        & actual_tokens
    ) / len(expected_tokens)

    return overlap >= 0.50


# ============================================================
# EXTRACTION ACCURACY
# ============================================================

def calculate_extraction_accuracy(
    scenario,
    result
):

    relationship = get_expected_relationship(
        scenario
    )

    expected_cause = get_expected_cause(
        scenario
    )

    expected_effect = get_expected_effect(
        scenario
    )

    actual_cause = get_actual_cause(
        result
    )

    actual_effect = get_actual_effect(
        result
    )

    # --------------------------------------------------------
    # INSUFFICIENT EVIDENCE
    # --------------------------------------------------------

    if relationship == "UNKNOWN":

        return (
            100.0
            if not actual_cause
            else 0.0
        )

    # --------------------------------------------------------
    # CORRELATION ONLY
    # --------------------------------------------------------
    #
    # In a correlation-only scenario, the system SHOULD NOT
    # identify a causal cause. Therefore an empty/unconfirmed
    # cause is correct behavior.
    #
    # We evaluate only the effect when an expected effect
    # exists.
    # --------------------------------------------------------

    if relationship == "CORRELATION":

        checks = []

        if expected_effect:

            effect_correct = (
                concept_match(
                    expected_effect,
                    actual_effect
                )
            )

            checks.append(
                effect_correct
            )

        # If no expected effect exists, correctly avoiding
        # causal extraction is sufficient.
        if not checks:

            return 100.0

        return (
            sum(checks)
            / len(checks)
            * 100
        )

    # --------------------------------------------------------
    # NORMAL CAUSAL CASE
    # --------------------------------------------------------

    checks = []

    if expected_cause:

        checks.append(
            concept_match(
                expected_cause,
                actual_cause
            )
        )

    if expected_effect:

        checks.append(
            concept_match(
                expected_effect,
                actual_effect
            )
        )

    if not checks:
        return 100.0

    return (
        sum(checks)
        / len(checks)
        * 100
    )


# ============================================================
# CHAIN ACCURACY
# ============================================================

def calculate_chain_accuracy(
    scenario,
    actual_chain
):

    expected_chain = get_expected_chain(
        scenario
    )

    relationship = get_expected_relationship(
        scenario
    )

    if relationship in {
        "CORRELATION",
        "UNKNOWN",
    }:

        return 100.0

    if not expected_chain:
        return 100.0

    if not actual_chain:
        return 0.0

    matched = 0
    used_indices = set()

    for expected_index, expected_item in enumerate(
        expected_chain
    ):

        if expected_index < len(actual_chain):

            if concept_match(
                expected_item,
                actual_chain[expected_index]
            ):

                matched += 1

                used_indices.add(
                    expected_index
                )

                continue

        found = False

        for actual_index, actual_item in enumerate(
            actual_chain
        ):

            if actual_index in used_indices:
                continue

            if concept_match(
                expected_item,
                actual_item
            ):

                matched += 1

                used_indices.add(
                    actual_index
                )

                found = True

                break

        if found:
            continue

    return (
        matched
        / len(expected_chain)
        * 100
    )


# ============================================================
# FAITHFULNESS
# ============================================================

def calculate_faithfulness(
    result,
    evidence
):

    evidence_text = clean_text(
        evidence
    )

    cause = get_actual_cause(
        result
    )

    effect = get_actual_effect(
        result
    )

    checks = []

    if cause:

        cause_supported = (
            clean_text(cause)
            in evidence_text
            or get_concept(cause)
            == get_concept(evidence_text)
            or any(
                token in evidence_text
                for token in clean_text(cause).split()
                if len(token) >= 5
            )
        )

        checks.append(
            cause_supported
        )

    if effect:

        effect_supported = (
            clean_text(effect)
            in evidence_text
            or any(
                token in evidence_text
                for token in clean_text(effect).split()
                if len(token) >= 5
            )
        )

        checks.append(
            effect_supported
        )

    if not checks:
        return 100.0

    return (
        sum(checks)
        / len(checks)
        * 100
    )


# ============================================================
# ALTERNATIVE CAUSE ACCURACY
# ============================================================

def calculate_alternative_accuracy(
    scenario,
    result
):

    expected = get_expected_alternatives(
        scenario
    )

    actual = get_actual_alternatives(
        result
    )

    relationship = get_expected_relationship(
        scenario
    )

    if relationship == "UNKNOWN":
        return 100.0

    if not expected:
        return 100.0

    if not actual:
        return 0.0

    matched = 0
    used = set()

    for expected_item in expected:

        for index, actual_item in enumerate(
            actual
        ):

            if index in used:
                continue

            if concept_match(
                expected_item,
                actual_item
            ):

                matched += 1

                used.add(
                    index
                )

                break

    return (
        matched
        / len(expected)
        * 100
    )


# ============================================================
# ANSWER ACCURACY
# ============================================================

def calculate_answer_accuracy(
    scenario,
    result
):

    answer = clean_text(
        get_actual_answer(result)
    )

    if not answer:
        return 0.0

    relationship = get_expected_relationship(
        scenario
    )

    expected_cause = get_expected_cause(
        scenario
    )

    expected_effect = get_expected_effect(
        scenario
    )

    checks = []

    # --------------------------------------------------------
    # CAUSAL
    # --------------------------------------------------------

    if relationship == "CAUSAL":

        if expected_cause:

            checks.append(
                concept_match(
                    expected_cause,
                    answer
                )
            )

        if expected_effect:

            checks.append(
                concept_match(
                    expected_effect,
                    answer
                )
            )

    # --------------------------------------------------------
    # CORRELATION
    # --------------------------------------------------------

    elif relationship == "CORRELATION":

        correlation_terms = [
            "correlation",
            "correlational",
            "correlated",
            "association",
            "associated",
            "same period",
            "same time",
            "increased together",
            "does not establish causation",
            "does not establish a causal",
            "causation is not confirmed",
            "causal relationship is not confirmed",
            "direct causation is not confirmed",
            "direct causation not confirmed",
            "causal link is not confirmed",
            "causal link not confirmed",
            "not proven to cause",
            "cannot confirm causation",
            "cannot establish causation",
        ]

        checks.append(
            any(
                term in answer
                for term in correlation_terms
            )
        )

    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    elif relationship == "UNKNOWN":

        insufficient_terms = [
            "insufficient evidence",
            "insufficient",
            "not enough evidence",
            "not enough support",
            "does not provide enough support",
            "does not provide sufficient evidence",
            "no reliable evidence",
            "no verified cause",
            "no cause identified",
            "cannot determine",
            "cannot identify",
            "unable to identify",
            "unknown",
            "not confirmed",
            "not enough information",
            "cannot be established",
        ]

        checks.append(
            any(
                term in answer
                for term in insufficient_terms
            )
        )

    if not checks:
        return 100.0

    return (
        sum(checks)
        / len(checks)
        * 100
    )


# ============================================================
# HALLUCINATION
# ============================================================

def calculate_hallucination(
    result,
    evidence
):

    evidence_text = clean_text(
        evidence
    )

    cause = get_actual_cause(
        result
    )

    effect = get_actual_effect(
        result
    )

    if not cause and not effect:
        return "NO"

    unsupported = 0
    checked = 0

    if cause:

        checked += 1

        supported = (
            clean_text(cause)
            in evidence_text
            or any(
                token in evidence_text
                for token in clean_text(cause).split()
                if len(token) >= 5
            )
        )

        if not supported:
            unsupported += 1

    if effect:

        checked += 1

        supported = (
            clean_text(effect)
            in evidence_text
            or any(
                token in evidence_text
                for token in clean_text(effect).split()
                if len(token) >= 5
            )
        )

        if not supported:
            unsupported += 1

    if checked == 0:
        return "NO"

    return (
        "YES"
        if unsupported > 0
        else "NO"
    )


# ============================================================
# SCENARIO EVALUATION
# ============================================================

def evaluate_scenario(
    scenario,
    index
):

    question = normalize_text(
        scenario.get(
            "question",
            ""
        )
    )

    scenario_type = normalize_text(
        scenario.get(
            "scenario_type",
            ""
        )
    ).upper()

    evidence = build_evidence(
        scenario
    )

    expected_relationship = (
        get_expected_relationship(
            scenario
        )
    )

    expected_confidence = (
        get_expected_confidence(
            scenario
        )
    )

    expected_strength = (
        get_expected_strength(
            scenario
        )
    )

    start_time = time.perf_counter()

    try:

        result = analyze_query(
            question,
            evidence=evidence
        )

    except Exception as error:

        result = {
            "success": False,
            "answer": "",
            "error": str(error),
        }

    elapsed_ms = (
        time.perf_counter()
        - start_time
    ) * 1000

    actual_relationship = (
        get_actual_relationship(
            result
        )
    )

    actual_confidence = (
        get_actual_confidence(
            result
        )
    )

    actual_strength = (
        get_actual_strength(
            result
        )
    )

    actual_chain = get_actual_chain(
        result
    )

    extraction_accuracy = (
        calculate_extraction_accuracy(
            scenario,
            result
        )
    )

    relation_accuracy = (
        100.0
        if actual_relationship
        == expected_relationship
        else 0.0
    )

    confidence_accuracy = (
        100.0
        if actual_confidence
        == expected_confidence
        else 0.0
    )

    evidence_accuracy = (
        100.0
        if actual_strength
        == expected_strength
        else 0.0
    )

    chain_accuracy = (
        calculate_chain_accuracy(
            scenario,
            actual_chain
        )
    )

    faithfulness = (
        calculate_faithfulness(
            result,
            evidence
        )
    )

    alternative_accuracy = (
        calculate_alternative_accuracy(
            scenario,
            result
        )
    )

    answer_accuracy = (
        calculate_answer_accuracy(
            scenario,
            result
        )
    )

    hallucination = (
        calculate_hallucination(
            result,
            evidence
        )
    )

    core_metrics = [
        extraction_accuracy,
        relation_accuracy,
        confidence_accuracy,
        evidence_accuracy,
        chain_accuracy,
        faithfulness,
        answer_accuracy,
    ]

    passed = all(
        metric >= 80.0
        for metric in core_metrics
    )

    if hallucination == "YES":
        passed = False

    return {
        "index": index,
        "scenario_type": scenario_type,
        "question": question,

        "expected_relationship":
            expected_relationship,

        "actual_relationship":
            actual_relationship,

        "expected_confidence":
            expected_confidence,

        "actual_confidence":
            actual_confidence,

        "expected_strength":
            expected_strength,

        "actual_strength":
            actual_strength,

        "extraction_accuracy":
            extraction_accuracy,

        "relation_accuracy":
            relation_accuracy,

        "confidence_accuracy":
            confidence_accuracy,

        "evidence_accuracy":
            evidence_accuracy,

        "chain_accuracy":
            chain_accuracy,

        "faithfulness":
            faithfulness,

        "alternative_accuracy":
            alternative_accuracy,

        "answer_accuracy":
            answer_accuracy,

        "hallucination":
            hallucination,

        "response_time":
            elapsed_ms,

        "result":
            result,

        "passed":
            passed,
    }


# ============================================================
# PRINT RESULT
# ============================================================

def print_scenario_result(data):

    print("-" * 70)

    print(
        f"Scenario {data['index']}"
    )

    print(
        f"Type     : "
        f"{data['scenario_type']}"
    )

    print(
        f"Question : "
        f"{data['question']}"
    )

    print(
        f"Expected Relationship : "
        f"{data['expected_relationship']}"
    )

    print(
        f"Actual Relationship   : "
        f"{data['actual_relationship']}"
    )

    print(
        f"Expected Confidence   : "
        f"{data['expected_confidence']}"
    )

    print(
        f"Actual Confidence     : "
        f"{data['actual_confidence']}"
    )

    print(
        f"Expected Evidence     : "
        f"{data['expected_strength']}"
    )

    print(
        f"Actual Evidence       : "
        f"{data['actual_strength']}"
    )

    print(
        f"Causal Extraction     : "
        f"{data['extraction_accuracy']:.2f}%"
    )

    print(
        f"Chain Accuracy        : "
        f"{data['chain_accuracy']:.2f}%"
    )

    print(
        f"Evidence Faithfulness : "
        f"{data['faithfulness']:.2f}%"
    )

    print(
        f"Alternative Accuracy  : "
        f"{data['alternative_accuracy']:.2f}%"
    )

    print(
        f"Answer Accuracy       : "
        f"{data['answer_accuracy']:.2f}%"
    )

    print(
        f"Hallucination         : "
        f"{data['hallucination']}"
    )

    print(
        f"Response Time         : "
        f"{data['response_time']:.2f} ms"
    )

    print(
        f"Result                : "
        f"{'PASS' if data['passed'] else 'FAIL'}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("CAUSAL RAG DATASET EVALUATION")
    print("=" * 70)
    print()

    if not DATASET_PATH.exists():

        print(
            f"ERROR: Dataset not found:\n"
            f"{DATASET_PATH}"
        )

        return

    try:

        with open(
            DATASET_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            dataset = json.load(file)

    except json.JSONDecodeError as error:

        print(
            f"ERROR: Invalid JSON dataset:\n"
            f"{error}"
        )

        return

    if isinstance(dataset, dict):

        scenarios = dataset.get(
            "scenarios",
            dataset.get(
                "test_cases",
                dataset.get(
                    "cases",
                    []
                )
            )
        )

    elif isinstance(dataset, list):

        scenarios = dataset

    else:

        scenarios = []

    if not scenarios:

        print(
            "ERROR: No scenarios found "
            "in dataset."
        )

        return

    print(
        f"Total Scenarios: "
        f"{len(scenarios)}"
    )

    results = []

    for index, scenario in enumerate(
        scenarios,
        start=1
    ):

        result = evaluate_scenario(
            scenario,
            index
        )

        results.append(
            result
        )

        print_scenario_result(
            result
        )

    total = len(results)

    passed = sum(
        1
        for result in results
        if result["passed"]
    )

    failed = total - passed

    def average(key):

        if not results:
            return 0.0

        return (
            sum(
                result[key]
                for result in results
            )
            / len(results)
        )

    overall_accuracy = (
        passed
        / total
        * 100
        if total
        else 0
    )

    print()
    print("=" * 70)
    print("FINAL DATASET RESULTS")
    print("=" * 70)
    print()

    print(
        f"Total Scenarios : "
        f"{total}"
    )

    print(
        f"Passed          : "
        f"{passed}"
    )

    print(
        f"Failed          : "
        f"{failed}"
    )

    print(
        f"Overall Accuracy: "
        f"{overall_accuracy:.2f}%"
    )

    print()
    print("-" * 70)
    print("CAUSAL RAG EVALUATION METRICS")
    print("-" * 70)
    print()

    print(
        f"Causal Extraction Accuracy : "
        f"{average('extraction_accuracy'):.2f}%"
    )

    print(
        f"Causal Relation Accuracy  : "
        f"{average('relation_accuracy'):.2f}%"
    )

    print(
        f"Confidence Accuracy        : "
        f"{average('confidence_accuracy'):.2f}%"
    )

    print(
        f"Evidence Strength Accuracy : "
        f"{average('evidence_accuracy'):.2f}%"
    )

    print(
        f"Causal Chain Accuracy      : "
        f"{average('chain_accuracy'):.2f}%"
    )

    print(
        f"Evidence Faithfulness      : "
        f"{average('faithfulness'):.2f}%"
    )

    print(
        f"Alternative Cause Accuracy : "
        f"{average('alternative_accuracy'):.2f}%"
    )

    print(
        f"Answer Accuracy            : "
        f"{average('answer_accuracy'):.2f}%"
    )

    hallucinations = sum(
        1
        for result in results
        if result["hallucination"]
        == "YES"
    )

    hallucination_rate = (
        hallucinations
        / total
        * 100
        if total
        else 0
    )

    print(
        f"Causal Hallucination Rate  : "
        f"{hallucination_rate:.2f}%"
    )

    print(
        f"Average Response Time      : "
        f"{average('response_time'):.2f} ms"
    )

    print()
    print("-" * 70)
    print("RESULTS BY SCENARIO TYPE")
    print("-" * 70)

    scenario_types = [
        "DIRECT_CAUSE",
        "MULTI_STEP_CAUSE",
        "CORRELATION_ONLY",
        "MULTIPLE_POSSIBLE_CAUSES",
        "INSUFFICIENT_EVIDENCE",
    ]

    for scenario_type in scenario_types:

        type_results = [
            result
            for result in results
            if result["scenario_type"]
            == scenario_type
        ]

        type_total = len(
            type_results
        )

        type_passed = sum(
            1
            for result in type_results
            if result["passed"]
        )

        type_accuracy = (
            type_passed
            / type_total
            * 100
            if type_total
            else 0
        )

        print(
            f"{scenario_type:<25}"
            f"{type_passed}/{type_total} "
            f"({type_accuracy:.2f}%)"
        )

    print()
    print("-" * 70)
    print("EVALUATION CONCLUSION")
    print("-" * 70)
    print()

    if overall_accuracy >= 90:

        print(
            "The Causal RAG system demonstrates "
            "strong causal reasoning performance "
            "across the test dataset."
        )

    elif overall_accuracy >= 70:

        print(
            "The Causal RAG system demonstrates "
            "good causal reasoning performance "
            "but requires some further improvement."
        )

    else:

        print(
            "The Causal RAG system requires further "
            "improvement in causal reasoning and "
            "evidence evaluation."
        )

    print()
    print("=" * 70)
    print(
        "CAUSAL RAG DATASET EVALUATION COMPLETE"
    )
    print("=" * 70)
    print()


# ============================================================
# PROGRAM ENTRY
# ============================================================

if __name__ == "__main__":
    main()