# ============================================================
# CAUSAL RAG AGENT
# AUTOMATED TEST RUNNER
# TechNova Solutions
# ============================================================

import json

from backend.causal_analyzer import analyze_query


# ============================================================
# LOAD TEST DATASET
# ============================================================

with open(
    "data/causal_test_dataset.json",
    "r",
    encoding="utf-8"
) as file:
    dataset = json.load(file)


# ============================================================
# EXTRACT SCENARIOS
# ============================================================

test_cases = dataset.get("scenarios", [])


if not isinstance(test_cases, list):
    raise ValueError(
        "Invalid dataset format: 'scenarios' must be a list."
    )


# ============================================================
# TEST COUNTERS
# ============================================================

total_tests = len(test_cases)
passed_tests = 0


print("\n")
print("=" * 70)
print("        CAUSAL RAG AGENT - AUTOMATED EVALUATION")
print("=" * 70)
print()


# ============================================================
# RUN TESTS
# ============================================================

for test in test_cases:

    test_id = test.get("id", "UNKNOWN")
    question = test.get("question", "")

    expected_status = test.get(
        "expected_causal_status",
        "UNKNOWN"
    )

    expected_evidence = test.get(
        "expected_evidence_strength",
        "UNKNOWN"
    )

    print("-" * 70)
    print(f"TEST {test_id}")
    print(f"Question: {question}")
    print("-" * 70)

    try:

        # ----------------------------------------------------
        # RUN CAUSAL ANALYZER
        # ----------------------------------------------------

        result = analyze_query(question)


        # ----------------------------------------------------
        # EXTRACT ACTUAL RESULTS
        # ----------------------------------------------------

        actual_status = result.get(
            "causal_verification",
            {}
        ).get(
            "status",
            "UNKNOWN"
        )

        actual_evidence = result.get(
            "evidence_evaluation",
            {}
        ).get(
            "strength",
            "UNKNOWN"
        )


        # ----------------------------------------------------
        # CHECK EXPECTED RESULTS
        # ----------------------------------------------------

        status_pass = (
            actual_status == expected_status
        )

        evidence_pass = (
            actual_evidence == expected_evidence
        )


        # ----------------------------------------------------
        # FINAL TEST RESULT
        # ----------------------------------------------------

        test_passed = (
            status_pass
            and evidence_pass
        )


        if test_passed:

            passed_tests += 1

            print("Expected Status   :", expected_status)
            print("Actual Status     :", actual_status)
            print("Expected Evidence :", expected_evidence)
            print("Actual Evidence   :", actual_evidence)
            print("RESULT            : PASS ✅")

        else:

            print("Expected Status   :", expected_status)
            print("Actual Status     :", actual_status)
            print("Expected Evidence :", expected_evidence)
            print("Actual Evidence   :", actual_evidence)
            print("RESULT            : FAIL ❌")


    except Exception as e:

        print("RESULT            : ERROR ❌")
        print("Error             :", str(e))


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 70)
print("                    TEST SUMMARY")
print("=" * 70)

print(f"Total Tests : {total_tests}")
print(f"Passed      : {passed_tests}")
print(f"Failed      : {total_tests - passed_tests}")

if total_tests > 0:

    pass_rate = (
        passed_tests / total_tests
    ) * 100

    print(
        f"Pass Rate   : {pass_rate:.2f}%"
    )

else:

    print("Pass Rate   : 0.00%")


print("=" * 70)
print()