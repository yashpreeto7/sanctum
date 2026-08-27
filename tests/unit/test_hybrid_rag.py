"""Unit tests for Vector Store, Hybrid Retriever with Temporal Decay, and Cross-Encoder Reranker."""

import time
import pytest
from execution.rag.hybrid_retriever import HybridRetriever
from execution.rag.reranker import CrossEncoderReranker
from execution.rag.vector_store import DocumentChunk, LocalVectorStore


@pytest.fixture
def mock_in_memory_store():
    """Provides an isolated in-memory Qdrant store populated with test chunks."""
    store = LocalVectorStore(in_memory=True)

    now = time.time()
    one_day_ago = now - 86400.0
    thirty_days_ago = now - (30 * 86400.0)

    chunks = [
        DocumentChunk(
            text="DocDispatch API architecture: uses FastAPI, LangGraph, and Ollama Qwen local model.",
            source_type="obsidian",
            created_at_timestamp=one_day_ago,
            metadata={"title": "DocDispatch Spec"},
        ),
        DocumentChunk(
            text="Meeting notes from Rahul regarding the API deployment timeline and staging outage.",
            source_type="email",
            created_at_timestamp=now,
            metadata={"sender": "rahul@company.com"},
        ),
        DocumentChunk(
            text="Legacy Python 2 server notes from 2019 about old database migrations.",
            source_type="document",
            created_at_timestamp=thirty_days_ago,
            metadata={"title": "Archive"},
        ),
    ]

    store.insert_chunks(chunks)
    return store


def test_vector_store_dense_search(mock_in_memory_store):
    """Verify semantic dense search retrieves relevant chunks."""
    results = mock_in_memory_store.search_dense(query="API architecture with FastAPI and LangGraph", limit=2)
    assert len(results) >= 1
    assert "DocDispatch" in results[0].text


def test_hybrid_retriever_temporal_decay(mock_in_memory_store):
    """Verify hybrid retriever scores recent documents higher using exponential decay."""
    retriever = HybridRetriever(store=mock_in_memory_store, half_life_days=14.0)

    results = retriever.search(query="notes", top_k=3)
    assert len(results) == 3

    # Recent Rahul meeting notes should have higher recency score than 30-day legacy notes
    recent_chunk = next(r for r in results if "Rahul" in r.text)
    old_chunk = next(r for r in results if "Legacy" in r.text)

    assert recent_chunk.metadata["score_breakdown"]["recency"] > old_chunk.metadata["score_breakdown"]["recency"]
    assert recent_chunk.score > old_chunk.score


def test_cross_encoder_reranker_pruning(mock_in_memory_store):
    """Verify Cross-Encoder reranker selects the most accurate snippet."""
    retriever = HybridRetriever(store=mock_in_memory_store)
    candidates = retriever.search(query="Who sent meeting notes about the API deployment?", top_k=3)

    reranker = CrossEncoderReranker()
    top_ranked = reranker.rerank(
        query="Who sent meeting notes about the API deployment?",
        candidates=candidates,
        top_n=1,
    )

    assert len(top_ranked) == 1
    assert "Rahul" in top_ranked[0].text
