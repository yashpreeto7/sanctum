# Directive: Deep Autonomous Research & Intelligence Engine (DeepSeek R1)

## Goal
Perform comprehensive, multi-step autonomous research on complex technical topics, open questions, and architectures. Leverage **local DeepSeek R1** reasoning models (via Ollama) to decompose queries, extract web documentation, perform deep `<think>` chain-of-thought technical synthesis, generate Mermaid workflows, and automatically index findings in the Obsidian vault and local vector store.

## Inputs
- **Research Topic / Inquiry**: (e.g., "Compare vLLM PagedAttention vs SGLang RadixAttention memory allocation", "Deep dive into FlashAttention-3 forward pass mechanics").
- **Research Depth**: 
  - `1`: Quick Overview (2 sub-aspects)
  - `2`: Standard Technical Deep-Dive (4 sub-aspects)
  - `3`: Exhaustive Architectural Dossier (Full multi-source crawl + R1 synthesis)
- **Model**: Local `deepseek-r1:7b` (default in `execution/core/config.py`).

## Execution Steps
1. **Query Decomposition**:
   - Break down target topic into structured sub-queries covering:
     - Architecture & Core Concepts
     - Mechanics & Internal Workings
     - Benchmarks & Trade-offs
     - Best Practices & Future Trends
2. **Multi-Source Evidence Extraction**:
   - Query web search for live documentation and technical snippets.
3. **DeepSeek R1 Technical Synthesis**:
   - Use local DeepSeek R1 to analyze the gathered evidence.
   - Separate `<think>` reasoning traces from the authoritative executive conclusions.
   - Synthesize architectural workflows into rendered **Mermaid diagrams**.
4. **Knowledge Persistence & Vector Indexing**:
   - Save formatted Markdown note to `Obsidian/Research/YYYY-MM-DD - <Topic>.md` with frontmatter tags `#research #deep-dive #deepseek-r1`.
   - Embed and index all sections in the local vector store for instant conversational RAG retrieval.

## Scripts Used
- `execution/tools/deep_researcher.py` — DeepSeek R1 autonomous researcher and synthesizer.
- `execution/tools/web_search_tool.py` — Web crawling & snippet extraction.
- `execution/tools/obsidian_connector.py` — Obsidian markdown note exporter.
- `execution/rag/vector_store.py` — Local vector indexing.

## Outputs
- Structured Markdown Dossier in Obsidian Vault (`Research/`).
- Interactive Mermaid diagrams and DeepSeek R1 reasoning traces.
- Embedded vector chunks available for Spotlight and Chat search.
