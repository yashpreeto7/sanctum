# Directive: Knowledge Retrieval, Hybrid RAG & Temporal Decay

## Goal
Retrieve personal context (emails, Obsidian notes, calendar events, project documents) using a two-stage hybrid retrieval pipeline that balances semantic meaning, exact keyword matching, and recency decay.

## Pipeline Architecture

```mermaid
flowchart TD
    Query[User Query / Inbound Message] --> DenseSearch[Qdrant Dense Vector Search: all-MiniLM-L6-v2]
    DenseSearch --> TopCandidates[Top 20-30 Candidate Chunks]
    TopCandidates --> BM25[BM25 Keyword Scoring]
    TopCandidates --> Decay[Exponential Recency Decay: e^-lambda*delta_days]
    BM25 & Decay & DenseSearch --> HybridFormula[Hybrid Score: 0.5*Dense + 0.3*BM25 + 0.2*Recency]
    HybridFormula --> TopHybrid[Top 10-15 Scored Chunks]
    TopHybrid --> CrossEncoder[Stage 2: Cross-Encoder Reranker ms-marco-MiniLM-L-6-v2]
    CrossEncoder --> FinalContext[Top 3 Precision Chunks into LLM Context]
```

## Tools & Modules
- **Vector Store**: `execution/rag/vector_store.py`
  - `insert_chunks(chunks)`: Ingests documents into local Qdrant collection with Sentence-Transformers embeddings.
  - `search_dense(query, limit)`: Fast vector cosine similarity search.
- **Hybrid Retriever**: `execution/rag/hybrid_retriever.py`
  - `search(query, top_k=20)`: Multi-factor scoring ($0.5 \cdot \text{Dense} + 0.3 \cdot \text{BM25} + 0.2 \cdot \text{Recency}$).
- **Cross-Encoder Reranker**: `execution/rag/reranker.py`
  - `rerank(query, candidates, top_n=3)`: Prunes candidates down to top 3 highest-scoring snippets using exact token-interaction cross-encoding.

## Temporal Decay Parameters
- **Half-life**: 14 days by default.
- A 2-day-old email receives a recency multiplier of $\approx 0.90$.
- A 60-day-old email receives a recency multiplier of $\approx 0.05$ unless strongly matched by semantic meaning and exact keywords.
