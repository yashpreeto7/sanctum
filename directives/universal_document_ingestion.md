# Directive: Universal Document Ingestion & Folder Watcher

## Goal
Automatically ingest, classify, parse, and summarize dropped documents (PDFs, CSVs, research papers, invoices, meeting docs, code snippets) from local folders (`data/inbox_drop/`), saving clean markdown notes to the Obsidian vault and indexing chunked text into Qdrant for semantic Hybrid RAG retrieval.

## Supported Document Types & Extraction Rules
1. **Research Papers & Technical Whitepapers (`.pdf`)**:
   - Extracts Title, Authors, Abstract, Core Methodology, Findings, and Conclusions.
   - Saves to `Obsidian/Documents/Papers/` with `#paper #research`.
2. **Invoices & Financial Receipts (`.pdf`, `.csv`, `.txt`)**:
   - Extracts Vendor, Total Amount, Date, Line Items, and Payment Status.
   - Saves to `Obsidian/Documents/Finance/` with `#invoice #finance`.
3. **Data Tables & Spreadsheets (`.csv`)**:
   - Parses column schema, row count, statistical distribution (mean, min, max, top categories), and preview records.
   - Saves to `Obsidian/Documents/Datasets/` with `#dataset #data`.
4. **General Documents & Specs (`.pdf`, `.md`, `.txt`)**:
   - Extracts executive summary, key sections, and actionable items.
   - Saves to `Obsidian/Documents/` with `#document`.

## Execution Steps
1. **Detection**: `FolderWatcher` detects new files in `data/inbox_drop/` or handles files uploaded via the UI.
2. **Parsing**: `DocumentParser` reads the file binary/text and runs tailored heuristics/LLM extraction.
3. **Vault Sync**: Creates a formatted markdown note with structured YAML frontmatter.
4. **Vector Store Ingestion**: Chunks document text with source metadata and inserts into Qdrant collection for instant Hybrid RAG search.

## Scripts Used
- `execution/tools/document_parser.py` — Multi-format parser (PDF, CSV, MD, TXT).
- `execution/tools/folder_watcher.py` — Background folder watcher and ingestion pipeline.
- `execution/tools/obsidian_connector.py` — Note persistence in Obsidian.
- `execution/rag/vector_store.py` — Vector indexing for Hybrid RAG.

## Outputs
- Structured Markdown note in local Obsidian vault.
- Searchable vector embeddings in Qdrant.
- Ingestion event trace emitted to the Command Center UI.
