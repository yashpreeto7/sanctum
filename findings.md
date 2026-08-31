# Architecture & Design Findings: SovereignOS

## 1. Editorial Design Language: Old Regime Foundation
- **Font Stack**:
  - Display / Serif: `Playfair Display` (Classic architectural serif for headings, branding, numbers).
  - Primary UI / Sans: `Space Grotesk` (Geometric modernist typography).
  - Code / Stamps: `JetBrains Mono` (High-density telemetry, log feeds, index stamps).
- **Continuous Grid System & Sharp Corner Geometry**:
  - **Zero Border Radius (`border-radius: 0px !important`)**: Directly mirrors `oldregime.github.io`'s pure rectilinear blueprint drafting aesthetic by eliminating all pill/bubble rounding on cards, buttons, badges, modals, inputs, and tabs.
  - 1px hairline precision borders (`.seamless-card`, `.theme-card` with `var(--border-main)`).
  - Corner crosshairs (`.corner-crosshair` with `+` glyphs at cardinal corners).
  - Monospace eyebrow stamps (`[ 01 // OVERVIEW ]`, `[ 02 // COPILOT ]`, etc.).
  - Zero disjointed floating rounded cards; structural continuous architectural layout.

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
- **Theme Engine Inline Style Overlap Fix (Phase 13)**:
  - **Root Cause**: When a custom theme was saved or applied via `applyCustomThemeVariables()`, custom CSS variables (`--bg-base`, `--bg-card`, `--color-brand`, `--border-main`, etc.) were attached directly as inline styles onto `document.documentElement.style`. Because CSS inline styles have higher specificity than stylesheet attribute selectors (`[data-theme="..."]`), subsequent selection of pre-configured themes in `setThemePreset()` failed to override those inline properties until the page was refreshed.
  - **Solution**: Added `clearCustomThemeInlineStyles()` inside `setThemePreset()` to remove all custom inline properties from `document.documentElement.style` whenever switching to any non-custom pre-configured theme. Switching between custom themes and pre-configured themes is now immediate and clean without refreshing.

## 6. High-Performance Native Scroll Engine & Anti-Chaining
- **Native Hardware-Accelerated Scrolling**:
  - Removed third-party Lenis library which intercepted native wheel events on `#main-content-scroll` and locked scrolling when non-first views were active.
  - Enabled standard CSS `scroll-behavior: smooth;` and cross-browser thin scrollbar support (`scrollbar-width: thin; scrollbar-color: var(--border-main) transparent;`).
- **Anti-Chaining & Jitter Prevention**:
  - Bound `overscroll-behavior: contain;` and `-webkit-overflow-scrolling: touch;` on all scrollable sub-panels (`#chat-messages-box`, `#chat-sessions-list`, `#traces-list-container`, `#obsidian-notes-list-container`, `#obsidian-markdown-body`, `#spotlight-results-container`, modals, code blocks).
  - Scrolling inside sub-containers no longer chains or causes outer viewport bounce jitter.
- **Film Grain & Organic Texture**:
  - `.noise-overlay` using SVG fractal noise filter (`feTurbulence`) fixed across viewport with `mix-blend-mode: overlay` (dark themes) and `multiply` (light themes) at `0.035` opacity.
- **Dynamic Difference Follower Cursor**:
  - `#blend-cursor` with `.cur-dot` and `.cur-circle` utilizing lerp physics (`cx += (mx - cx) * 0.18`) and `mix-blend-mode: difference`.
  - Expands (`scale(1.65)`) over clickable elements (`button`, `a`, `.nav-item`, `.workspace-pill`, `.seamless-card`, `.theme-card`, `input`).
- **Multi-Layer Ambient Shadows & Specular Bevels**:
  - `--shadow-card`: 2-layer ambient occlusion + ground bounce shadow tailored to each theme's brand hue.
  - `--bevel-highlight`: 1px specular top rim lighting (`inset 0 1px 0 0 rgba(255,255,255,0.08)` / theme color).
  - Spring hover physics: `transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1)` with `transform: translateY(-2px)` on card hover and `scale(0.98)` on button click.

## 7. Persistence & Context Protocol
- Branch: `feature/research-ux-and-sidebar-toggle`.
- Local Memory: `task_plan.md`, `findings.md`, `progress.md`, `CONTEXT.md`.
- MCP Memory: `claude-mem` corpus `sovereign_os_context`.

