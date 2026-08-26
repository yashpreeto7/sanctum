"""Quantitative Benchmark for Hybrid RAG: HitRate@K, MRR, and Context Precision."""

import time
import pytest
from execution.rag.hybrid_retriever import HybridRetriever
from execution.rag.reranker import CrossEncoderReranker
from execution.rag.vector_store import DocumentChunk, LocalVectorStore


# Curated benchmark dataset of test queries and ground-truth target fragments
RAG_BENCHMARK_SCENARIOS = [
    {
        "query": "What is the architecture for DocDispatch?",
        "ground_truth_keyword": "DocDispatch",
        "doc": "DocDispatch architecture is built on FastAPI, LangGraph, and local Qwen 2.5 7B LLM.",
        "source": "obsidian",
        "days_ago": 1,
    },
    {
        "query": "When was the interview scheduled with the AI recruiter?",
        "ground_truth_keyword": "Google Meet",
        "doc": "Interview confirmed for tomorrow at 3 PM on Google Meet with the AI hiring team.",
        "source": "email",
        "days_ago": 0.5,
    },
    {
        "query": "Where are the cloud compute expense invoices stored?",
        "ground_truth_keyword": "Invoice #10492",
        "doc": "Invoice #10492: Cloud compute expenses for August totaled $42.10.",
        "source": "document",
        "days_ago": 3,
    },
    {
        "query": "What did Rahul say about the staging gateway crash?",
        "ground_truth_keyword": "staging gateway outage",
        "doc": "Rahul's message: Investigating the staging gateway outage in the cluster.",
        "source": "email",
        "days_ago": 2,
    },
    {
        "query": "What are the rules for LangGraph checkpointing?",
        "ground_truth_keyword": "SQLite checkpointer",
        "doc": "LangGraph state machine uses SQLite checkpointer to persist thread states during approval waits.",
        "source": "obsidian",
        "days_ago": 5,
    },
]


@pytest.fixture
def populated_benchmark_store():
    """Populates an in-memory vector store with benchmark documents and noise/distractors."""
    store = LocalVectorStore(in_memory=True)
    now = time.time()

    chunks = []
    # 1. Add Ground-Truth benchmark documents
    for item in RAG_BENCHMARK_SCENARIOS:
        created_at = now - (item["days_ago"] * 86400.0)
        chunks.append(
            DocumentChunk(
                text=item["doc"],
                source_type=item["source"],
                created_at_timestamp=created_at,
            )
        )

    # 2. Add distractor / noise documents to challenge the retriever
    noise_docs = [
        "Unrelated shopping receipt from 2022 for coffee beans and filters.",
        "General notes about cooking pasta and tomato sauce recipes.",
        "Weather forecast for Mumbai: rainy with heavy clouds.",
        "JavaScript React 18 component lifecycle documentation snippet.",
        "Kubernetes cluster configuration yaml file notes from legacy project.",
    ]
    for n in noise_docs:
        chunks.append(
            DocumentChunk(
                text=n,
                source_type="document",
                created_at_timestamp=now - (20 * 86400.0),
            )
        )

    store.insert_chunks(chunks)
    return store


def test_rag_hitrate_and_mrr_benchmark(populated_benchmark_store):
    """Measures HitRate@3 and Mean Reciprocal Rank (MRR) across all test scenarios."""
    retriever = HybridRetriever(store=populated_benchmark_store)
    reranker_inst = CrossEncoderReranker()

    hits_at_1 = 0
    hits_at_3 = 0
    reciprocal_ranks = []

    for scenario in RAG_BENCHMARK_SCENARIOS:
        candidates = retriever.search(query=scenario["query"], top_k=10)
        reranked = reranker_inst.rerank(query=scenario["query"], candidates=candidates, top_n=3)

        # Evaluate position of target document
        target_keyword = scenario["ground_truth_keyword"].lower()
        rank = None

        for idx, chunk in enumerate(reranked, start=1):
            if target_keyword in chunk.text.lower():
                rank = idx
                break

        if rank == 1:
            hits_at_1 += 1
        if rank is not None and rank <= 3:
            hits_at_3 += 1
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)

    total_scenarios = len(RAG_BENCHMARK_SCENARIOS)
    hit_rate_at_3 = hits_at_3 / total_scenarios
    hit_rate_at_1 = hits_at_1 / total_scenarios
    mrr = sum(reciprocal_ranks) / total_scenarios

    # Benchmark Acceptance Thresholds
    assert hit_rate_at_3 >= 0.80, f"HitRate@3 was {hit_rate_at_3:.2f}, expected >= 0.80"
    assert hit_rate_at_1 >= 0.60, f"HitRate@1 was {hit_rate_at_1:.2f}, expected >= 0.60"
    assert mrr >= 0.70, f"MRR was {mrr:.2f}, expected >= 0.70"
