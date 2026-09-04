# Causal RAG Reasoning Agent

## Evidence-Grounded Causal Reasoning for TechNova Solutions

The **Causal RAG Reasoning Agent** is a Generative AI-based system designed to answer questions that require understanding of cause-and-effect relationships. It extends conventional Retrieval-Augmented Generation (RAG) by adding structured causal reasoning, evidence evaluation, causal verification, alternative-cause analysis, and causal graph generation.

## Project Objective

The main objective of this project is to build an AI system that can go beyond retrieving relevant information and provide a structured explanation of **why an event occurred** based on available evidence.

The system is designed to:

* Identify causes and effects
* Extract cause-effect relationships
* Construct causal chains
* Evaluate evidence strength
* Distinguish causation from correlation
* Verify causal conclusions
* Analyze alternative causes
* Generate causal graph representations
* Provide confidence and overall evaluation scores

## Key Features

### Causal Query Analysis

The system identifies whether a user question is factual or causal and selects the appropriate processing path.

### Evidence Retrieval

Relevant information is retrieved from the TechNova Solutions knowledge base using the configured RAG retrieval pipeline and ChromaDB.

### Cause-Effect Extraction

The system extracts structured relationships between possible causes and observed effects.

### Causal Chain Construction

Multiple cause-effect relationships can be organized into a step-by-step causal pathway.

### Evidence Evaluation

Retrieved evidence is evaluated for strength and confidence before a causal conclusion is presented.

### Causal Verification

The system determines whether the evidence supports:

* `CAUSALITY_SUPPORTED`
* `CORRELATION_ONLY`
* `INSUFFICIENT_EVIDENCE`

### Alternative Cause Analysis

Possible competing explanations are considered when multiple causes may explain an observed outcome.

### Causal Graph

Verified relationships are represented through a directed causal graph for easier interpretation.

### Interactive Dashboard

The web interface displays the answer, causal information, evidence, causal chain, graph, verification results, confidence, and evaluation metrics.

## System Workflow

```text
User Query
    ↓
Query Classification
    ↓
Evidence Retrieval
    ↓
Claim Extraction
    ↓
Cause-Effect Extraction
    ↓
Causal Chain Construction
    ↓
Evidence Evaluation
    ↓
Causal Verification
    ↓
Alternative Cause Analysis
    ↓
Causal Graph
    ↓
Final Evaluation
    ↓
Evidence-Grounded Answer
```

## Technology Stack

* **Python** – Core development and reasoning pipeline
* **FastAPI** – Backend API services
* **ChromaDB** – Knowledge retrieval and vector storage
* **Google GenAI** – Generative AI integration
* **HTML** – Frontend structure
* **CSS** – Frontend styling
* **JavaScript** – Frontend interaction

## Project Structure

```text
causal-rag-reasoning-agentt/
│
├── backend/
│   ├── causal_analyzer.py
│   ├── causal_chain.py
│   ├── causal_graph.py
│   ├── causal_reasoning.py
│   ├── causal_verifier.py
│   ├── cause_effect_extractor.py
│   ├── claim_extractor.py
│   ├── evaluation.py
│   ├── evaluator.py
│   ├── evidence_evaluator.py
│   ├── ingest_documents.py
│   ├── main.py
│   ├── rag.py
│   ├── rag_comparison.py
│   ├── standard_rag.py
│   ├── test_causal_dataset.py
│   ├── test_system.py
│   └── frontend/
│       ├── index.html
│       ├── script.js
│       └── style.css
│
├── data/
│   ├── causal_data.txt
│   ├── causal_test_dataset.json
│   └── company_info.txt
│
├── .gitignore
├── test_gemini.py
├── all_python_code.txt
└── project_structure.txt
```

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/iswaryachinnaiyanpillai-cloud/causal-rag-reasoning-agentt.git
cd causal-rag-reasoning-agentt
```

### 2. Create and activate a Python environment

```bash
python -m venv venv312
```

Windows PowerShell:

```powershell
.\venv312\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a local `.env` file:

```text
GEMINI_API_KEY=YOUR_API_KEY
```

**Never commit the `.env` file or your API key to GitHub.**

### 5. Start the backend

```bash
python -m uvicorn backend.main:app --reload
```

### 6. Open the application

Use the local URL displayed by FastAPI/Uvicorn and open the web dashboard.

## Standard RAG vs Causal RAG

The project includes a Standard RAG baseline for comparison.

| Capability                 | Standard RAG | Causal RAG |
| -------------------------- | ------------ | ---------- |
| Evidence Retrieval         | Yes          | Yes        |
| Answer Generation          | Yes          | Yes        |
| Causal Reasoning           | No           | Yes        |
| Cause-Effect Extraction    | No           | Yes        |
| Causal Chain Construction  | No           | Yes        |
| Evidence Evaluation        | No           | Yes        |
| Causal Verification        | No           | Yes        |
| Causal Graph               | No           | Yes        |
| Alternative Cause Analysis | No           | Yes        |
| Overall Causal Evaluation  | No           | Yes        |

## Evaluation Results

The system was evaluated using predefined causal scenarios.

### Automated Evaluation

* **Total test cases:** 11
* **Passed:** 11
* **Failed:** 0
* **Pass rate:** 100%

### Multi-Scenario Benchmark

* **Questions evaluated:** 6
* **Causality supported:** 4
* **Correlation only:** 1
* **Insufficient evidence:** 1
* **Average Causal RAG score:** 76.67

### Detailed Multi-Step Scenario

For the question:

> **Why did system latency increase?**

The system identified **increased database traffic** as the strongest supported cause.

Results:

* **Overall score:** 100/100
* **Evidence quality:** STRONG
* **Chain quality:** EXCELLENT
* **Verification:** CAUSALITY_SUPPORTED
* **Confidence:** HIGH
* **Analysis completeness:** 100%

## Example Scenarios

The system supports different causal reasoning situations, including:

1. Direct causal relationships
2. Multi-step causal chains
3. Correlation-only situations
4. Multiple possible causes
5. Insufficient-evidence cases

## Security

API credentials are stored locally in `.env` and excluded from Git tracking using `.gitignore`.

Do not publish or share API keys in source code, screenshots, documentation, or public repositories.

## Future Scope

Future improvements could include:

* More advanced causal inference techniques
* Larger and more diverse knowledge bases
* Automated evidence source ranking
* Domain-specific causal models
* Advanced graph analytics
* Improved natural-language explanations
* Larger-scale evaluation datasets

## Author

**Iswarya C.P**

**AI & Data Science Student**

**Project:** Causal RAG Reasoning Agent
**Domain:** Generative AI

## Internship

Developed as part of the **Generative AI Internship at Aspire Code AI**.

---
