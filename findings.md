# Architecture & Design Findings: SovereignOS

## 1. Editorial Design Language: Old Regime Foundation
- **Font Stack**:
  - Display / Serif: `Playfair Display` (Classic architectural serif for headings, branding, numbers).
  - Primary UI / Sans: `Space Grotesk` (Geometric modernist typography).
  - Code / Stamps: `JetBrains Mono` (High-density telemetry, log feeds, index stamps).
- **Continuous Grid System**:
  - 1px hairline precision borders (`.seamless-card` with `var(--border-main)`).
  - Corner crosshairs (`.corner-crosshair` with `+` glyphs at cardinal corners).
  - Monospace eyebrow stamps (`[ 01 // OVERVIEW ]`, `[ 02 // COPILOT ]`, etc.).
  - Zero disjointed floating rounded cards; structural continuous layout.

## 2. Dynamic Theming Engine & Color Architecture
- **Theme Variables**:
  - `--bg-base`: Core background surface.
  - `--bg-card`: Surface container background.
  - `--border-main`: Precision hairline border.
  - `--text-main`: High contrast primary text.
  - `--text-muted`: Secondary label text.
  - `--color-brand`: Dynamic brand accent (used for active buttons, badges, user bubbles).
- **Universal Input Rules**:
  - `input, textarea, select, #chat-input-textarea, #chat-search-input, #spotlight-search-input` dynamically bind to `color: var(--text-main) !important;` and placeholder to `var(--text-muted) !important;`. This resolves all light-theme text illegibility bugs.
- **Sovereign Manifesto Theme**:
  - Canvas: Cream parchment (`#f5f0e8`).
  - Ink: Deep charcoal (`#0a0a0a`).
  - Accent: Swiss vermilion (`#d42b2b`).
  - Secondary Accents: Cobalt blue (`#1a3dc4`), Golden amber (`#f5c518`).
  - Box Shadows: Brutalist 2px hard offset shadow (`2px 2px 0px rgba(10, 10, 10, 0.08)`).

## 3. Workspace Layout & Fluid Expansion
- **`.view-container` Standard**:
  - Removed rigid `max-w-7xl mx-auto` centering wrappers.
  - All workspace sections expand fluidly across 100% available viewport width.
  - Sidebar collapse (`#app-sidebar.collapsed` / `Ctrl+B`) triggers zero-gutter edge-to-edge content expansion.

## 4. Multi-Agent & Orchestration Stack
- **LangGraph State Graph**:
  - Nodes: `quarantine_gate`, `router`, `triage_agent`, `researcher`, `obsidian_vault`, `human_gatekeeper`.
  - Checkpointer: Local SQLite checkpointer store with step-by-step state inspection.
  - Security: Dual-LLM zero-tool isolation quarantine for untrusted inputs (emails, raw web content).
- **RAG Engine**:
  - Hybrid dense vector search + BM25 keyword matching + recency decay scoring.
  - Automatic indexing of all research dossiers and Obsidian notes.

## 5. Persistence & Context Protocol
- Branch: `feature/research-ux-and-sidebar-toggle`.
- Local Memory: `task_plan.md`, `findings.md`, `progress.md`, `CONTEXT.md`.
- MCP Memory: `claude-mem` corpus `sovereign_os_context`.
