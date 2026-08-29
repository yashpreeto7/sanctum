# Task Plan: Personal AI OS

**Goal:** Build, test, and maintain the autonomous Personal AI OS architecture (Directives, Orchestration, Deterministic Execution, UI/Dashboard, Connectors, Traces & RAG).

## Current Phase: Active Development & System Stability
**Status:** in_progress

## Phases

### Phase 1: Environment & Robust Execution Safeguards
- **Status:** complete
- [x] Configure `GEMINI.md` with non-interactive CLI flags, anti-hanging safeguards, and persistent memory protocol.
- [x] Initialize on-disk working memory (`task_plan.md`, `findings.md`, `progress.md`).

### Phase 2: Local DeepSeek R1 Research Engine
- **Status:** complete
- [x] Wire `deepseek-r1:7b` as the default research reasoning model in `execution/core/config.py`.
- [x] Implement `<think>` Chain-of-Thought parsing, deep technical synthesis, dynamic Mermaid generation, and Obsidian/Vector indexing in `execution/tools/deep_researcher.py`.
- [x] Update `directives/deep_autonomous_research.md`.
- [x] Trigger Ollama download for `deepseek-r1:7b`.

### Phase 3: Core Components & Test Verification
- **Status:** complete
- [x] Run comprehensive 56-scenario test suite across RAG, LangGraph, Tools, Parsers, Traces, and Security Sandbox (100% pass rate).
- [x] Committed and pushed stable base to `origin/main`.

### Phase 4: Research UX, Full Document Formatting & Export Suite
- **Status:** complete
- [x] Created and branched to `feature/research-ux-and-sidebar-toggle`.
- [x] Implemented Left Dashboard hide/collapse toggle (`btn-toggle-sidebar`, sidebar header collapse chevron, `Ctrl+B` shortcut, full width expansion).
- [x] Upgraded markdown engine (`formatMarkdownText`) to parse complete GFM (headings hierarchy, styled tables, blockquotes, callout alerts `[!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!CAUTION]`, bullet/numbered lists, inline code, and Mermaid diagrams).
- [x] Upgraded Deep Autonomous Research reader with executive summary callout, collapsible DeepSeek R1 `<think>` reasoning trace, interactive Mermaid workflow cards, aspect breakdown cards, and verified citations.
- [x] Built export engine for **Save as Microsoft Word (.doc)**, **Save as PDF**, **Save as Markdown (.md)**, and **Copy to Clipboard** across Research Dossiers and Obsidian Notes.
- [x] Added `/api/research/dossier` endpoint to load past research notes directly into the rich dossier reader.
- [x] Verified test suite and pushed branch to `origin/feature/research-ux-and-sidebar-toggle`.

## Next Step
User test and review the interactive app on `feature/research-ux-and-sidebar-toggle`. If approved, merge into `main`.
