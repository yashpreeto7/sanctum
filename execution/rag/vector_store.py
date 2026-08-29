"""Local Qdrant Vector Store interface with Sentence-Transformers embedding generation."""

import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from sentence_transformers import SentenceTransformer

from execution.core.config import settings


class DocumentChunk(BaseModel):
    """Container for an indexed chunk with metadata and timestamp."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    source_type: str = Field(..., description="email, obsidian, document, calendar, project")
    created_at_timestamp: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    score: Optional[float] = None


class LocalVectorStore:
    """Manages Qdrant vector database and embeddings locally."""

    DEFAULT_COLLECTION = "personal_knowledge"

    def __init__(
        self,
        storage_path: Optional[Path] = None,
        model_name: Optional[str] = None,
        in_memory: bool = False,
    ):
        self.model_name = model_name or settings.DEFAULT_EMBEDDING_MODEL
        self.embedding_model = SentenceTransformer(self.model_name)
        if hasattr(self.embedding_model, "get_embedding_dimension"):
            self.vector_dim = self.embedding_model.get_embedding_dimension()
        else:
            self.vector_dim = self.embedding_model.get_sentence_embedding_dimension()

        # Initialize Qdrant local client
        if in_memory:
            self.client = QdrantClient(location=":memory:")
        else:
            path = storage_path or settings.QDRANT_PATH
            path.mkdir(parents=True, exist_ok=True)
            try:
                self.client = QdrantClient(path=str(path))
            except Exception:
                # Fallback to in-memory if directory lock is temporarily contended
                self.client = QdrantClient(location=":memory:")

        self._ensure_collection(self.DEFAULT_COLLECTION)

    def _ensure_collection(self, collection_name: str) -> None:
        """Create collection if not already existing."""
        collections = [c.name for c in self.client.get_collections().collections]
        if collection_name not in collections:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=qmodels.VectorParams(
                    size=self.vector_dim,
                    distance=qmodels.Distance.COSINE,
                ),
            )

    def insert_chunks(self, chunks: List[Any], collection_name: Optional[str] = None) -> List[str]:
        """Embed and upsert chunks into Qdrant."""
        if not chunks:
            return []

        formatted_chunks: List[DocumentChunk] = []
        for c in chunks:
            if isinstance(c, DocumentChunk):
                formatted_chunks.append(c)
            elif isinstance(c, dict):
                formatted_chunks.append(
                    DocumentChunk(
                        id=str(c.get("id") or uuid.uuid4()),
                        text=c.get("text", ""),
                        source_type=c.get("source_type", c.get("metadata", {}).get("source", "document")),
                        metadata=c.get("metadata", {}),
                    )
                )

        coll = collection_name or self.DEFAULT_COLLECTION
        texts = [chunk.text for chunk in formatted_chunks]
        embeddings = self.embedding_model.encode(texts, show_progress_bar=False, convert_to_numpy=True)

        points = []
        for chunk, emb in zip(formatted_chunks, embeddings):
            payload = {
                "text": chunk.text,
                "source_type": chunk.source_type,
                "created_at_timestamp": chunk.created_at_timestamp,
                "metadata": chunk.metadata,
            }
            points.append(
                qmodels.PointStruct(
                    id=chunk.id,
                    vector=emb.tolist(),
                    payload=payload,
                )
            )

        self.client.upsert(collection_name=coll, points=points)
        return [c.id for c in chunks]

    def search_dense(
        self,
        query: str,
        limit: int = 20,
        source_type: Optional[str] = None,
        collection_name: Optional[str] = None,
    ) -> List[DocumentChunk]:
        """Perform dense semantic vector search."""
        coll = collection_name or self.DEFAULT_COLLECTION
        query_vector = self.embedding_model.encode(query, show_progress_bar=False, convert_to_numpy=True)

        query_filter = None
        if source_type:
            query_filter = qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="source_type",
                        match=qmodels.MatchValue(value=source_type),
                    )
                ]
            )

        search_results = self.client.query_points(
            collection_name=coll,
            query=query_vector.tolist(),
            query_filter=query_filter,
            limit=limit,
        ).points

        chunks = []
        for hit in search_results:
            payload = hit.payload or {}
            chunk = DocumentChunk(
                id=str(hit.id),
                text=payload.get("text", ""),
                source_type=payload.get("source_type", "unknown"),
                created_at_timestamp=payload.get("created_at_timestamp", time.time()),
                metadata=payload.get("metadata", {}),
                score=float(hit.score),
            )
            chunks.append(chunk)

        return chunks


# Singleton instance (in-memory for unit tests / disk path for production)
vector_store = LocalVectorStore()
