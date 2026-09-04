# ============================================================
# DOCUMENT INGESTION MODULE
# Causal RAG Reasoning Agent
# TechNova Solutions
# ============================================================

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

import chromadb


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / "chroma_db"

SOURCE_FILE = DATA_DIR / "causal_data.txt"

COLLECTION_NAME = "technova_documents"


# ============================================================
# CHROMA CLIENT
# ============================================================

def get_chroma_client():
    """
    Create and return a persistent ChromaDB client.
    """

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    return chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text: str) -> str:
    """
    Normalize whitespace and remove unnecessary blank lines.
    """

    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove trailing spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Normalize excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ============================================================
# SCENARIO SPLITTING
# ============================================================

def split_scenarios(text: str) -> List[str]:
    """
    Split causal_data.txt into scenario blocks.

    The expected format is generally:

    Scenario 1
    ...

    Scenario 2
    ...

    etc.
    """

    text = clean_text(text)

    if not text:
        return []

    # Scenario headings such as:
    # Scenario 1
    # SCENARIO 1:
    # Scenario 10 -
    pattern = r"(?im)(?=^\s*scenario\s+\d+\b)"

    parts = re.split(pattern, text)

    scenarios = []

    for part in parts:
        part = clean_text(part)

        if part:
            scenarios.append(part)

    return scenarios


# ============================================================
# SCENARIO METADATA
# ============================================================

def extract_scenario_metadata(
    scenario_text: str,
) -> Tuple[int, str]:
    """
    Extract scenario number and title.
    """

    match = re.search(
        r"(?im)^\s*scenario\s+(\d+)\s*[:\-]?\s*(.*)$",
        scenario_text,
    )

    if match:
        scenario_number = int(match.group(1))
        title = match.group(2).strip()

        if not title:
            title = f"Scenario {scenario_number}"

        return scenario_number, title

    return 0, "Unknown Scenario"


# ============================================================
# CHUNKING
# ============================================================

def chunk_text(
    text: str,
    chunk_size: int = 700,
    overlap: int = 100,
) -> List[str]:
    """
    Split long text into overlapping chunks.

    chunk_size:
        Maximum approximate character count per chunk.

    overlap:
        Number of characters carried into the next chunk.
    """

    text = clean_text(text)

    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    # If the text is already small enough
    if len(text) <= chunk_size:
        return [text]

    chunks: List[str] = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = min(
            start + chunk_size,
            text_length,
        )

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap

    return chunks


# ============================================================
# LOAD SOURCE DOCUMENT
# ============================================================

def load_source_document() -> str:
    """
    Load causal_data.txt.
    """

    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"Source document not found: {SOURCE_FILE}"
        )

    text = SOURCE_FILE.read_text(
        encoding="utf-8"
    )

    text = clean_text(text)

    if not text:
        raise ValueError(
            f"Source document is empty: {SOURCE_FILE}"
        )

    return text


# ============================================================
# COLLECTION MANAGEMENT
# ============================================================

def get_collection():
    """
    Get or create the TechNova document collection.
    """

    client = get_chroma_client()

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    return collection


def clear_collection() -> None:
    """
    Delete and recreate the ingestion collection.

    This gives us a clean knowledge base every time the
    ingestion script is executed.
    """

    client = get_chroma_client()

    try:
        client.delete_collection(
            name=COLLECTION_NAME
        )
    except Exception:
        # Collection may not exist yet.
        pass

    client.get_or_create_collection(
        name=COLLECTION_NAME
    )


# ============================================================
# BUILD DOCUMENT RECORDS
# ============================================================

def build_document_records(
    source_text: str,
    chunk_size: int = 700,
    overlap: int = 100,
) -> List[Dict[str, Any]]:
    """
    Convert the source document into ChromaDB records.
    """

    scenarios = split_scenarios(source_text)

    records: List[Dict[str, Any]] = []

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    if not scenarios:
        chunks = chunk_text(
            source_text,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for chunk_index, chunk in enumerate(chunks):

            records.append(
                {
                    "id": f"document_chunk_{chunk_index}",
                    "document": chunk,
                    "metadata": {
                        "source": SOURCE_FILE.name,
                        "scenario": 0,
                        "scenario_title": "General Knowledge Base",
                        "chunk": chunk_index,
                        "document_type": "causal_knowledge",
                        "chunk_size": chunk_size,
                        "overlap": overlap,
                    },
                }
            )

        return records

    # --------------------------------------------------------
    # SCENARIO-BASED RECORDS
    # --------------------------------------------------------

    for scenario_text in scenarios:

        scenario_number, scenario_title = (
            extract_scenario_metadata(
                scenario_text
            )
        )

        chunks = chunk_text(
            scenario_text,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for chunk_index, chunk in enumerate(chunks):

            # NOTE:
            # This is only the logical/base ID.
            # A globally unique ID is created later during
            # ingestion before adding records to ChromaDB.

            base_id = (
                f"scenario_{scenario_number}_"
                f"chunk_{chunk_index}"
            )

            metadata = {
                "source": SOURCE_FILE.name,
                "scenario": scenario_number,
                "scenario_title": scenario_title,
                "chunk": chunk_index,
                "document_type": "causal_knowledge",
                "chunk_size": chunk_size,
                "overlap": overlap,
            }

            records.append(
                {
                    "id": base_id,
                    "document": chunk,
                    "metadata": metadata,
                }
            )

    return records


# ============================================================
# INGEST DOCUMENTS
# ============================================================

def ingest_documents(
    chunk_size: int = 700,
    overlap: int = 100,
) -> Dict[str, Any]:
    """
    Complete ingestion pipeline.

    1. Load source document
    2. Split into scenarios
    3. Create chunks
    4. Clear old ChromaDB collection
    5. Generate globally unique IDs
    6. Insert documents
    7. Return ingestion statistics
    """

    print("=" * 70)
    print("TECHNOVA DOCUMENT INGESTION")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. LOAD SOURCE
    # --------------------------------------------------------

    print(f"\nSource file:")
    print(SOURCE_FILE)

    source_text = load_source_document()

    print(
        f"Loaded characters: {len(source_text)}"
    )

    # --------------------------------------------------------
    # 2. BUILD RECORDS
    # --------------------------------------------------------

    records = build_document_records(
        source_text=source_text,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    if not records:
        raise ValueError(
            "No document records were created."
        )

    print(
        f"Prepared records: {len(records)}"
    )

    # --------------------------------------------------------
    # 3. CLEAR PREVIOUS COLLECTION
    # --------------------------------------------------------

    print("\nClearing previous collection...")

    clear_collection()

    # --------------------------------------------------------
    # 4. GET COLLECTION
    # --------------------------------------------------------

    collection = get_collection()

    # --------------------------------------------------------
    # 5. PREPARE CHROMADB DATA
    # --------------------------------------------------------

    unique_ids: List[str] = []
    documents: List[str] = []
    metadatas: List[Dict[str, Any]] = []

    used_ids = set()

    for index, record in enumerate(records):

        original_id = str(
            record.get(
                "id",
                f"document_{index}",
            )
        )

        # ----------------------------------------------------
        # GUARANTEED UNIQUE CHROMADB ID
        # ----------------------------------------------------

        unique_id = f"{original_id}_{index}"

        # Additional safety check
        while unique_id in used_ids:
            index += 1
            unique_id = f"{original_id}_{index}"

        used_ids.add(unique_id)

        # ----------------------------------------------------
        # DOCUMENT
        # ----------------------------------------------------

        document = clean_text(
            str(
                record.get(
                    "document",
                    "",
                )
            )
        )

        if not document:
            continue

        # ----------------------------------------------------
        # METADATA
        # ----------------------------------------------------

        metadata = dict(
            record.get(
                "metadata",
                {},
            )
        )

        # Store the original logical ID too.
        metadata["record_id"] = original_id
        metadata["chromadb_id"] = unique_id

        # ----------------------------------------------------
        # APPEND
        # ----------------------------------------------------

        unique_ids.append(unique_id)
        documents.append(document)
        metadatas.append(metadata)

    # --------------------------------------------------------
    # SAFETY VALIDATION
    # --------------------------------------------------------

    if not unique_ids:
        raise ValueError(
            "No valid documents were prepared for ChromaDB."
        )

    if len(unique_ids) != len(set(unique_ids)):
        raise ValueError(
            "Internal error: ChromaDB IDs are still duplicated."
        )

    if not (
        len(unique_ids)
        == len(documents)
        == len(metadatas)
    ):
        raise ValueError(
            "IDs, documents, and metadata lengths do not match."
        )

    # --------------------------------------------------------
    # 6. INSERT INTO CHROMADB
    # --------------------------------------------------------

    print(
        "\nInserting documents into ChromaDB..."
    )

    collection.add(
        ids=unique_ids,
        documents=documents,
        metadatas=metadatas,
    )

    # --------------------------------------------------------
    # 7. VERIFY
    # --------------------------------------------------------

    stored_count = collection.count()

    # --------------------------------------------------------
    # SCENARIO COUNT
    # --------------------------------------------------------

    scenario_numbers = set()

    for metadata in metadatas:

        scenario = metadata.get(
            "scenario"
        )

        if scenario is not None:
            scenario_numbers.add(
                scenario
            )

    # Remove fallback scenario 0 from actual count
    real_scenarios = {
        value
        for value in scenario_numbers
        if value != 0
    }

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    result = {
        "success": True,
        "source_file": str(SOURCE_FILE),
        "collection": COLLECTION_NAME,
        "records_prepared": len(records),
        "records_inserted": len(unique_ids),
        "stored_count": stored_count,
        "scenario_count": len(real_scenarios),
        "chunk_size": chunk_size,
        "overlap": overlap,
        "unique_ids": len(set(unique_ids)),
    }

    # --------------------------------------------------------
    # PRINT RESULT
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("INGESTION COMPLETE")
    print("=" * 70)

    print(
        f"Collection          : {COLLECTION_NAME}"
    )

    print(
        f"Records prepared    : {len(records)}"
    )

    print(
        f"Records inserted    : {len(unique_ids)}"
    )

    print(
        f"Stored in ChromaDB  : {stored_count}"
    )

    print(
        f"Scenarios detected  : {len(real_scenarios)}"
    )

    print(
        f"Unique IDs          : {len(set(unique_ids))}"
    )

    print(
        f"Chunk size          : {chunk_size}"
    )

    print(
        f"Overlap             : {overlap}"
    )

    print("=" * 70)

    return result


# ============================================================
# VERIFY KNOWLEDGE BASE
# ============================================================

def verify_knowledge_base() -> Dict[str, Any]:
    """
    Verify that documents actually exist in ChromaDB.
    """

    collection = get_collection()

    count = collection.count()

    # Retrieve a small sample for verification
    sample = collection.get(
        limit=min(5, count)
    ) if count > 0 else {
        "ids": [],
        "documents": [],
        "metadatas": [],
    }

    result = {
        "success": count > 0,
        "collection": COLLECTION_NAME,
        "document_count": count,
        "sample_ids": sample.get(
            "ids",
            [],
        ),
        "sample_documents": sample.get(
            "documents",
            [],
        ),
    }

    return result


# ============================================================
# DISPLAY KNOWLEDGE BASE
# ============================================================

def display_knowledge_base() -> None:
    """
    Print knowledge-base information for debugging.
    """

    result = verify_knowledge_base()

    print("\n" + "=" * 70)
    print("KNOWLEDGE BASE VERIFICATION")
    print("=" * 70)

    print(
        f"Collection: {result['collection']}"
    )

    print(
        f"Documents : {result['document_count']}"
    )

    if result["document_count"] == 0:

        print(
            "\nKnowledge base is empty."
        )

        return

    print("\nSample records:")

    for index, document_id in enumerate(
        result["sample_ids"]
    ):

        print(
            f"\n[{index + 1}] ID: {document_id}"
        )

        if index < len(
            result["sample_documents"]
        ):

            document = (
                result["sample_documents"][index]
            )

            preview = document[:250]

            if len(document) > 250:
                preview += "..."

            print(
                f"Document: {preview}"
            )

    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        result = ingest_documents()

        print("\nVerification:")

        verification = verify_knowledge_base()

        print(
            f"Knowledge base ready: "
            f"{verification['success']}"
        )

        print(
            f"Documents available: "
            f"{verification['document_count']}"
        )

        print("\nSample data:")

        for index, document_id in enumerate(
            verification["sample_ids"]
        ):

            print(
                f"  {index + 1}. {document_id}"
            )

        print("\n✅ Document ingestion successful.")

    except Exception as error:

        print("\n" + "=" * 70)
        print("INGESTION FAILED")
        print("=" * 70)

        print(
            f"Error: {error}"
        )

        print("=" * 70)

        raise