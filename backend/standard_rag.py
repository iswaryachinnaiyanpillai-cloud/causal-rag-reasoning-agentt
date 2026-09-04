# ============================================================
# STANDARD RAG BASELINE
# Causal RAG Agent
# TechNova Solutions
# ============================================================

from backend.rag import (
    retrieve_company_info,
    retrieve_causal_evidence
)


# ============================================================
# STANDARD RAG ANSWER
# ============================================================

def standard_rag_answer(question: str):

    question = question.strip()

    if not question:
        return {
            "success": False,
            "question": "",
            "answer": "Please provide a question.",
            "retrieved_evidence": ""
        }

    # --------------------------------------------------------
    # Detect whether the question is causal
    # --------------------------------------------------------

    causal_keywords = [
        "why",
        "cause",
        "caused",
        "causing",
        "reason",
        "responsible",
        "because",
        "factor",
        "contributed",
        "led to",
        "resulted in"
    ]

    is_causal = any(
        keyword in question.lower()
        for keyword in causal_keywords
    )

    # --------------------------------------------------------
    # Standard RAG retrieval
    #
    # Factual question -> company knowledge
    # Causal question  -> causal knowledge
    # --------------------------------------------------------

    if is_causal:
        retrieved_evidence = retrieve_causal_evidence(question)
    else:
        retrieved_evidence = retrieve_company_info(question)

    # --------------------------------------------------------
    # Generate simple Standard RAG answer
    # --------------------------------------------------------

    if retrieved_evidence:

        answer = (
            "Based on the retrieved information "
            "from the knowledge base:\n\n"
            + retrieved_evidence
        )

    else:

        answer = (
            "No relevant information was found "
            "in the knowledge base."
        )

    return {
        "success": True,
        "question": question,
        "answer": answer,
        "retrieved_evidence": retrieved_evidence
    }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    test_questions = [

        "What services does TechNova provide?",

        "Why did system latency increase?",

        "What caused the decrease in model accuracy?",

        "What caused the slower API requests?"
    ]

    print("\n" + "=" * 70)
    print("STANDARD RAG BASELINE TEST")
    print("=" * 70)

    for question in test_questions:

        print("\n" + "-" * 70)

        print("QUESTION:")
        print(question)

        result = standard_rag_answer(question)

        print("\nANSWER:")
        print(result["answer"])

        print("\nRETRIEVED EVIDENCE:")
        print(result["retrieved_evidence"])

    print("\n" + "=" * 70)
    print("STANDARD RAG TEST COMPLETE")
    print("=" * 70)