# ============================================================
# RAG RETRIEVAL MODULE
# Causal RAG Agent
# TechNova Solutions
# ============================================================

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

import chromadb


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

DATA_DIR = BASE_DIR / "data"

CAUSAL_DATA_FILE = (
    DATA_DIR / "causal_data.txt"
)

CHROMA_DIR = (
    BASE_DIR / "chroma_db"
)


# ============================================================
# CHROMA DATABASE
# ============================================================

CHROMA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

company_collection = (
    client.get_or_create_collection(
        name="company_info"
    )
)

causal_collection = (
    client.get_or_create_collection(
        name="causal_evidence"
    )
)

document_collection = (
    client.get_or_create_collection(
        name="technova_documents"
    )
)


# ============================================================
# TEXT UTILITIES
# ============================================================

def clean_text(text: str) -> str:
    """
    Normalize whitespace while preserving readable content.
    """

    if not text:
        return ""

    text = str(text)

    text = text.replace(
        "\r\n",
        "\n"
    )

    text = text.replace(
        "\r",
        "\n"
    )

    lines = []

    for line in text.split("\n"):

        line = line.strip()

        if line:

            lines.append(
                line
            )

    return "\n".join(
        lines
    ).strip()


def normalize_text(text: str) -> str:
    """
    Normalize text for keyword matching.
    """

    if not text:
        return ""

    text = str(text).lower()

    text = text.replace(
        "→",
        "->"
    )

    text = text.replace(
        "➜",
        "->"
    )

    text = text.replace(
        "=>",
        "->"
    )

    text = re.sub(
        r"[^a-z0-9\s\-\>]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def contains_any(
    text: str,
    keywords: List[str]
) -> bool:
    """
    Return True when any keyword is present.
    """

    if not keywords:
        return False

    normalized = normalize_text(
        text
    )

    return any(
        normalize_text(keyword)
        in normalized
        for keyword in keywords
    )


# ============================================================
# LOAD CAUSAL DATA
# ============================================================

def load_causal_data() -> str:
    """
    Load causal_data.txt.
    """

    if not CAUSAL_DATA_FILE.exists():

        return ""

    try:

        return CAUSAL_DATA_FILE.read_text(
            encoding="utf-8"
        )

    except Exception as error:

        print(
            "Error loading causal data:",
            error
        )

        return ""


# ============================================================
# SPLIT SCENARIOS
# ============================================================

def split_scenarios(
    text: str
) -> List[str]:
    """
    Split causal_data.txt into scenario blocks.

    Supports headings such as:

        SCENARIO 1:
        SCENARIO 1 -
        SCENARIO 1
    """

    if not text:
        return []

    text = str(text)

    matches = list(
        re.finditer(
            r"(?im)^\s*SCENARIO\s+(\d+)\s*[:\-]?",
            text
        )
    )

    scenarios: List[str] = []

    for index, match in enumerate(matches):

        start = match.start()

        if (
            index + 1
            < len(matches)
        ):

            end = matches[
                index + 1
            ].start()

        else:

            end = len(text)

        scenario = text[
            start:end
        ].strip()

        if scenario:

            scenarios.append(
                scenario
            )

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    if not scenarios and text.strip():

        scenarios.append(
            text.strip()
        )

    return scenarios


def get_scenarios() -> List[str]:
    """
    Return all causal scenarios.
    """

    data = load_causal_data()

    return split_scenarios(
        data
    )


# ============================================================
# SCENARIO HELPERS
# ============================================================

def get_scenario_number(
    text: str
) -> str:
    """
    Extract scenario number from text.
    """

    if not text:
        return ""

    match = re.search(
        r"(?i)SCENARIO\s+(\d+)",
        str(text)
    )

    if match:

        return match.group(1)

    return ""


def get_scenario_by_number(
    scenarios: List[str],
    number: str
) -> str:
    """
    Return a scenario by its number.
    """

    target = str(
        number
    ).strip()

    for scenario in scenarios:

        if (
            get_scenario_number(
                scenario
            )
            == target
        ):

            return scenario

    return ""


def get_legacy_scenario_by_number(
    number: str
) -> str:
    """
    Retrieve a scenario from the legacy Chroma collection.
    """

    target = str(
        number
    ).strip()

    # --------------------------------------------------------
    # String metadata
    # --------------------------------------------------------

    try:

        result = (
            causal_collection.get(
                where={
                    "scenario": target
                }
            )
        )

        documents = result.get(
            "documents",
            []
        )

        if documents:

            return documents[0]

    except Exception:
        pass

    # --------------------------------------------------------
    # Integer metadata
    # --------------------------------------------------------

    try:

        result = (
            causal_collection.get(
                where={
                    "scenario": int(
                        target
                    )
                }
            )
        )

        documents = result.get(
            "documents",
            []
        )

        if documents:

            return documents[0]

    except Exception:
        pass

    return ""


def retrieve_known_scenario(
    number: str
) -> str:
    """
    Retrieve a known scenario from causal_data.txt first,
    then the legacy ChromaDB collection.
    """

    scenarios = get_scenarios()

    scenario = (
        get_scenario_by_number(
            scenarios,
            number
        )
    )

    if scenario:

        return scenario

    return (
        get_legacy_scenario_by_number(
            number
        )
    )


# ============================================================
# SCENARIO CHECK
# ============================================================

def scenario_has(
    text: str,
    *terms: str
) -> bool:
    """
    Return True when all supplied terms occur.
    """

    normalized = normalize_text(
        text
    )

    return all(
        normalize_text(term)
        in normalized
        for term in terms
    )


# ============================================================
# INITIALIZE LEGACY CAUSAL COLLECTION
# ============================================================

def initialize_causal_collection() -> None:
    """
    Initialize the legacy causal_evidence collection.
    """

    scenarios = get_scenarios()

    if not scenarios:

        print(
            "Warning: No causal scenarios found."
        )

        return

    existing_ids = set()

    try:

        existing = (
            causal_collection.get()
        )

        for item_id in (
            existing.get(
                "ids",
                []
            )
        ):

            existing_ids.add(
                item_id
            )

    except Exception:
        pass

    for scenario in scenarios:

        scenario_number = (
            get_scenario_number(
                scenario
            )
        )

        if not scenario_number:
            continue

        scenario_id = (
            f"scenario_{scenario_number}"
        )

        if scenario_id in existing_ids:
            continue

        try:

            causal_collection.add(

                ids=[
                    scenario_id
                ],

                documents=[
                    scenario
                ],

                metadatas=[
                    {
                        "scenario":
                            scenario_number,

                        "type":
                            "causal_evidence"
                    }
                ]
            )

        except Exception as error:

            print(
                "Chroma initialization warning:",
                error
            )


initialize_causal_collection()


# ============================================================
# COMPANY INFORMATION
# ============================================================

def get_company_information() -> str:
    """
    Read company information from the data directory.
    """

    possible_files = [

        DATA_DIR /
        "company_info.txt",

        DATA_DIR /
        "company_info.md",

        DATA_DIR /
        "company.txt"

    ]

    for file_path in possible_files:

        if file_path.exists():

            try:

                return clean_text(
                    file_path.read_text(
                        encoding="utf-8"
                    )
                )

            except Exception:
                pass

    return (
        "TechNova Solutions is a technology company "
        "working in software development, cloud computing, "
        "artificial intelligence, data analytics and web development."
    )


# ============================================================
# COMPANY INFORMATION RETRIEVAL
# ============================================================

def retrieve_company_info(
    question: str
) -> str:
    """
    Retrieve relevant company information.
    """

    question = clean_text(
        question
    )

    if not question:
        return ""

    information = (
        get_company_information()
    )

    if not information:
        return ""

    q = normalize_text(
        question
    )

    # --------------------------------------------------------
    # SERVICES
    # --------------------------------------------------------

    if contains_any(
        q,
        [
            "service",
            "services",
            "what does technova provide",
            "what services",
            "technova provide"
        ]
    ):

        match = re.search(
            r"Services:\s*(.*?)(?=\nMission:|\nContact:|\Z)",
            information,
            flags=(
                re.IGNORECASE |
                re.DOTALL
            )
        )

        if match:

            services = clean_text(
                match.group(1)
            )

            return (
                "TechNova Solutions provides "
                "the following services:\n"
                + services
            )

    # --------------------------------------------------------
    # ABOUT
    # --------------------------------------------------------

    if contains_any(
        q,
        [
            "about technova",
            "what is technova",
            "about the company",
            "company information"
        ]
    ):

        match = re.search(
            r"About:\s*(.*?)(?=\nServices:|\nMission:|\nContact:|\Z)",
            information,
            flags=(
                re.IGNORECASE |
                re.DOTALL
            )
        )

        if match:

            return clean_text(
                match.group(1)
            )

    # --------------------------------------------------------
    # MISSION
    # --------------------------------------------------------

    if contains_any(
        q,
        [
            "mission",
            "company mission",
            "technova mission"
        ]
    ):

        match = re.search(
            r"Mission:\s*(.*?)(?=\nContact:|\Z)",
            information,
            flags=(
                re.IGNORECASE |
                re.DOTALL
            )
        )

        if match:

            return clean_text(
                match.group(1)
            )

    # --------------------------------------------------------
    # CONTACT
    # --------------------------------------------------------

    if contains_any(
        q,
        [
            "contact",
            "email",
            "phone",
            "website"
        ]
    ):

        match = re.search(
            r"Contact:\s*(.*)$",
            information,
            flags=(
                re.IGNORECASE |
                re.DOTALL
            )
        )

        if match:

            return clean_text(
                match.group(1)
            )

    # --------------------------------------------------------
    # GENERAL FALLBACK
    # --------------------------------------------------------

    return information


# ============================================================
# DETERMINISTIC CAUSAL RETRIEVAL
# ============================================================

def deterministic_causal_retrieval(
    question: str
) -> str:
    """
    Deterministic retrieval for the known TechNova scenarios.

    IMPORTANT:
    Database traffic + system latency questions are handled
    before the generic social-media Scenario 3 so they cannot
    retrieve the wrong evidence.
    """

    question_normalized = normalize_text(
        question
    )

    if not question_normalized:
        return ""

    # ========================================================
    # SCENARIO 1
    #
    # DATABASE OVERLOAD -> PRODUCTION SYSTEM FAILURE
    # ========================================================

    if (
        "system failure"
        in question_normalized
        or "production system failed"
        in question_normalized
        or "production failure"
        in question_normalized
        or (
            "what caused"
            in question_normalized
            and "failure"
            in question_normalized
        )
    ):

        scenario = (
            retrieve_known_scenario(
                "1"
            )
        )

        if scenario:

            return scenario

    # ========================================================
    # DATABASE TRAFFIC + SYSTEM LATENCY
    #
    # MUST COME BEFORE SCENARIO 3.
    # ========================================================

    database_latency_question = (
        contains_any(
            question_normalized,
            [
                "database traffic",
                "database load"
            ]
        )
        and contains_any(
            question_normalized,
            [
                "system latency",
                "latency"
            ]
        )
    )

    if database_latency_question:

        # ----------------------------------------------------
        # CORRELATION / DID-CAUSE QUESTION
        # ----------------------------------------------------

        if contains_any(
            question_normalized,
            [
                "relationship",
                "correlation",
                "correlational",
                "responsible",
                "associated",
                "did",
                "cause",
                "caused"
            ]
        ):

            # IMPORTANT:
            # In the current causal_data.txt, the dedicated
            # database-latency correlation evidence is stored
            # under Scenario 11.
            scenario = (
                retrieve_known_scenario(
                    "11"
                )
            )

            if scenario:

                return scenario

    # ========================================================
    # SCENARIO 2
    #
    # MULTI-STEP SYSTEM LATENCY
    # ========================================================

    if contains_any(
        question_normalized,
        [
            "why did system latency increase",
            "why did latency increase",
            "system latency increased"
        ]
    ):

        scenario = (
            retrieve_known_scenario(
                "2"
            )
        )

        if scenario:

            return scenario

    # ========================================================
    # SCENARIO 5
    #
    # MODEL ACCURACY
    # ========================================================

    if contains_any(
        question_normalized,
        [
            "model accuracy",
            "accuracy decreased",
            "accuracy decrease",
            "machine learning model",
            "training data noise",
            "noisy training data"
        ]
    ):

        scenario = (
            retrieve_known_scenario(
                "5"
            )
        )

        if scenario:

            return scenario

    # ========================================================
    # SCENARIO 6
    #
    # SERVER RESOURCE ISSUE
    # ========================================================

    if contains_any(
        question_normalized,
        [
            "server resources",
            "reduced server resources",
            "cpu utilization",
            "memory pressure"
        ]
    ):

        scenario = (
            retrieve_known_scenario(
                "6"
            )
        )

        if scenario:

            return scenario

    # ========================================================
    # SCENARIO 7
    #
    # NETWORK CONGESTION
    # ========================================================

    if contains_any(
        question_normalized,
        [
            "network congestion",
            "packet delay",
            "bandwidth utilization",
            "network response time",
            "api requests became slower",
            "api requests slower",
            "api request slower",
            "slower api requests",
            "slower api"
        ]
    ):

        scenario = (
            retrieve_known_scenario(
                "7"
            )
        )

        if scenario:

            return scenario

    # ========================================================
    # SCENARIO 8
    #
    # INSUFFICIENT EVIDENCE
    # ========================================================

    if contains_any(
        question_normalized,
        [
            "employee productivity",
            "productivity decreased",
            "employee performance"
        ]
    ):

        scenario = (
            retrieve_known_scenario(
                "8"
            )
        )

        if scenario:

            return scenario

    # ========================================================
    # SCENARIO 9
    #
    # DATABASE QUERY PERFORMANCE
    # ========================================================

    if (
        contains_any(
            question_normalized,
            [
                "database query",
                "query execution",
                "query execution time",
                "query performance",
                "database performance"
            ]
        )
        and not contains_any(
            question_normalized,
            [
                "system latency"
            ]
        )
    ):

        scenario = (
            retrieve_known_scenario(
                "9"
            )
        )

        if scenario:

            return scenario

    # ========================================================
    # SCENARIO 10
    #
    # CACHE FAILURE
    # ========================================================

    if contains_any(
        question_normalized,
        [
            "cache failure",
            "cache effectiveness",
            "cache hit rate",
            "cache failed"
        ]
    ):

        scenario = (
            retrieve_known_scenario(
                "10"
            )
        )

        if scenario:

            return scenario

    # ========================================================
    # SCENARIO 4
    #
    # MULTIPLE POSSIBLE CAUSES
    # ========================================================

    if (
        "response time"
        in question_normalized
        and (
            "most likely"
            in question_normalized
            or "what factor"
            in question_normalized
            or "factor"
            in question_normalized
        )
    ):

        scenario = (
            retrieve_known_scenario(
                "4"
            )
        )

        if scenario:

            return scenario

    # ========================================================
    # SCENARIO 3
    #
    # SOCIAL MEDIA / WEBSITE TRAFFIC
    #
    # This is deliberately checked AFTER database-latency
    # questions so Scenario 3 cannot steal those requests.
    # ========================================================

    if (
        contains_any(
            question_normalized,
            [
                "social media activity",
                "social media",
                "website traffic"
            ]
        )
        and contains_any(
            question_normalized,
            [
                "cause",
                "caused",
                "responsible",
                "relationship",
                "causation"
            ]
        )
    ):

        scenario = (
            retrieve_known_scenario(
                "3"
            )
        )

        if scenario:

            return scenario

    # ========================================================
    # GENERAL SERVER/APPLICATION PERFORMANCE
    # ========================================================

    performance_question = contains_any(
        question_normalized,
        [
            "server performance",
            "application performance",
            "performance decrease",
            "performance decreased",
            "application became slow",
            "application become slow",
            "system performance"
        ]
    )

    if (
        performance_question
        and contains_any(
            question_normalized,
            [
                "why",
                "cause",
                "caused",
                "reason",
                "factor",
                "responsible",
                "what caused"
            ]
        )
        and not contains_any(
            question_normalized,
            [
                "accuracy",
                "model accuracy",
                "database query",
                "cache"
            ]
        )
    ):

        scenario = (
            retrieve_known_scenario(
                "4"
            )
        )

        if scenario:

            return scenario

    return ""


# ============================================================
# SEMANTIC DOCUMENT RETRIEVAL
# ============================================================

def semantic_document_retrieval(
    question: str
) -> str:
    """
    Semantic retrieval from technova_documents.
    """

    question = clean_text(
        question
    )

    if not question:
        return ""

    try:

        count = (
            document_collection.count()
        )

        if count == 0:
            return ""

        result = (
            document_collection.query(
                query_texts=[
                    question
                ],
                n_results=min(
                    3,
                    count
                )
            )
        )

        documents = result.get(
            "documents",
            [[]]
        )

        if (
            not documents
            or not documents[0]
        ):

            return ""

        retrieved_documents = []

        for document in documents[0]:

            if (
                document
                and document
                not in retrieved_documents
            ):

                retrieved_documents.append(
                    document
                )

        if not retrieved_documents:
            return ""

        return (
            "\n\n"
            "--- RETRIEVED KNOWLEDGE CHUNK ---"
            "\n\n"
            .join(
                retrieved_documents
            )
        )

    except Exception as error:

        print(
            "Semantic document retrieval warning:",
            error
        )

        return ""


# ============================================================
# LEGACY SEMANTIC RETRIEVAL
# ============================================================

def semantic_causal_retrieval(
    question: str
) -> str:
    """
    Semantic fallback from causal_evidence.
    """

    question = clean_text(
        question
    )

    if not question:
        return ""

    try:

        count = (
            causal_collection.count()
        )

        if count == 0:
            return ""

        result = (
            causal_collection.query(
                query_texts=[
                    question
                ],
                n_results=min(
                    3,
                    count
                )
            )
        )

        documents = result.get(
            "documents",
            [[]]
        )

        if (
            not documents
            or not documents[0]
        ):

            return ""

        candidates = documents[0]

        question_normalized = (
            normalize_text(
                question
            )
        )

        # ----------------------------------------------------
        # Scenario 1 protection
        # ----------------------------------------------------

        if (
            "system failure"
            in question_normalized
            or (
                "what caused"
                in question_normalized
                and "failure"
                in question_normalized
            )
        ):

            for document in candidates:

                normalized_document = (
                    normalize_text(
                        document
                    )
                )

                if (
                    "system failure"
                    in normalized_document
                    and (
                        "database overload"
                        in normalized_document
                        or "database"
                        in normalized_document
                    )
                ):

                    return document

        # ----------------------------------------------------
        # Model accuracy
        # ----------------------------------------------------

        if (
            "model accuracy"
            in question_normalized
        ):

            for document in candidates:

                normalized_document = (
                    normalize_text(
                        document
                    )
                )

                if (
                    "model accuracy"
                    in normalized_document
                ):

                    return document

        # ----------------------------------------------------
        # Network
        # ----------------------------------------------------

        if (
            "network"
            in question_normalized
            and "api"
            in question_normalized
        ):

            for document in candidates:

                normalized_document = (
                    normalize_text(
                        document
                    )
                )

                if (
                    "network congestion"
                    in normalized_document
                ):

                    return document

        return candidates[0]

    except Exception as error:

        print(
            "Legacy semantic retrieval warning:",
            error
        )

        return ""


# ============================================================
# MAIN CAUSAL RETRIEVAL
# ============================================================

def retrieve_causal_evidence(
    question: str
) -> str:
    """
    Main causal retrieval pipeline.

    Priority:

        1. Deterministic known-scenario retrieval
        2. Semantic final knowledge-base retrieval
        3. Legacy causal retrieval
        4. Empty result
    """

    question = clean_text(
        question
    )

    if not question:
        return ""

    # --------------------------------------------------------
    # 1. Deterministic retrieval
    # --------------------------------------------------------

    deterministic_result = (
        deterministic_causal_retrieval(
            question
        )
    )

    if deterministic_result:

        return deterministic_result

    # --------------------------------------------------------
    # 2. Final ChromaDB retrieval
    # --------------------------------------------------------

    semantic_document_result = (
        semantic_document_retrieval(
            question
        )
    )

    if semantic_document_result:

        return semantic_document_result

    # --------------------------------------------------------
    # 3. Legacy retrieval
    # --------------------------------------------------------

    semantic_result = (
        semantic_causal_retrieval(
            question
        )
    )

    if semantic_result:

        return semantic_result

    return ""


# ============================================================
# GENERIC INFORMATION RETRIEVAL
# ============================================================

def retrieve_information(
    question: str
) -> Dict[str, Any]:
    """
    Retrieve both company information and causal evidence.
    """

    question = clean_text(
        question
    )

    if not question:

        return {
            "success": False,
            "question": "",
            "company_info": "",
            "causal_evidence": ""
        }

    company_info = (
        retrieve_company_info(
            question
        )
    )

    causal_evidence = (
        retrieve_causal_evidence(
            question
        )
    )

    return {
        "success": True,
        "question": question,
        "company_info": company_info,
        "causal_evidence": causal_evidence
    }


# ============================================================
# KNOWLEDGE BASE STATISTICS
# ============================================================

def get_knowledge_base_stats() -> Dict[str, Any]:
    """
    Return knowledge-base statistics.
    """

    return {

        "causal_document_chunks":
            document_collection.count(),

        "legacy_causal_records":
            causal_collection.count(),

        "company_records":
            company_collection.count(),

        "database_path":
            str(CHROMA_DIR),

        "causal_source_file":
            CAUSAL_DATA_FILE.name
    }


# ============================================================
# TEST RUNNER
# ============================================================

if __name__ == "__main__":

    test_questions = [

        "What services does TechNova provide?",

        "What caused the system failure?",

        "Why did system latency increase?",

        "What caused the decrease in model accuracy?",

        "What caused the slower API requests?",

        (
            "Is increased database traffic "
            "responsible for higher system latency?"
        )
    ]

    print(
        "\n" + "=" * 70
    )

    print(
        "TECHNOVA SOLUTIONS - RAG RETRIEVAL TEST"
    )

    print(
        "=" * 70
    )

    stats = (
        get_knowledge_base_stats()
    )

    print(
        "\nKnowledge Base Statistics:"
    )

    for key, value in stats.items():

        print(
            f"{key}: {value}"
        )

    print(
        "\n" + "=" * 70
    )

    for index, question in enumerate(
        test_questions,
        start=1
    ):

        print(
            f"\nTEST {index}"
        )

        print(
            "QUESTION:"
        )

        print(
            question
        )

        print(
            "-" * 70
        )

        company_info = (
            retrieve_company_info(
                question
            )
        )

        evidence = (
            retrieve_causal_evidence(
                question
            )
        )

        if evidence:

            scenario_number = (
                get_scenario_number(
                    evidence
                )
            )

            if scenario_number:

                print(
                    "RETRIEVED SCENARIO:",
                    scenario_number
                )

            else:

                print(
                    "RETRIEVED FROM KNOWLEDGE BASE"
                )

            print()

            print(
                evidence[:3000]
            )

        elif company_info:

            print(
                "RETRIEVED COMPANY INFORMATION"
            )

            print()

            print(
                company_info
            )

        else:

            print(
                "NO RELEVANT EVIDENCE FOUND"
            )

        print(
            "-" * 70
        )

    print(
        "\n" + "=" * 70
    )

    print(
        "RAG RETRIEVAL TEST COMPLETE"
    )

    print(
        "=" * 70
    )