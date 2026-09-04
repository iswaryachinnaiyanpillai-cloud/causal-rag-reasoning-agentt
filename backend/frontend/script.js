// ============================================================
// CAUSAL RAG AGENT
// FRONTEND JAVASCRIPT
// TechNova Solutions
// ============================================================


// ============================================================
// API CONFIGURATION
// ============================================================

const API_BASE = "http://127.0.0.1:8000";


// ============================================================
// DOM HELPERS
// ============================================================

function getElement(id) {
    return document.getElementById(id);
}


function setText(id, value) {

    const element = getElement(id);

    if (!element) {
        return;
    }

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {

        element.textContent = "Not available";

        return;
    }

    element.textContent = String(value);
}


// ============================================================
// VISIBILITY HELPERS
// ============================================================

function showElement(element) {

    if (!element) {
        return;
    }

    element.classList.remove("hidden");
    element.style.display = "";
}


function hideElement(element) {

    if (!element) {
        return;
    }

    element.classList.add("hidden");
    element.style.display = "none";
}


// ============================================================
// VALUE HELPERS
// ============================================================

function normalizeArray(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return [];
    }

    if (Array.isArray(value)) {
        return value;
    }

    return [value];
}


function cleanValue(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    if (typeof value === "string") {
        return value.trim();
    }

    if (typeof value === "number") {
        return String(value);
    }

    if (typeof value === "object") {

        return String(
            value.label ??
            value.name ??
            value.title ??
            value.text ??
            value.claim ??
            value.value ??
            value.id ??
            ""
        ).trim();
    }

    return String(value).trim();
}


function formatStatus(value) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "Not available";
    }

    return String(value)
        .replaceAll("_", " ")
        .toUpperCase();
}


function isFactual(result) {

    return (
        String(
            result?.query_type || ""
        ).toUpperCase() === "FACTUAL"
    );
}


function getVerificationStatus(result) {

    return String(
        result?.causal_verification?.status ||
        result?.causal_status ||
        result?.overall_evaluation?.causal_verification ||
        result?.evaluation?.causal_verification ||
        ""
    ).toUpperCase();
}


function isCorrelation(result) {

    const status = getVerificationStatus(result);

    const evidence =
        String(
            result?.retrieved_evidence || ""
        ).toLowerCase();

    return (
        status === "CORRELATION_ONLY" ||
        evidence.includes("correlation_only") ||
        evidence.includes("correlation only") ||
        evidence.includes(
            "direct causation is not confirmed"
        ) ||
        evidence.includes(
            "relationship is correlational"
        ) ||
        evidence.includes(
            "does not establish direct causation"
        )
    );
}


function isInsufficient(result) {

    const status = getVerificationStatus(result);

    const evidence =
        String(
            result?.retrieved_evidence || ""
        ).toLowerCase();

    return (
        status === "INSUFFICIENT_EVIDENCE" ||
        evidence.includes("insufficient evidence") ||
        evidence.includes("no reliable cause") ||
        evidence.includes(
            "does not identify a verified cause"
        ) ||
        evidence.includes(
            "does not provide enough information"
        )
    );
}


// ============================================================
// ERROR HANDLING
// ============================================================

function showError(message) {

    const errorElement =
        getElement("errorMessage");

    if (!errorElement) {
        return;
    }

    errorElement.textContent =
        message ||
        "Something went wrong.";

    errorElement.classList.remove(
        "hidden"
    );

    errorElement.style.display =
        "block";
}


function hideError() {

    const errorElement =
        getElement("errorMessage");

    if (!errorElement) {
        return;
    }

    errorElement.textContent = "";

    errorElement.classList.add(
        "hidden"
    );

    errorElement.style.display =
        "none";
}


// ============================================================
// LOADING
// ============================================================

function setLoading(isLoading) {

    const loading =
        getElement("loading");

    const button =
        getElement("askButton");

    if (isLoading) {

        if (loading) {

            loading.classList.remove(
                "hidden"
            );

            loading.style.display =
                "flex";
        }

        if (button) {

            button.disabled = true;

            button.style.opacity =
                "0.7";

            button.style.cursor =
                "wait";
        }

    } else {

        if (loading) {

            loading.classList.add(
                "hidden"
            );

            loading.style.display =
                "none";
        }

        if (button) {

            button.disabled = false;

            button.style.opacity =
                "1";

            button.style.cursor =
                "pointer";
        }
    }
}


// ============================================================
// RENDER FACTORS
// ============================================================

function renderFactors(
    elementId,
    values,
    emptyMessage = "None identified"
) {

    const element =
        getElement(elementId);

    if (!element) {
        return;
    }

    element.innerHTML = "";

    const items =
        normalizeArray(values)
            .map(cleanValue)
            .filter(Boolean);


    if (!items.length) {

        const empty =
            document.createElement("span");

        empty.className =
            "empty-value";

        empty.textContent =
            emptyMessage;

        element.appendChild(
            empty
        );

        return;
    }


    items.forEach(item => {

        const factor =
            document.createElement("span");

        factor.className =
            "factor-item";

        factor.textContent =
            item;

        element.appendChild(
            factor
        );
    });
}


// ============================================================
// EXTRACT CHAIN FROM EVIDENCE
// ============================================================

function extractChainFromEvidence(
    evidence
) {

    if (!evidence) {
        return [];
    }

    const text =
        String(evidence);

    /*
     * Looks for a line such as:
     *
     * Causal Chain:
     * Increased user requests -> Higher database queries
     * -> Higher database load -> Increased processing time
     * -> Higher system latency -> System timeout.
     */

    const match =
        text.match(
            /Causal Chain:\s*([\s\S]*?)(?:\n\s*\n|\nEvidence Strength:|\nCausal Status:|\nRetrieved Evidence:|$)/i
        );

    if (!match) {
        return [];
    }

    let chainText =
        match[1]
            .replace(/\r/g, " ")
            .replace(/\n/g, " ")
            .trim();

    chainText =
        chainText.replace(/\.$/, "");

    const chain =
        chainText
            .split(/\s*(?:->|→)\s*/)
            .map(item => item.trim())
            .filter(Boolean);

    return chain;
}


// ============================================================
// RESOLVE CAUSAL CHAIN
// ============================================================

function resolveCausalChain(result) {

    // --------------------------------------------------------
    // 1. API causal_chain
    // --------------------------------------------------------

    let chain =
        normalizeArray(
            result?.causal_chain
        )
        .map(cleanValue)
        .filter(Boolean);


    // --------------------------------------------------------
    // 2. If API chain is complete, use it.
    // --------------------------------------------------------

    if (chain.length >= 3) {
        return chain;
    }


    // --------------------------------------------------------
    // 3. Try chain inside causal_information
    // --------------------------------------------------------

    const information =
        result?.causal_information || {};


    const informationChain =
        normalizeArray(
            information.chain ||
            information.causal_chain
        )
        .map(cleanValue)
        .filter(Boolean);


    if (informationChain.length >= 3) {
        return informationChain;
    }


    // --------------------------------------------------------
    // 4. Extract the explicit chain from evidence
    // --------------------------------------------------------

    const evidenceChain =
        extractChainFromEvidence(
            result?.retrieved_evidence || ""
        );


    if (evidenceChain.length >= 2) {
        return evidenceChain;
    }


    // --------------------------------------------------------
    // 5. Fall back to API chain
    // --------------------------------------------------------

    if (chain.length) {
        return chain;
    }


    // --------------------------------------------------------
    // 6. Last-resort cause -> effect
    // --------------------------------------------------------

    const cause =
        cleanValue(
            information.cause ||
            information.primary_cause
        );

    const effect =
        cleanValue(
            information.effect
        );


    if (cause && effect) {
        return [
            cause,
            effect
        ];
    }


    return [];
}


// ============================================================
// RENDER CAUSAL CHAIN
// ============================================================

function renderCausalChain(
    chain,
    result = null
) {

    const container =
        getElement("causalChain");

    if (!container) {
        return;
    }

    container.innerHTML = "";


    const resolvedChain =
        resolveCausalChain(
            result || {
                causal_chain: chain
            }
        );


    if (!resolvedChain.length) {

        const empty =
            document.createElement("div");

        empty.className =
            "empty-chain";

        empty.textContent =
            "No verified causal chain available.";

        container.appendChild(
            empty
        );

        return;
    }


    const chainWrapper =
        document.createElement("div");

    chainWrapper.className =
        "chain-wrapper";


    resolvedChain.forEach(
        (item, index) => {

            const node =
                document.createElement("div");

            node.className =
                "chain-node";

            node.textContent =
                item;

            chainWrapper.appendChild(
                node
            );


            if (
                index <
                resolvedChain.length - 1
            ) {

                const arrow =
                    document.createElement("div");

                arrow.className =
                    "chain-arrow";

                arrow.textContent =
                    "→";

                chainWrapper.appendChild(
                    arrow
                );
            }
        }
    );


    container.appendChild(
        chainWrapper
    );
}


// ============================================================
// NORMALIZE GRAPH NODES
// ============================================================

function normalizeGraphNodes(
    graph
) {

    if (
        !graph ||
        typeof graph !== "object"
    ) {
        return [];
    }


    return normalizeArray(
        graph.nodes
    )
    .map(
        (node, index) => {

            if (
                typeof node ===
                "string"
            ) {

                return {
                    id: String(index),
                    label: node
                };
            }


            if (
                node &&
                typeof node ===
                "object"
            ) {

                return {

                    id: String(
                        node.id ??
                        node.name ??
                        index
                    ),

                    label: cleanValue(
                        node.label ??
                        node.name ??
                        node.title ??
                        node.text ??
                        node.value ??
                        `Node ${index + 1}`
                    )
                };
            }


            return null;
        }
    )
    .filter(Boolean);
}


// ============================================================
// NORMALIZE GRAPH EDGES
// ============================================================

function normalizeGraphEdges(
    graph
) {

    if (
        !graph ||
        typeof graph !== "object"
    ) {
        return [];
    }


    return normalizeArray(
        graph.edges
    )
    .filter(Boolean);
}


// ============================================================
// RENDER CAUSAL GRAPH
// ============================================================

function renderCausalGraph(
    graph,
    chain,
    result = null
) {

    const container =
        getElement("causalGraph");

    if (!container) {
        return;
    }

    container.innerHTML = "";


    let nodes =
        normalizeGraphNodes(
            graph
        );

    let edges =
        normalizeGraphEdges(
            graph
        );


    // --------------------------------------------------------
    // Resolve chain
    // --------------------------------------------------------

    const resolvedChain =
        resolveCausalChain(
            result || {
                causal_chain: chain
            }
        );


    // --------------------------------------------------------
    // FALLBACK GRAPH FROM CHAIN
    // --------------------------------------------------------

    if (
        resolvedChain.length &&
        resolvedChain.length !== nodes.length
    ) {

        nodes =
            resolvedChain.map(
                (item, index) => {

                    return {
                        id: String(index),
                        label: item
                    };
                }
            );

        edges = [];

        for (
            let index = 0;
            index <
            resolvedChain.length - 1;
            index++
        ) {

            edges.push({

                source:
                    String(index),

                target:
                    String(index + 1),

                label:
                    "causes",

                relationship:
                    "causal"
            });
        }
    }


    // --------------------------------------------------------
    // If no graph nodes, construct from chain
    // --------------------------------------------------------

    if (!nodes.length) {

        resolvedChain.forEach(
            (item, index) => {

                nodes.push({

                    id:
                        String(index),

                    label:
                        item
                });


                if (
                    index <
                    resolvedChain.length - 1
                ) {

                    edges.push({

                        source:
                            String(index),

                        target:
                            String(index + 1),

                        label:
                            "causes"
                    });
                }
            }
        );
    }


    // --------------------------------------------------------
    // NO GRAPH
    // --------------------------------------------------------

    if (!nodes.length) {

        const empty =
            document.createElement("div");

        empty.className =
            "empty-graph";

        empty.textContent =
            "No causal graph available for this analysis.";

        container.appendChild(
            empty
        );

        return;
    }


    // --------------------------------------------------------
    // GRAPH WRAPPER
    // --------------------------------------------------------

    const graphWrapper =
        document.createElement("div");

    graphWrapper.className =
        "causal-graph-wrapper";


    // --------------------------------------------------------
    // GRAPH LEGEND
    // --------------------------------------------------------

    const graphHint =
        document.createElement("div");

    graphHint.className =
        "graph-hint";

    graphHint.innerHTML = `
        <span class="legend-cause">CAUSE</span>
        <span>→</span>
        <span class="legend-effect">EFFECT</span>
    `;

    graphWrapper.appendChild(
        graphHint
    );


    // --------------------------------------------------------
    // GRAPH AREA
    // --------------------------------------------------------

    const graphArea =
        document.createElement("div");

    graphArea.className =
        "graph-area";


    // --------------------------------------------------------
    // RENDER NODES
    // --------------------------------------------------------

    nodes.forEach(
        (node, index) => {

            const nodeWrapper =
                document.createElement("div");

            nodeWrapper.className =
                "graph-node-wrapper";


            const graphNode =
                document.createElement("div");

            graphNode.className =
                "graph-node";


            graphNode.textContent =
                cleanValue(
                    node.label
                );


            if (
                index === 0
            ) {

                graphNode.classList.add(
                    "graph-cause"
                );
            }


            if (
                index ===
                nodes.length - 1
            ) {

                graphNode.classList.add(
                    "graph-effect"
                );
            }


            nodeWrapper.appendChild(
                graphNode
            );


            if (
                index <
                nodes.length - 1
            ) {

                const connector =
                    document.createElement("div");

                connector.className =
                    "graph-connector";


                const line =
                    document.createElement("div");

                line.className =
                    "graph-line";


                const relation =
                    document.createElement("span");

                relation.className =
                    "graph-relation";


                const currentNode =
                    node;

                const nextNode =
                    nodes[index + 1];


                const currentEdge =
                    edges.find(
                        edge => {

                            const source =
                                cleanValue(
                                    edge?.source ??
                                    edge?.from ??
                                    edge?.source_id
                                );

                            const target =
                                cleanValue(
                                    edge?.target ??
                                    edge?.to ??
                                    edge?.target_id
                                );

                            return (
                                (
                                    source ===
                                    String(
                                        currentNode.id
                                    )
                                )
                                &&
                                (
                                    target ===
                                    String(
                                        nextNode.id
                                    )
                                )
                            );
                        }
                    );


                relation.textContent =
                    cleanValue(
                        currentEdge?.relationship ??
                        currentEdge?.relation ??
                        currentEdge?.label ??
                        "causes"
                    ).toLowerCase();


                const arrow =
                    document.createElement("div");

                arrow.className =
                    "graph-arrow";

                arrow.textContent =
                    "↓";


                connector.appendChild(
                    line
                );

                connector.appendChild(
                    relation
                );

                connector.appendChild(
                    arrow
                );


                nodeWrapper.appendChild(
                    connector
                );
            }


            graphArea.appendChild(
                nodeWrapper
            );
        }
    );


    graphWrapper.appendChild(
        graphArea
    );


    container.appendChild(
        graphWrapper
    );
}


// ============================================================
// EVIDENCE EVALUATION
// ============================================================

function renderEvidenceEvaluation(
    evaluation
) {

    evaluation =
        evaluation || {};


    setText(
        "evidenceStrength",
        formatStatus(
            evaluation.strength ??
            evaluation.evidence_strength ??
            evaluation.evidenceQuality
        )
    );


    setText(
        "evidenceConfidence",
        formatStatus(
            evaluation.confidence ??
            evaluation.evidence_confidence
        )
    );


    setText(
        "claimCount",
        evaluation.claim_count ??
        evaluation.claims ??
        evaluation.claimCount ??
        0
    );


    setText(
        "causalClaims",
        evaluation.causal_claims ??
        evaluation.causalClaims ??
        0
    );
}


// ============================================================
// VERIFICATION
// ============================================================

function renderVerification(
    verification
) {

    verification =
        verification || {};


    setText(
        "verificationStatus",
        formatStatus(
            verification.status ??
            verification.verification_status
        )
    );


    setText(
        "verificationConfidence",
        formatStatus(
            verification.confidence
        )
    );


    setText(
        "verifiedClaims",
        verification.verified_claims ??
        verification.verified_claim_count ??
        verification.verifiedClaims ??
        0
    );
}


// ============================================================
// OVERALL EVALUATION
// ============================================================

function renderEvaluation(
    evaluation,
    result
) {

    evaluation =
        evaluation || {};


    // --------------------------------------------------------
    // FACTUAL
    // --------------------------------------------------------

    if (
        isFactual(result)
    ) {

        setText(
            "overallScore",
            "N/A"
        );

        setText(
            "evaluationEvidence",
            "N/A"
        );

        setText(
            "evaluationChain",
            "N/A"
        );

        setText(
            "evaluationVerification",
            "N/A"
        );

        setText(
            "evaluationConfidence",
            "N/A"
        );

        setText(
            "analysisCompleteness",
            "N/A"
        );

        setText(
            "evaluationSummary",
            "Factual query. Causal evaluation is not required."
        );

        return;
    }


    // --------------------------------------------------------
    // SCORE
    // --------------------------------------------------------

    const score =
        evaluation.overall_score ??
        evaluation.overallScore ??
        evaluation.score ??
        null;


    setText(
        "overallScore",
        score !== null
            ? score
            : "N/A"
    );


    // --------------------------------------------------------
    // EVIDENCE QUALITY
    // --------------------------------------------------------

    const evidenceQuality =
        evaluation.evidence_quality ??
        evaluation.evidenceQuality ??
        evaluation.evidence_strength ??
        evaluation.strength ??
        result?.evidence_evaluation?.evidence_strength ??
        null;


    setText(
        "evaluationEvidence",
        evidenceQuality
            ? formatStatus(
                evidenceQuality
            )
            : "N/A"
    );


    // --------------------------------------------------------
    // CHAIN QUALITY
    // --------------------------------------------------------

    const resolvedChain =
        resolveCausalChain(
            result
        );


    let chainQuality =
        evaluation.chain_quality ??
        evaluation.chainQuality ??
        evaluation.causal_chain_quality ??
        evaluation.chain ??
        null;


    /*
     * If the backend did not provide a useful chain-quality
     * value, calculate a display value from the actual chain.
     */

    if (
        !chainQuality &&
        resolvedChain.length >= 3
    ) {

        chainQuality =
            "EXCELLENT";
    }


    setText(
        "evaluationChain",
        chainQuality
            ? formatStatus(
                chainQuality
            )
            : "N/A"
    );


    // --------------------------------------------------------
    // VERIFICATION
    // --------------------------------------------------------

    const verificationStatus =
        evaluation.verification_status ??
        evaluation.verificationStatus ??
        evaluation.causal_verification ??
        evaluation.verification ??
        result?.causal_verification?.status ??
        result?.causal_status ??
        null;


    setText(
        "evaluationVerification",
        verificationStatus
            ? formatStatus(
                verificationStatus
            )
            : "N/A"
    );


    // --------------------------------------------------------
    // CONFIDENCE
    // --------------------------------------------------------

    const confidence =
        evaluation.confidence ??
        evaluation.overall_confidence ??
        result?.causal_verification?.confidence ??
        result?.evidence_evaluation?.confidence ??
        null;


    setText(
        "evaluationConfidence",
        confidence
            ? formatStatus(
                confidence
            )
            : "N/A"
    );


    // --------------------------------------------------------
    // COMPLETENESS
    // --------------------------------------------------------

    let completeness =
        evaluation.completeness ??
        evaluation.analysis_completeness ??
        evaluation.completeness_percentage ??
        null;


    if (
        completeness !== null &&
        completeness !== undefined
    ) {

        if (
            typeof completeness === "number" &&
            completeness <= 1
        ) {

            completeness =
                completeness * 100;
        }


        if (
            typeof completeness === "number"
        ) {

            completeness =
                Math.round(
                    completeness
                ) + "%";
        }
    }


    setText(
        "analysisCompleteness",
        completeness ??
        "N/A"
    );


    // --------------------------------------------------------
    // SUMMARY
    // --------------------------------------------------------

    const summary =
        evaluation.evaluation_summary ??
        evaluation.summary ??
        result?.evaluation_summary ??
        "";


    if (summary) {

        setText(
            "evaluationSummary",
            summary
        );

    } else {

        const generatedSummary = [];


        if (evidenceQuality) {

            generatedSummary.push(
                `Evidence quality: ${formatStatus(
                    evidenceQuality
                )}.`
            );
        }


        if (chainQuality) {

            generatedSummary.push(
                `Causal chain quality: ${formatStatus(
                    chainQuality
                )}.`
            );
        }


        if (verificationStatus) {

            generatedSummary.push(
                `Causal verification: ${formatStatus(
                    verificationStatus
                )}.`
            );
        }


        if (confidence) {

            generatedSummary.push(
                `Confidence: ${formatStatus(
                    confidence
                )}.`
            );
        }


        if (
            completeness !== null &&
            completeness !== undefined
        ) {

            generatedSummary.push(
                `Analysis completeness: ${completeness}.`
            );
        }


        if (score !== null) {

            generatedSummary.push(
                `Overall evaluation score: ${score}/100.`
            );
        }


        setText(
            "evaluationSummary",
            generatedSummary.length
                ? generatedSummary.join(" ")
                : "No evaluation available."
        );
    }
}


// ============================================================
// CAUSAL INFORMATION
// ============================================================

function renderCausalInformation(
    information,
    result
) {

    information =
        information || {};


    // --------------------------------------------------------
    // FACTUAL
    // --------------------------------------------------------

    if (
        isFactual(result)
    ) {

        setText(
            "cause",
            "Not applicable"
        );

        setText(
            "effect",
            "Not applicable"
        );


        renderFactors(
            "intermediateFactors",
            [],
            "None identified"
        );


        renderFactors(
            "alternativeCauses",
            [],
            "None identified"
        );


        return;
    }


    // --------------------------------------------------------
    // CORRELATION
    // --------------------------------------------------------

    if (
        isCorrelation(result)
    ) {

        setText(
            "cause",
            "Direct cause not confirmed"
        );


        setText(
            "effect",
            information.effect ||
            "Related outcome"
        );


        /*
         * For correlation-only results, intermediate factors
         * are not presented as confirmed causal factors.
         */

        renderFactors(
            "intermediateFactors",
            information.factors ??
            information.intermediate_factors ??
            information.intermediateFactors ??
            [],
            "No causal intermediate factors confirmed"
        );


        renderFactors(
            "alternativeCauses",
            information.alternatives ??
            information.alternative_causes ??
            information.alternativeCauses ??
            [],
            "No verified alternatives available"
        );


        return;
    }


    // --------------------------------------------------------
    // INSUFFICIENT
    // --------------------------------------------------------

    if (
        isInsufficient(result)
    ) {

        setText(
            "cause",
            "Unknown"
        );


        setText(
            "effect",
            information.effect ||
            "Observed outcome"
        );


        renderFactors(
            "intermediateFactors",
            information.factors ??
            information.intermediate_factors ??
            information.intermediateFactors ??
            [],
            "None identified"
        );


        renderFactors(
            "alternativeCauses",
            information.alternatives ??
            information.alternative_causes ??
            information.alternativeCauses ??
            [],
            "No verified alternatives available"
        );


        return;
    }


    // --------------------------------------------------------
    // NORMAL CAUSAL
    // --------------------------------------------------------

    setText(
        "cause",
        information.cause ||
        information.primary_cause ||
        "Not available"
    );


    setText(
        "effect",
        information.effect ||
        "Not available"
    );


    /*
     * IMPORTANT:
     *
     * Your backend uses:
     *     factors
     *     alternatives
     *
     * Earlier frontend code was looking only for:
     *     intermediate_factors
     *     alternative_causes
     *
     * Support both formats.
     */

    renderFactors(
        "intermediateFactors",
        information.factors ??
        information.intermediate_factors ??
        information.intermediateFactors ??
        []
    );


    renderFactors(
        "alternativeCauses",
        information.alternatives ??
        information.alternative_causes ??
        information.alternativeCauses ??
        []
    );
}


// ============================================================
// ANSWER
// ============================================================

function renderAnswer(result) {

    const answerElement =
        getElement("answer");

    if (!answerElement) {
        return;
    }


    const answer =
        result?.answer ||
        "No answer available.";


    answerElement.textContent =
        answer;
}


// ============================================================
// RESULT RENDERER
// ============================================================

function renderResult(result) {

    const resultSection =
        getElement("resultSection");

    if (!resultSection) {
        return;
    }


    // --------------------------------------------------------
    // SHOW RESULT
    // --------------------------------------------------------

    resultSection.classList.remove(
        "hidden"
    );

    resultSection.style.display =
        "block";


    // --------------------------------------------------------
    // QUERY TYPE
    // --------------------------------------------------------

    setText(
        "queryType",
        formatStatus(
            result?.query_type ||
            "UNKNOWN"
        )
    );


    // --------------------------------------------------------
    // ANSWER
    // --------------------------------------------------------

    renderAnswer(
        result
    );


    // --------------------------------------------------------
    // CAUSAL INFORMATION
    // --------------------------------------------------------

    renderCausalInformation(
        result?.causal_information ||
        {},
        result
    );


    // --------------------------------------------------------
    // CAUSAL CHAIN
    // --------------------------------------------------------

    renderCausalChain(
        result?.causal_chain ||
        [],
        result
    );


    // --------------------------------------------------------
    // GRAPH
    // --------------------------------------------------------

    renderCausalGraph(
        result?.causal_graph ||
        {},
        result?.causal_chain ||
        [],
        result
    );


    // --------------------------------------------------------
    // EVIDENCE
    // --------------------------------------------------------

    const evidenceElement =
        getElement(
            "retrievedEvidence"
        );


    if (evidenceElement) {

        evidenceElement.textContent =
            result?.retrieved_evidence ||
            "No relevant evidence was found.";
    }


    // --------------------------------------------------------
    // EVIDENCE EVALUATION
    // --------------------------------------------------------

    renderEvidenceEvaluation(
        result?.evidence_evaluation ||
        {}
    );


    // --------------------------------------------------------
    // VERIFICATION
    // --------------------------------------------------------

    renderVerification(
        result?.causal_verification ||
        {}
    );


    // --------------------------------------------------------
    // OVERALL EVALUATION
    //
    // Prefer "overall_evaluation", but keep "evaluation"
    // for compatibility with older API responses.
    // --------------------------------------------------------

    renderEvaluation(
        result?.overall_evaluation ||
        result?.evaluation ||
        {},
        result
    );


    // --------------------------------------------------------
    // UPDATE QUERY TYPE STYLE
    // --------------------------------------------------------

    const queryBadge =
        getElement("queryType");

    if (queryBadge) {

        queryBadge.classList.remove(
            "badge-factual",
            "badge-causal",
            "badge-correlation",
            "badge-insufficient"
        );


        if (
            isFactual(result)
        ) {

            queryBadge.classList.add(
                "badge-factual"
            );

        } else if (
            isCorrelation(result)
        ) {

            queryBadge.classList.add(
                "badge-correlation"
            );

        } else if (
            isInsufficient(result)
        ) {

            queryBadge.classList.add(
                "badge-insufficient"
            );

        } else {

            queryBadge.classList.add(
                "badge-causal"
            );
        }
    }


    // --------------------------------------------------------
    // SCROLL TO RESULTS
    // --------------------------------------------------------

    setTimeout(
        () => {

            resultSection.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        },
        100
    );
}


// ============================================================
// ASK QUESTION
// ============================================================

async function askQuestion() {

    const input =
        getElement("questionInput");

    if (!input) {
        return;
    }


    const question =
        input.value.trim();


    // --------------------------------------------------------
    // VALIDATION
    // --------------------------------------------------------

    if (!question) {

        showError(
            "Please enter a question."
        );

        input.focus();

        return;
    }


    // --------------------------------------------------------
    // START ANALYSIS
    // --------------------------------------------------------

    hideError();

    setLoading(true);


    const resultSection =
        getElement("resultSection");


    if (resultSection) {

        resultSection.classList.add(
            "hidden"
        );

        resultSection.style.display =
            "none";
    }


    try {

        const url =
            `${API_BASE}/ask?question=${encodeURIComponent(
                question
            )}`;


        const response =
            await fetch(url, {
                method: "GET",
                headers: {
                    "Accept":
                        "application/json"
                }
            });


        let data;


        try {

            data =
                await response.json();

        } catch (error) {

            throw new Error(
                "The backend returned an invalid response."
            );
        }


        if (!response.ok) {

            throw new Error(
                data?.error ||
                `Request failed with status ${response.status}.`
            );
        }


        if (
            !data ||
            data.success === false
        ) {

            throw new Error(
                data?.error ||
                "The analysis could not be completed."
            );
        }


        // Console logging makes it easy to inspect
        // the exact backend response during development.
        console.log(
            "Causal RAG API response:",
            data
        );


        renderResult(
            data
        );


    } catch (error) {

        console.error(
            "Causal RAG Error:",
            error
        );


        showError(
            error?.message ||
            "Unable to connect to the Causal RAG backend."
        );


    } finally {

        setLoading(false);
    }
}


// ============================================================
// EXAMPLE QUESTION
// ============================================================

function useExampleQuestion(
    question
) {

    const input =
        getElement("questionInput");

    if (!input) {
        return;
    }


    input.value =
        question ||
        "";


    input.focus();
}


// ============================================================
// NAVIGATION
// ============================================================

function setupNavigation() {

    const links =
        document.querySelectorAll(
            ".nav-item"
        );


    links.forEach(
        link => {

            link.addEventListener(
                "click",
                () => {

                    links.forEach(
                        item => {

                            item.classList.remove(
                                "active"
                            );
                        }
                    );


                    link.classList.add(
                        "active"
                    );
                }
            );
        }
    );
}


// ============================================================
// EXAMPLE BUTTONS
// ============================================================

function setupExampleButtons() {

    const buttons =
        document.querySelectorAll(
            "[data-question]"
        );


    buttons.forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    const question =
                        button.getAttribute(
                            "data-question"
                        );


                    useExampleQuestion(
                        question
                    );
                }
            );
        }
    );
}


// ============================================================
// ANALYZE BUTTON
// ============================================================

function setupAnalyzeButton() {

    const button =
        getElement("askButton");


    if (!button) {
        return;
    }


    button.addEventListener(
        "click",
        event => {

            event.preventDefault();

            askQuestion();
        }
    );
}


// ============================================================
// ENTER KEY
// ============================================================

function setupEnterKey() {

    const input =
        getElement("questionInput");


    if (!input) {
        return;
    }


    input.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                askQuestion();
            }
        }
    );
}


// ============================================================
// BACKEND STATUS
// ============================================================

async function checkBackendStatus() {

    const statusText =
        document.querySelector(
            ".backend-status strong"
        );


    const statusSmall =
        document.querySelector(
            ".backend-status small"
        );


    try {

        const response =
            await fetch(
                `${API_BASE}/health`
            );


        if (response.ok) {

            if (statusText) {

                statusText.textContent =
                    "Backend Online";
            }


            if (statusSmall) {

                statusSmall.textContent =
                    "FastAPI connected";
            }


            console.log(
                "Causal RAG backend connected."
            );


            return true;
        }


    } catch (error) {

        console.warn(
            "Backend status check failed:",
            error
        );
    }


    if (statusText) {

        statusText.textContent =
            "Backend Offline";
    }


    if (statusSmall) {

        statusSmall.textContent =
            "Start FastAPI server";
    }


    return false;
}


// ============================================================
// INITIALIZATION
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        console.log(
            "Causal RAG Agent frontend initialized."
        );


        setupAnalyzeButton();

        setupEnterKey();

        setupExampleButtons();

        setupNavigation();

        checkBackendStatus();
    }
);