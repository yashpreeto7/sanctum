"""Cross-Encoder Learned Reranker for two-stage context pruning.

Reranks candidate chunks from hybrid retrieval down to top-N highest-precision snippets,
minimizing context window consumption and eliminating hallucinated context.
"""

from typing import List, Optional, Tuple
from sentence_transformers import CrossEncoder

from execution.core.config import settings
from execution.rag.vector_store import DocumentChunk


class CrossEncoderReranker:
    """Two-stage precision reranker using local Cross-Encoder models."""

    DEFAULT_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or self.DEFAULT_MODEL
        self._model: Optional[CrossEncoder] = None

    @property
    def model(self) -> CrossEncoder:
        """Lazy-load the Cross-Encoder weights on first invocation."""
        if self._model is None:
            self._model = CrossEncoder(self.model_name)
        return self._model

    def rerank(
        self,
        query: str,
        candidates: List[DocumentChunk],
        top_n: Optional[int] = None,
    ) -> List[DocumentChunk]:
        """Rerank candidate chunks by exact query-document token interactions."""
        if not candidates:
            return []

        limit = top_n or settings.RAG_RERANK_TOP_N
        pairs: List[Tuple[str, str]] = [(query, c.text) for c in candidates]

        try:
            scores = self.model.predict(pairs)
            for idx, score in enumerate(scores):
                candidates[idx].score = round(float(score), 4)
                candidates[idx].metadata["rerank_score"] = round(float(score), 4)

            candidates.sort(key=lambda c: (c.score or 0.0), reverse=True)
            return candidates[:limit]

        except Exception:
            # Graceful fallback: return top_n from initial hybrid retrieval order
            return candidates[:limit]


# Singleton instance
reranker = CrossEncoderReranker()
