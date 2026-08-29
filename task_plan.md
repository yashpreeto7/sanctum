# Task Plan: SovereignOS (Personal AI OS)

**Goal:** Build, test, and maintain the autonomous SovereignOS architecture (Directives, Orchestration, Deterministic Execution, UI/Dashboard, Connectors, Traces & RAG).

## Current Phase: Active Development & Testing
**Status:** in_progress (on branch `feature/research-ux-and-sidebar-toggle`)

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

### Phase 5: SovereignOS UI/UX Overhaul, Professional Themes, Backdrops & Rebranding
- **Status:** complete
- [x] Rename app to **SovereignOS** across all branding, titles, Waybar status bar, and desktop launcher (`SovereignOS — Autonomous Executive Intelligence`).
- [x] Simplify naming structure to clean, professional titles (`Overview`, `Copilot`, `Traces`, `Inbox`, `Approvals`, `Topology`, `Memory`, `Vault`, `Schedule`, `Research`, `Documents`, `Settings`).
- [x] De-vibe-code card design: Linear / Apple Pro subtle borders (`border-white/[0.08]` / `border-slate-800`), inner top bevel highlights, cohesive typography.
- [x] Add 5 Sovereign Professional Themes: `Sovereign Slate`, `Titanium Onyx`, `Minimal Studio`, `Obsidian Gold`, and `Light Studio` while retaining the 8 Omarchy cyber presets.
- [x] Add 4 Professional Workstation Backgrounds: `Solid Minimal (0% CPU)`, `Technical Grid`, `Slate Ambient`, and `Titanium Studio`.
- [x] Modernize the Multi-Agent Pipeline Topology DAG map (`#view-topology`) with interactive SVG flow connectors, latency badges, and live simulation execution runner.
- [x] Fixed Light Studio high-contrast text and surface readability.
- [x] Built full interactive **Custom Theme Studio & Palette Creator** with live preview, preset starters, and JSON import/export.

### Phase 6: Old Regime Design Base, Fluid Edge-to-Edge Workspace & Dynamic Theming
- **Status:** complete
- [x] Applied **Old Regime design system** as foundational base: `Playfair Display` serif headers + `Space Grotesk` sans + `JetBrains Mono` code, 1px continuous precision grid borders, corner crosshair anchors (`+`), and monospace section stamps (`01 //`, `02 //`).
- [x] Added **Sovereign Manifesto** theme preset (cream parchment `#f5f0e8`, deep charcoal ink `#0a0a0a`, Swiss vermilion accent `#d42b2b`, brutalist 2px offset shadows).
### Phase 8: Old Regime 100% Sharp Blueprint Cornering Geometry
- **Status:** complete
- [x] Identified root cause of rounding discrepancy: eliminated all `rounded-2xl`, `rounded-xl`, `rounded-lg`, and `border-radius: 1rem` pill softening.
- [x] Enforced Old Regime pure rectilinear blueprint drafting geometry (`border-radius: 0px !important;`) across all cards, buttons, navigation items, workspace pills, modals, inputs, and badges in every theme.
- [x] Maintained circular status indicators (`.status-dot`, `.cur-dot`, `.avatar-circle`) while turning all structural containers into crisp cornered architectural units.

## Next Steps
- User hands-on testing of cornered blueprint architecture and tactile physics.
- On user approval, merge branch `feature/research-ux-and-sidebar-toggle` into `main`.


