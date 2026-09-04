# ============================================================
# FASTAPI MAIN APPLICATION
# Causal RAG Reasoning Agent
# TechNova Solutions
# ============================================================

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.standard_rag import standard_rag_answer
from backend.causal_analyzer import analyze_query


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Causal RAG Reasoning Agent",
    description="Causal RAG Agent for TechNova Solutions",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# FRONTEND
# ============================================================

frontend_path = Path(__file__).parent / "frontend"

if frontend_path.exists():
    app.mount(
        "/frontend",
        StaticFiles(
            directory=str(frontend_path),
            html=True,
        ),
        name="frontend",
    )


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Causal RAG Agent is running!",
        "company": "TechNova Solutions",
        "status": "online",
    }


# ============================================================
# HEALTH ENDPOINT
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


# ============================================================
# ASK ENDPOINT
# ============================================================

@app.get("/ask")
def ask(question: str):

    try:

        # ====================================================
        # VALIDATE QUESTION
        # ====================================================

        question = question.strip()

        if not question:

            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Please provide a question.",
                },
            )

        # ====================================================
        # STANDARD RAG
        # ====================================================

        standard_result = standard_rag_answer(
            question
        )

        if not standard_result.get(
            "success",
            False,
        ):

            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": (
                        "Standard RAG retrieval failed."
                    ),
                },
            )

        standard_evidence = (
            standard_result.get(
                "retrieved_evidence",
                "",
            )
        )

        # ====================================================
        # CAUSAL ANALYSIS
        # ====================================================

        analysis = analyze_query(
            question
        )

        if not analysis.get(
            "success",
            False,
        ):

            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": analysis.get(
                        "error",
                        "Causal analysis failed.",
                    ),
                },
            )

        # ====================================================
        # QUERY TYPE
        # ====================================================

        query_type = analysis.get(
            "query_type",
            "CAUSAL",
        )

        # ====================================================
        # FACTUAL QUERY
        # ====================================================

        if query_type == "FACTUAL":

            return {
                "success": True,

                "question": question,

                "query_type": "FACTUAL",

                "answer": standard_result.get(
                    "answer",
                    analysis.get(
                        "answer",
                        "",
                    ),
                ),

                "retrieved_evidence": (
                    standard_evidence
                ),

                "causal_information": {},

                "claims": [],

                "cause_effect_relationships": [],

                "causal_chain": [],

                "causal_graph": {
                    "success": True,
                    "nodes": [],
                    "edges": [],
                    "node_count": 0,
                    "edge_count": 0,
                },

                "evidence_evaluation": {},

                "causal_verification": {},

                "causal_reasoning": {},

                # Keep BOTH names for compatibility.
                "evaluation": {},

                "overall_evaluation": {},

                "evaluation_summary": "",
            }

        # ====================================================
        # CAUSAL INFORMATION
        # ====================================================

        causal_information = analysis.get(
            "causal_information",
            {},
        )

        # ====================================================
        # CAUSAL CHAIN
        # ====================================================

        causal_chain = analysis.get(
            "causal_chain",
            [],
        )

        if isinstance(
            causal_chain,
            list,
        ):

            clean_chain = [
                str(item).strip()
                for item in causal_chain
                if item is not None
                and str(item).strip()
            ]

        else:

            clean_chain = []

        # ====================================================
        # CAUSAL GRAPH
        #
        # IMPORTANT:
        # Use the graph produced by analyze_query().
        # Do not rebuild it here.
        # ====================================================

        causal_graph = analysis.get(
            "causal_graph",
            {},
        )

        if not isinstance(
            causal_graph,
            dict,
        ):

            causal_graph = {
                "success": True,
                "nodes": [],
                "edges": [],
                "node_count": 0,
                "edge_count": 0,
            }

        # ====================================================
        # EVIDENCE EVALUATION
        # ====================================================

        evidence_evaluation = analysis.get(
            "evidence_evaluation",
            {},
        )

        if not isinstance(
            evidence_evaluation,
            dict,
        ):

            evidence_evaluation = {}

        # ====================================================
        # CAUSAL VERIFICATION
        # ====================================================

        causal_verification = analysis.get(
            "causal_verification",
            {},
        )

        if not isinstance(
            causal_verification,
            dict,
        ):

            causal_verification = {}

        # ====================================================
        # CAUSAL REASONING
        # ====================================================

        causal_reasoning = analysis.get(
            "causal_reasoning",
            {},
        )

        if not isinstance(
            causal_reasoning,
            dict,
        ):

            causal_reasoning = {}

        # ====================================================
        # OVERALL EVALUATION
        #
        # THIS IS THE IMPORTANT FIX.
        # ====================================================

        overall_evaluation = analysis.get(
            "overall_evaluation",
            {},
        )

        if not isinstance(
            overall_evaluation,
            dict,
        ):

            overall_evaluation = {}

        # Keep "evaluation" as an alias too, because your
        # existing frontend may still read this key.
        evaluation = overall_evaluation

        # ====================================================
        # EVALUATION SUMMARY
        # ====================================================

        evaluation_summary = analysis.get(
            "evaluation_summary",
            "",
        )

        if not evaluation_summary:

            evaluation_summary = (
                overall_evaluation.get(
                    "evaluation_summary",
                    "",
                )
            )

        # ====================================================
        # CAUSAL RESPONSE
        # ====================================================

        return {

            "success": True,

            "question": question,

            "query_type": query_type,

            "scenario": analysis.get(
                "scenario",
                0,
            ),

            "scenario_title": analysis.get(
                "scenario_title",
                "",
            ),

            # ------------------------------------------------
            # FINAL ANSWER
            # ------------------------------------------------

            "answer": analysis.get(
                "answer",
                "",
            ),

            # ------------------------------------------------
            # RETRIEVED EVIDENCE
            # ------------------------------------------------

            "retrieved_evidence": analysis.get(
                "retrieved_evidence",
                "",
            ),

            # ------------------------------------------------
            # CAUSAL INFORMATION
            # ------------------------------------------------

            "causal_information": (
                causal_information
            ),

            # ------------------------------------------------
            # CLAIMS
            # ------------------------------------------------

            "claims": analysis.get(
                "claims",
                [],
            ),

            # ------------------------------------------------
            # CAUSE-EFFECT RELATIONSHIPS
            # ------------------------------------------------

            "cause_effect_relationships": (
                analysis.get(
                    "cause_effect_relationships",
                    [],
                )
            ),

            # ------------------------------------------------
            # CAUSAL CHAIN
            # ------------------------------------------------

            "causal_chain": clean_chain,

            "causal_chain_length": len(
                clean_chain
            ),

            # ------------------------------------------------
            # CAUSAL GRAPH
            # ------------------------------------------------

            "causal_graph": causal_graph,

            # ------------------------------------------------
            # EVIDENCE EVALUATION
            # ------------------------------------------------

            "evidence_evaluation": (
                evidence_evaluation
            ),

            # ------------------------------------------------
            # VERIFICATION
            # ------------------------------------------------

            "causal_verification": (
                causal_verification
            ),

            # ------------------------------------------------
            # REASONING
            # ------------------------------------------------

            "causal_reasoning": (
                causal_reasoning
            ),

            # ------------------------------------------------
            # OVERALL EVALUATION
            # ------------------------------------------------

            "overall_evaluation": (
                overall_evaluation
            ),

            # Frontend compatibility alias
            "evaluation": evaluation,

            # ------------------------------------------------
            # EVALUATION SUMMARY
            # ------------------------------------------------

            "evaluation_summary": (
                evaluation_summary
            ),

            # ------------------------------------------------
            # STATUS SHORTCUTS
            # ------------------------------------------------

            "causal_status": analysis.get(
                "causal_status",
                causal_information.get(
                    "status",
                    "",
                ),
            ),

            "evidence_strength": analysis.get(
                "evidence_strength",
                causal_information.get(
                    "evidence_strength",
                    "",
                ),
            ),

            "confidence": analysis.get(
                "confidence",
                causal_information.get(
                    "confidence",
                    "",
                ),
            ),

            # ------------------------------------------------
            # MODULE STATUS
            # ------------------------------------------------

            "modules": analysis.get(
                "modules",
                {},
            ),
        }

    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as e:

        import traceback

        print("\n" + "=" * 70)
        print("ERROR IN /ask")
        print("=" * 70)

        traceback.print_exc()

        print("=" * 70 + "\n")

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
            },
        )