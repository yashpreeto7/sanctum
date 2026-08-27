"""Hybrid Retriever combining Dense Vector Search, BM25 Keyword Search, and Exponential Temporal Decay."""

import math
import time
from pathlib import Path
from typing import List, Optional
import numpy as np
from rank_bm25 import BM25Okapi

from execution.core.config import settings
from execution.rag.vector_store import DocumentChunk, LocalVectorStore, vector_store


KNOWLEDGE_VAULT_DIR = Path(__file__).resolve().parent.parent.parent / "directives" / "knowledge_vault"


class HybridRetriever:
    """Combines semantic vectors, exact keywords, and recency weighting."""

    def __init__(
        self,
        store: Optional[LocalVectorStore] = None,
        alpha_dense: float = 0.5,
        beta_bm25: float = 0.3,
        gamma_recency: float = 0.2,
        half_life_days: Optional[float] = None,
    ):
        self.store = store or vector_store
        self.alpha = alpha_dense
        self.beta = beta_bm25
        self.gamma = gamma_recency
        self.half_life_days = half_life_days or settings.TEMPORAL_DECAY_HALF_LIFE_DAYS
        self.decay_lambda = math.log(2.0) / max(0.1, self.half_life_days)
        if store is None:
            self._ensure_sample_vault_indexed()

    def _ensure_sample_vault_indexed(self) -> None:
        """Indexes sample knowledge from directives/knowledge_vault if collection is empty."""
        if not KNOWLEDGE_VAULT_DIR.exists():
            return
        chunks: List[DocumentChunk] = []
        for file_path in KNOWLEDGE_VAULT_DIR.glob("*.*"):
            if file_path.suffix.lower() in [".txt", ".md", ".json"]:
                try:
                    content = file_path.read_text(encoding="utf-8").strip()
                    if not content:
                        continue
                    sections = content.split("\n\n")
                    current_block = ""
                    for sec in sections:
                        if len(current_block) + len(sec) < 500:
                            current_block += "\n\n" + sec if current_block else sec
                        else:
                            if current_block:
                                chunks.append(
                                    DocumentChunk(
                                        text=current_block.strip(),
                                        source_type=f"file:{file_path.name}",
                                        metadata={"filename": file_path.name, "path": str(file_path)},
                                    )
                                )
                            current_block = sec
                    if current_block:
                        chunks.append(
                            DocumentChunk(
                                text=current_block.strip(),
                                source_type=f"file:{file_path.name}",
                                metadata={"filename": file_path.name, "path": str(file_path)},
                            )
                        )
                except Exception:
                    pass
        if chunks:
            self.store.insert_chunks(chunks)

    def calculate_temporal_score(self, created_at_timestamp: float, current_timestamp: Optional[float] = None) -> float:
        """Calculates exponential decay factor e^(-lambda * delta_days)."""
        now = current_timestamp or time.time()
        delta_seconds = max(0.0, now - created_at_timestamp)
        delta_days = delta_seconds / 86400.0
        return math.exp(-self.decay_lambda * delta_days)

    def search(
        self,
        query: str,
        top_k: int = 20,
        source_type: Optional[str] = None,
    ) -> List[DocumentChunk]:
        """Executes 3-factor hybrid retrieval: Dense + BM25 + Temporal Decay."""
        # 1. Retrieve initial candidate pool from vector store
        candidates = self.store.search_dense(query=query, limit=top_k * 2, source_type=source_type)
        if not candidates:
            return []

        # 2. Tokenize for BM25 ranking across the retrieved candidate corpus
        corpus_tokens = [c.text.lower().split() for c in candidates]
        query_tokens = query.lower().split()

        bm25 = BM25Okapi(corpus_tokens)
        bm25_raw_scores = bm25.get_scores(query_tokens)

        # Normalize BM25 scores to [0, 1] range
        max_bm25 = max(bm25_raw_scores) if max(bm25_raw_scores) > 0 else 1.0
        bm25_norm_scores = [float(s / max_bm25) for s in bm25_raw_scores]

        now = time.time()
        scored_chunks: List[DocumentChunk] = []

        for idx, chunk in enumerate(candidates):
            dense_score = chunk.score or 0.0
            bm25_score = bm25_norm_scores[idx]
            recency_score = self.calculate_temporal_score(chunk.created_at_timestamp, current_timestamp=now)

            hybrid_score = (self.alpha * dense_score) + (self.beta * bm25_score) + (self.gamma * recency_score)

            chunk.score = round(hybrid_score, 4)
            chunk.metadata["score_breakdown"] = {
                "dense": round(dense_score, 3),
                "bm25": round(bm25_score, 3),
                "recency": round(recency_score, 3),
            }
            scored_chunks.append(chunk)

        scored_chunks.sort(key=lambda c: (c.score or 0.0), reverse=True)
        return scored_chunks[:top_k]


# Singleton instance
hybrid_retriever = HybridRetriever()
