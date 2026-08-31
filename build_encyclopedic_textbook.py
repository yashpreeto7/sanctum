"""
Encyclopedic 45-50+ Page Engineering Textbook & Technical Interview Master Guide.
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib import colors
from pdf_setup import get_styles, NumberedCanvas, COLOR_PRIMARY, COLOR_SECONDARY, COLOR_ACCENT, COLOR_BRAND, COLOR_PURPLE, COLOR_CARD_BG, COLOR_BG_LIGHT, COLOR_BORDER
from large_doc_helpers import create_section_header, make_qa, make_table

def build_encyclopedia():
    pdf_path = os.path.abspath("Yashpreet_Master_Interview_Preparation_Guide.pdf")
    md_path = os.path.abspath("INTERVIEW_PREPARATION_MASTER_GUIDE.md")

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )

    styles = get_styles()
    story = []
    md_lines = []

    def add_md(text):
        md_lines.append(text)

    # ══════════════════════════════════════════════════════════════════════════
    # COVER / HEADER BANNER
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Yashpreet — Technical Interview Master Engineering Compendium", styles['title']))
    story.append(Paragraph("Comprehensive 360° Technical Textbook & Interview Guide • SDE / Full-Stack / AI Systems", styles['subtitle']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_ACCENT, spaceBefore=2, spaceAfter=8))

    meta_table_data = [
        [
            Paragraph("<b>Candidate:</b> Yashpreet", styles['body']),
            Paragraph("<b>Degree:</b> B.Tech in CSE (VIT Bhopal, CGPA: 8.47/10)", styles['body']),
            Paragraph("<b>Graduation:</b> 2026", styles['body'])
        ],
        [
            Paragraph("<b>Email:</b> yash09preet@gmail.com", styles['body']),
            Paragraph("<b>GitHub:</b> github.com/yashpreeto7 (22 Repos)", styles['body']),
            Paragraph("<b>LinkedIn:</b> linkedin.com/in/yashpreeto7", styles['body'])
        ]
    ]
    meta_table = Table(meta_table_data, colWidths=[160, 220, 160])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_CARD_BG),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    add_md("# 🎓 Yashpreet — Technical Interview Master Engineering Compendium\n")
    add_md("**Candidate:** Yashpreet  \n**Education:** B.Tech in Computer Science and Engineering (VIT Bhopal University, CGPA: 8.47/10, Class of 2026)  \n**GitHub:** [github.com/yashpreeto7](https://github.com/yashpreeto7) | **Email:** yash09preet@gmail.com | **LinkedIn:** [linkedin.com/in/yashpreeto7](https://www.linkedin.com/in/yashpreeto7)\n\n---\n")

    # ──────────────────────────────────────────────────────────────────────────
    # CHAPTER 1: CANDIDATE POSITIONING & BEHAVIORAL PLAYBOOK (4-5 pages)
    # ──────────────────────────────────────────────────────────────────────────
    story.extend(create_section_header("Chapter 1: Candidate Positioning, Narrative & Behavioral STAR Playbook", "Comprehensive communication strategy and high-impact scenario breakdowns", styles))
    add_md("## Chapter 1: Candidate Positioning, Narrative & Behavioral STAR Playbook\n\n")

    story.append(Paragraph("1.1 The 90-Second High-Impact Self-Introduction", styles['h2']))
    pitch_text = (
        "<i>\"I am a final-year Computer Science undergraduate at VIT Bhopal with an 8.47 CGPA, specializing in "
        "full-stack distributed systems, API architecture, and autonomous AI engineering. Over the past two years, "
        "I've focused on engineering reliable, production-grade applications that combine modern web runtimes with local-first AI intelligence. "
        "Most recently, I engineered <b>SovereignOS</b>, an autonomous AI operating system powered by a 5-tier LangGraph state machine DAG, "
        "hybrid vector RAG (combining Qdrant dense embeddings with BM25 sparse keyword ranking via Reciprocal Rank Fusion), "
        "zero-shot prompt injection quarantine gates, and real-time word-by-word WebSocket streaming. "
        "Prior to that, I built <b>MacroLens Vision AI</b>, a full-stack nutrition platform with a serving-aware calculation engine "
        "across a 1,014 Indian food database and multimodal vision recognition, as well as <b>Pal-AI</b>, a provider-agnostic companion "
        "with token-budgeted sliding context memory. I love tackling hard systems problems—from eliminating async ASGI deadlocks to optimizing "
        "vector database indexing—and I'm excited to bring my engineering discipline to this role.\"</i>"
    )
    story.append(Paragraph(pitch_text, styles['callout']))
    story.append(Spacer(1, 8))
    add_md(f"### 1.1 The 90-Second High-Impact Self-Introduction\n\n> {pitch_text}\n\n")

    story.append(Paragraph("1.2 The Complete 15-Scenario Behavioral STAR Playbook", styles['h2']))
    add_md("### 1.2 The Complete 15-Scenario Behavioral STAR Playbook\n\n")

    star_15 = [
        ("1. Hardest Technical Bug Overcome (Async Concurrency & Deadlocks)",
         "During development of SovereignOS, streaming responses over WebSockets while background sub-agents performed external tool calls caused intermittent event loop starvation. First-token latency spiked to 4.2 seconds and occasionally deadlocked Uvicorn workers.",
         "I profiled the ASGI event loop using `asyncio` task inspection. I identified that synchronous subprocess I/O in the legacy tool runner was blocking the main thread. I re-architected the pipeline to use LangGraph's native `astream_events(version='v1')`, decoupled background tool execution into dedicated thread pools using `asyncio.to_thread`, and implemented non-blocking WebSocket queues.",
         "First-token latency dropped from 4.2s to 120ms with steady 55 tokens/sec emission. 100% of event loop deadlocks were permanently resolved under load tests."),

        ("2. Resolving Ambiguity in Architectural Design (Search Engine)",
         "Needed to design the retrieval engine for SovereignOS to search across local personal notes, code snippets, and structured calendar events. Plain dense vector embeddings were failing on exact code identifiers and dates.",
         "Researched modern IR techniques and implemented a Hybrid Search architecture. Combined Qdrant dense vector cosine similarity (using `all-MiniLM-L6-v2`) with a BM25 sparse lexical inverted index. Merged rankings using Reciprocal Rank Fusion (RRF with k=60).",
         "Search recall jumped by 34% compared to pure dense search, particularly for alphanumeric tokens, function names, and ISO dates."),

        ("3. Handling Security & Adversarial Attacks (Prompt Injection)",
         "Private desktop automations (e.g. deleting files, sending emails) exposed the local environment to catastrophic indirect prompt injections when reading untrusted emails or web pages.",
         "Engineered a multi-tier Quarantine Security Gate (`execution/security/quarantine.py`). Integrated fast regex heuristics, canary token validation, zero-shot LLM classification, and an asynchronous Human-In-The-Loop (HITL) approval token gate for high-risk tool calls.",
         "Neutralized 100% of adversarial prompt injection test suites without degrading system throughput for normal queries."),

        ("4. Tight Deadlines & Rapid Delivery (Anthropic MCP Integration)",
         "Anthropic released the Model Context Protocol (MCP) standard, and I wanted SovereignOS to support standardized tool servers without existing Python MCP client libraries for our stack.",
         "Read the JSON-RPC 2.0 stdio wire specifications directly. Built a custom `MCPClient` and `MCPManager` from scratch in Python to spawn background MCP server processes, handshake over stdio, and dynamically translate tool schemas into agent functions.",
         "Delivered full Filesystem and SQLite MCP tool support within 48 hours, demonstrating rapid prototyping and standard compliance."),

        ("5. Performance Optimization (MongoDB Aggregation Pipelines)",
         "In MacroLens Vision AI, computing 30-day rolling macronutrient and micronutrient totals across user meal histories was causing 800ms query latency on dashboard page loads.",
         "Analyzed query execution plans using `explain('executionStats')`. Identified full-collection scans. Created a compound index on `{ userId: 1, date: -1 }` and restructured the aggregation pipeline to filter first (`$match`), then unwind and group (`$group`), eliminating redundant memory stages.",
         "Reduced dashboard query latency from 800ms to 11ms (a 98.6% speedup), dramatically improving perceived user experience."),

        ("6. Disagreement on Technical Approach (State Management)",
         "During a team frontend project, a peer proposed using prop drilling and component-level state across 6 nested modal levels for an appointment booking flow, while I advocated for Redux Toolkit.",
         "Rather than arguing abstractly, I created a minimal branch comparison demonstrating how Redux Toolkit with RTK Query eliminated 200 lines of boilerplate, centralized loading/error states, and prevented unnecessary re-renders in nested components.",
         "The team adopted Redux Toolkit, resulting in cleaner code reviews and zero state synchronization bugs during QA testing."),

        ("7. Handling a Production Incident / Edge Case (Calendar Sync)",
         "Users reported that deleting calendar events offline in SovereignOS caused deleted events to reappear when the network reconnected (event resurrection bug).",
         "Identified that the sync engine performed blind upserts from local cache without tracking deletion tombstones. Implemented a dedicated `deleted_calendar_events.json` tombstone ledger with composite keys `(summary, start_time[:16])`. Updated sync logic to execute remote deletions before upserting active records.",
         "Completely eliminated zombie event resurrection across all network disconnect/reconnect cycles."),

        ("8. Taking Ownership Beyond Assigned Scope (Accessibility Compliance)",
         "In DocDispatch, accessibility was not initially specified in the project requirements, but I noticed the healthcare portal was completely unusable with screen readers and keyboard navigation.",
         "Took the initiative to audit the entire component library against WCAG 2.1 AA standards. Added semantic HTML5 landmarks, ARIA labels, keyboard focus trapping on modals, and tested with NVDA screen readers.",
         "Achieved 100% accessibility audit score, ensuring compliant and inclusive access for healthcare patients with motor and visual impairments."),

        ("9. Learning a New Technology Under Pressure (LangGraph State Machines)",
         "Traditional LangChain chains were too brittle for cyclic multi-step reasoning with error recovery. Needed to transition to LangGraph which had just been released.",
         "Read source code, experimented with state graph channels, TypedDict reducers, and checkpointing mechanisms. Built proof-of-concept cyclic graphs with conditional edges and approval interrupts.",
         "Successfully migrated SovereignOS to LangGraph, enabling robust cyclic self-correction loops and thread-isolated session checkpointing."),

        ("10. Making Tough Engineering Trade-offs (Local vs Cloud LLM Inference)",
         "Faced a trade-off between the high reasoning power of 70B+ cloud models vs the privacy and zero cost of local 7B models on consumer hardware.",
         "Engineered a hybrid inference architecture: lightweight intent classification and sensitive private tasks run locally via Ollama (Qwen 2.5 7B) at 0 cost and 100% privacy, while complex multi-step reasoning gracefully falls back to Gemini 2.5 Flash / OpenRouter when cloud keys are present.",
         "Delivered an optimal balance of strict data privacy, offline autonomy, and frontier intelligence when available."),

        ("11. Refactoring Legacy Technical Debt",
         "In the initial prototype of SovereignOS, all REST endpoints and WebSocket handlers were bundled in a single monolithic 1,200-line script with global mutable variables.",
         "Refactored the codebase into modular domain layers: API routers, orchestration state machines, security guardrails, RAG retrievers, and tool connectors. Introduced dependency injection and Pydantic schemas.",
         "Eliminated 100% of global state side-effects and enabled independent unit testing for every connector."),

        ("12. Overcoming Incomplete API Documentation",
         "While integrating the Google Calendar API offline cache, found that the official SDK lacked clear patterns for delta sync and local tombstone tracking.",
         "Inspected the raw RFC 5545 iCalendar specification and Google API HTTP change-log headers. Built a custom synchronization manager that computes delta patches locally using composite keys.",
         "Built a robust bidirectional sync engine capable of operating seamlessly during extended offline periods."),

        ("13. Handling Critical Feedback from Code Reviews",
         "In an earlier project, a senior engineer noted that my API endpoints lacked proper input sanitization and rate limiting, leaving them open to denial-of-service.",
         "Took the feedback constructively. Researched OWASP Top 10 web security best practices, implemented Express rate limiters with Redis sliding window counters, and introduced Zod schema validation across all routes.",
         "The updated API passed automated penetration testing with zero critical vulnerabilities."),

        ("14. Managing Multiple Competing Priorities",
         "Had to juggle academic coursework, competitive programming DSA practice, and delivering sprint milestones for SovereignOS simultaneously.",
         "Adopted a strict time-boxing framework: morning 2-hour deep work blocks for DSA problem solving, afternoons for academic labs, and evening focused sprints with clear GitHub issue milestones for project engineering.",
         "Maintained an 8.47 CGPA while completing 22 GitHub repositories and solving 150+ complex algorithmic challenges."),

        ("15. Mentoring and Pair Programming",
         "Assisted junior peers at VIT Bhopal who were struggling with understanding async JavaScript promises and React component lifecycle re-renders.",
         "Conducted interactive pair-programming sessions breaking down the JavaScript Event Loop, microtask queues, and hooks dependency arrays with visual execution diagrams.",
         "Mentees successfully built their full-stack capstone projects and improved their debugging speed by over 50%.")
    ]

    for title, s_t, a, r in star_15:
        story.append(Paragraph(f"<b>{title}</b>", styles['h3']))
        table_content = [
            [Paragraph("<b>Situation & Task:</b>", styles['body_bold']), Paragraph(s_t, styles['body'])],
            [Paragraph("<b>Action Taken:</b>", styles['body_bold']), Paragraph(a, styles['body'])],
            [Paragraph("<b>Result & Impact:</b>", styles['body_bold']), Paragraph(r, styles['body'])]
        ]
        t = Table(table_content, colWidths=[110, 430])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), COLOR_CARD_BG),
            ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
            ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t)
        story.append(Spacer(1, 4))
        add_md(f"#### {title}\n- **Situation & Task:** {s_t}\n- **Action:** {a}\n- **Result & Metric:** {r}\n\n")

    # ──────────────────────────────────────────────────────────────────────────
    # CHAPTER 2 & 3: SOVEREIGN OS EXHAUSTIVE BLUEPRINT & 30 DEEP Q&AS (12-14 pages)
    # ──────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 2: SovereignOS — Flagship Engineering Reference Manual", "Exhaustive file-by-file codebase walkthrough, state graph DAG, and 30 deep interview Q&As", styles))
    add_md("## Chapter 2: SovereignOS — Flagship Engineering Reference Manual\n\n")

    story.append(Paragraph("2.1 High-Level Architecture & 5-Tier State Machine Blueprint", styles['h2']))
    arch_blueprint = (
        "<b>SovereignOS</b> is a local-first autonomous command center and automation engine built on a 5-tier hybrid state machine architecture. "
        "Unlike simple wrapper apps that make synchronous single-turn LLM calls, SovereignOS coordinates security evaluation, intent triaging, "
        "hybrid retrieval, reasoning with tool planning, human-in-the-loop safety gating, and sandboxed tool execution over an asynchronous state graph.<br/><br/>"
        "<b>Architectural Flow:</b><br/>"
        "1. <b>Client Ingestion:</b> Audio voice transcriptions or text prompts arrive via WebSockets at `/ws/chat`.<br/>"
        "2. <b>Quarantine Gate (Node 1):</b> Evaluates input for prompt injection and assigns security risk score.<br/>"
        "3. <b>Triaging Node (Node 2):</b> Determines whether query is conversational chit-chat vs complex desktop automation.<br/>"
        "4. <b>Hybrid RAG (Node 3):</b> Queries Qdrant dense vectors (384-dim) + BM25 sparse index with Reciprocal Rank Fusion.<br/>"
        "5. <b>Reasoning Node (Node 4):</b> Multi-agent reasoning generates structured tool-call JSON via Qwen 2.5 7B / Gemini Flash.<br/>"
        "6. <b>HITL Safety Gate (Node 5):</b> Pauses DAG execution for high-risk operations until user confirmation token arrives.<br/>"
        "7. <b>Tool Execution (Node 6):</b> Executes sandboxed tools (Google Calendar, Gmail, Obsidian AST, MCP servers) and loops results back."
    )
    story.append(Paragraph(arch_blueprint, styles['body']))
    story.append(Spacer(1, 8))
    add_md(f"### 2.1 High-Level Architecture & 5-Tier State Machine Blueprint\n\n{arch_blueprint}\n\n")

    story.append(Paragraph("2.2 File-by-File Codebase Deep Dive", styles['h2']))
    add_md("### 2.2 File-by-File Codebase Deep Dive\n\n")

    codebase_10_files = [
        ("server/app.py (FastAPI Gateway & WebSocket Streaming)",
         "• <b>ASGI Lifespan Management:</b> Initializes database connection pools, mounts static asset directories, and launches background daemons on startup.<br/>"
         "• <b>WebSocket Handler:</b> Subscribes to LangGraph's `astream_events(version='v1')`, pushing structured JSON packets (`node_progress`, `tool_start`, `token`, `done`) with 18ms word-by-word streaming intervals (~55 words/sec).<br/>"
         "• <b>REST Endpoints:</b> Provides `/api/calendar/event` (GET, POST, PUT, DELETE), `/api/approvals/{id}/decision` (POST), and `/api/chat/history` (GET)."),

        ("execution/orchestration/agent_engine.py (LangGraph State Machine DAG)",
         "• <b>AgentState Schema:</b> TypedDict managing `messages: Annotated[list, add_messages]`, `context_docs: list[str]`, `planned_tool: str`, `tool_args: dict`, `approval_required: bool`, `risk_level: str`.<br/>"
         "• <b>Cyclic Graph Compilation:</b> Connects conditional routing edges, error recovery loops, and `MemorySaver` checkpoints for resilient state persistence across server restarts."),

        ("execution/security/quarantine.py (Quarantine Security Gate)",
         "• <b>Canary Token Injection:</b> Injects high-entropy random GUID canary tokens into system prompt boundaries. Halts execution if output attempts to leak canary strings.<br/>"
         "• <b>Regex AST Heuristics:</b> Matches malicious prompt injection patterns ('ignore previous instructions', 'system override', 'reveal system prompt').<br/>"
         "• <b>Risk Scoring:</b> Categorizes queries into LOW, MEDIUM, and HIGH risk levels to determine approval policies."),

        ("execution/rag/hybrid_retriever.py (Hybrid Vector Search Engine)",
         "• <b>Dense Vector Search:</b> Embeds queries using `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions) and performs cosine similarity search over local Qdrant collections.<br/>"
         "• <b>Sparse Lexical Search:</b> Inverted index scored using BM25 ($k_1=1.5, b=0.75$).<br/>"
         "• <b>Reciprocal Rank Fusion (RRF):</b> Merges dense and sparse rankings: $RRF(d) = \\sum \\frac{1}{60 + rank_i(d)}$ to eliminate keyword blindness on technical terms and exact dates."),

        ("execution/tools/calendar_connector.py (Offline-First Calendar Engine)",
         "• <b>Composite Keys:</b> Indexes events locally by composite tuple `(summary, start_time[:16])` to prevent duplication.<br/>"
         "• <b>Tombstone Ledger:</b> Offline deletions append records to `deleted_calendar_events.json`. Sync engine deletes remote events first before upserting active items."),

        ("execution/tools/gmail_connector.py (Gmail Triage & Dispatch Engine)",
         "• <b>MIME Decoding:</b> Parses raw RFC 2822 base64url payloads and extracts plain text from multi-part MIME structures.<br/>"
         "• <b>Contextual Reply Generation:</b> Classifies emails by urgency and synthesizes 1-click reply drafts saved into Obsidian daily notes."),

        ("execution/tools/obsidian_workspace.py (Obsidian Vault Markdown Engine)",
         "• <b>Markdown AST Parsing:</b> Extracts YAML frontmatter metadata (tags, created_date, status).<br/>"
         "• <b>Header-Level Chunking:</b> Slices notes along `# H1` and `## H2` header boundaries to preserve semantic section integrity."),

        ("execution/tools/mcp_manager.py (Model Context Protocol Host)",
         "• <b>Stdio JSON-RPC 2.0 Transport:</b> Launches sandboxed background MCP servers (`@modelcontextprotocol/server-filesystem`, `@modelcontextprotocol/server-sqlite`).<br/>"
         "• <b>Dynamic Tool Discovery:</b> Calls `tools/list` on handshake and dynamically mounts tools into the agent graph."),

        ("execution/tools/folder_watcher.py (Automated Document Ingestion)",
         "• <b>Filesystem Observers:</b> Uses `watchdog` to listen for file drop events.<br/>"
         "• <b>Debounced Parsing:</b> Verifies file write completion before parsing `.pdf`, `.txt`, `.md`, `.json` files and indexing into Qdrant."),

        ("server/dashboard_template.py (Reactive Cyber HUD Frontend)",
         "• <b>Pure Native JS:</b> Zero-dependency reactive DOM rendering.<br/>"
         "• <b>Web Audio Visualizer:</b> Connects `AnalyserNode` to render real-time CAVA-style frequency spectrum on canvas.<br/>"
         "• <b>Calendar Multi-View:</b> Interactive Month Grid, 7-Day Week columns, and Agenda feed.")
    ]

    for title, desc in codebase_10_files:
        story.append(Paragraph(f"<b>{title}</b>", styles['h3']))
        story.append(Paragraph(desc, styles['body']))
        story.append(Spacer(1, 4))
        add_md(f"#### {title}\n{desc.replace('<b>', '**').replace('</b>', '**').replace('<br/>', '\n')}\n\n")

    # ──────────────────────────────────────────────────────────────────────────
    # 30 DEEP TECHNICAL Q&AS ON SOVEREIGN OS
    # ──────────────────────────────────────────────────────────────────────────
    story.append(Paragraph("2.3 Top 30 Technical Interview Q&As on SovereignOS", styles['h2']))
    add_md("### 2.3 Top 30 Technical Interview Q&As on SovereignOS\n\n")

    sovereign_30_qa = [
        ("Q1: Why did you choose LangGraph over traditional linear LangChain chains or while-loops?",
         "Traditional LangChain chains enforce a unidirectional, deterministic execution flow. Real-world autonomous agents require non-deterministic branching, cyclic self-correction loops (retrying failed tool calls with revised arguments), and asynchronous human-in-the-loop pauses. LangGraph models the system as a stateful cyclic graph where nodes are functions and edges are conditional transitions. It provides first-class state checkpointing (resuming across server restarts) and fine-grained event streaming hooks (`astream_events`)."),

        ("Q2: Explain the mathematics and engineering rationale behind your Hybrid RAG (Qdrant + BM25 + RRF).",
         "Dense vector search computes cosine similarity: $\\text{sim}(u, v) = \\frac{u \\cdot v}{\\|u\\| \\|v\\|}$. While effective for broad semantic concepts ('improving sleep' $\\rightarrow$ 'sleep hygiene'), dense embeddings fail on exact alphanumeric tokens (function names like `astream_events`, dates, error codes). BM25 uses term frequency and inverse document frequency: $\\text{BM25}(D, Q) = \\sum \\text{IDF}(q_i) \\cdot \\frac{f(q_i, D) \\cdot (k_1 + 1)}{f(q_i, D) + k_1 \\cdot (1 - b + b \\cdot \\frac{|D|}{\\text{avgdl}})}$. I combine both using Reciprocal Rank Fusion: $\\text{RRF}(d) = \\sum_{m} \\frac{1}{60 + \\text{rank}_m(d)}$, ensuring exact matches rank #1 while semantic context fills remaining slots."),

        ("Q3: How does WebSocket token streaming work in SovereignOS without blocking the ASGI event loop?",
         "The WebSocket route in `server/app.py` subscribes to LangGraph's `astream_events(version='v1')`. When graph nodes transition, lightweight JSON packets (`node_progress`) are pushed immediately to update UI indicators. When reasoning completes, text tokens are emitted word-by-word at 18ms intervals (~55 words/sec) via custom `token` events. All background tasks and tool executions are dispatched as non-blocking `asyncio` coroutines, preventing event loop starvation."),

        ("Q4: How did you solve the 'Zombie Event Resurrection' bug in offline calendar synchronization?",
         "Offline calendar systems often suffer from deleted events reappearing after sync. I implemented a two-pronged solution: (1) Indexed every event locally by a composite key `(summary, start_time[:16])`; (2) Created a dedicated tombstone file `deleted_calendar_events.json`. During sync, the daemon processes tombstones first to delete remote events on Google Calendar before executing upsert passes for active events, guaranteeing zero resurrecting zombies."),

        ("Q5: What is Model Context Protocol (MCP) and how does SovereignOS implement both Host and Client roles?",
         "MCP is an open standard created by Anthropic that standardizes how AI agents discover and execute tools using JSON-RPC 2.0 over standard I/O (`stdio`). SovereignOS implements an `MCPManager` that spawns isolated background worker processes (e.g. `@modelcontextprotocol/server-filesystem`), calls `tools/list` on handshake, translates tool schemas into the agent's LLM function definitions, and dispatches calls via `tools/call` over stdin/stdout pipes."),

        ("Q6: How does the Quarantine Security Gate detect and prevent Prompt Injection?",
         "Quarantine employs a defense-in-depth architecture: (1) **Static Heuristics:** Regex filters for known escape patterns ('ignore previous instructions', 'system prompt override'); (2) **Zero-Shot Canary Tokens:** High-entropy GUID tokens injected into system instructions; if an LLM response contains the canary token, execution is terminated immediately; (3) **Policy Gate:** High-risk actions (file deletion, mass email dispatch) require cryptographic approval tokens verified via Human-in-the-Loop approval."),

        ("Q7: How do you handle local LLM inference latency on consumer hardware with Qwen 2.5 7B?",
         "Running local 7B models can encounter memory-bandwidth bottlenecks. I optimized inference by: (1) Using 4-bit / 8-bit quantized GGUF weights in Ollama, reducing VRAM usage to under 5.5GB; (2) Pre-filtering user queries with a lightweight 1.5B intent classifier so trivial chit-chat skips heavy tool-calling pipelines; (3) Offloading token streaming to non-blocking generators so the user perceives immediate response start (TTFT < 150ms)."),

        ("Q8: How does the Obsidian Markdown AST parser work and why is heading-level chunking superior?",
         "Naive RAG splitters use fixed-character windows with overlap, frequently splitting sentences or code blocks midway. In `obsidian_workspace.py`, I parse notes using a Markdown Abstract Syntax Tree (AST). The parser extracts YAML frontmatter metadata and chunks content along `# H1` and `## H2` header boundaries. Each chunk forms a complete, self-contained semantic unit with its parent document hierarchy preserved in metadata."),

        ("Q9: What happens if an MCP server crashes or hangs during tool execution?",
         "In `execution/tools/mcp_client.py`, every tool invocation is wrapped in an `asyncio.wait_for(timeout=15.0)` boundary. If an MCP subprocess fails to respond or crashes, the client intercepts the timeout/broken pipe exception, logs telemetry to SQLite, terminates the orphaned process, and returns a structured error object back to LangGraph's reasoning node for automatic retry or graceful degradation."),

        ("Q10: Explain the Human-in-the-Loop (HITL) approval architecture in SovereignOS.",
         "When Node 4 proposes a destructive tool call (e.g. `delete_file`, `send_email`), Node 5 (HITL Gate) intercepts the payload, generates a cryptographically secure UUID `approval_id`, registers it in an active memory store with a 5-minute TTL, and yields an `approval_required` WebSocket event. The graph pauses at this checkpoint. When the user clicks 'Approve' on the UI, `POST /api/approvals/{id}/decision` resolves the token and resumes graph execution from the exact checkpoint."),

        ("Q11: How do you manage conversation session persistence across server restarts?",
         "Chat sessions and messages are persisted in a local SQLite database (`data/chat_history.db`) using WAL (Write-Ahead Logging) mode for concurrent read/write throughput. On startup, the UI auto-restores the last active session ID from `localStorage`, queries `GET /api/chat/history?session_id=...`, and repopulates the message DOM seamlessly."),

        ("Q12: How does the background Folder Watcher avoid ingesting partially-written files?",
         "The `FolderWatcher` uses the `watchdog` library to listen for `on_created` and `on_modified` OS filesystem events. To prevent reading half-copied large files, it implements a debounce delay: the worker verifies that the file size remains unchanged across two consecutive checks (500ms apart) and confirms non-exclusive file lock acquisition before passing the file to the document parser and vectorizer."),

        ("Q13: What embedding model do you use and what are the trade-offs of embedding dimensions?",
         "I use `sentence-transformers/all-MiniLM-L6-v2` which produces 384-dimensional dense vectors. While 1536-dim models (e.g. OpenAI `text-embedding-3-small`) offer marginal gains on massive public benchmarks, `all-MiniLM-L6-v2` executes in <15ms on local CPU, consumes 75% less VRAM/disk storage in Qdrant, and achieves 99%+ of the semantic retrieval accuracy when paired with BM25 hybrid ranking."),

        ("Q14: Explain the Web Audio spectrum visualizer implementation in the dashboard.",
         "The HUD dashboard features a real-time audio visualizer styled after CAVA. It connects to the Web Audio API via `AudioContext` and `AnalyserNode` with an FFT size of 64 (`fftSize = 64`). An `animationFrame` loop reads `getByteFrequencyData()`, normalizes frequency amplitudes across 16 frequency bands, and renders animated neon cyan bars on a `<canvas>` element with 60 FPS smoothness."),

        ("Q15: How does the Gmail connector handle OAuth2 token expiration and refresh?",
         "The `GmailConnector` loads credentials from `token.json`. If the access token is expired, it uses the Google OAuth2 `InstalledAppFlow` and refresh token to execute a non-blocking `creds.refresh(Request())` call in the background, writes updated tokens back to disk, and transparently retries the failed API call without interrupting user workflows."),

        ("Q16: How do you prevent context window exhaustion during long multi-turn conversations?",
         "SovereignOS enforces a token-budgeted sliding window. The state machine monitors token counts using `tiktoken`. When message history exceeds 70% of the model's context capacity, an asynchronous node triggers a summarization prompt over older turns, compressing past context into a structured summary block injected into system instructions while retaining the last 5 turns verbatim."),

        ("Q17: What design patterns are used throughout the SovereignOS codebase?",
         "Key design patterns include: (1) **State Pattern / State Machine:** LangGraph DAG modeling agent phases; (2) **Adapter Pattern:** Wrapping MCP, Google APIs, and local tools into a unified `BaseTool` interface; (3) **Observer Pattern:** Filesystem folder watcher emitting ingestion events; (4) **Factory Pattern:** LLM client factory selecting between Ollama, Gemini, and OpenRouter runtimes; (5) **Singleton Pattern:** Database connection pools and WebSocket connection manager."),

        ("Q18: How does SovereignOS handle rate limits when falling back to Cloud LLM APIs?",
         "When routing requests to Gemini Flash or OpenRouter, API calls are wrapped with an exponential backoff retry decorator using jitter: $\\text{Delay} = 2^{\\text{attempt}} \\times \\text{base} + \\text{uniform}(0, 1)$. If HTTP 429 (Too Many Requests) is returned, the system retries up to 3 times before automatically falling back to the local Ollama instance with a user notification."),

        ("Q19: How do you ensure idempotent tool executions in agent retry loops?",
         "Every planned tool call receives a deterministic `action_fingerprint = SHA256(tool_name + sorted_args + session_id)`. Before executing a tool, the engine checks an in-memory execution cache. If an identical fingerprint was executed within the current turn, the cached result is returned immediately, preventing duplicate email sends or calendar additions during retry loops."),

        ("Q20: What are the primary scalability bottlenecks of SovereignOS and how would you scale it to multi-user enterprise?",
         "The current architecture is optimized for single-user desktop privacy. To scale to a multi-tenant enterprise system: (1) Replace SQLite with PostgreSQL / TimescaleDB with connection pooling (PgBouncer); (2) Transition local Qdrant to a distributed Qdrant cluster with sharded collections; (3) Decouple agent graph execution from the web server using Celery/RabbitMQ or Redis Streams worker pools; (4) Introduce role-based access control (RBAC) and OAuth2 OIDC multi-tenancy."),

        ("Q21: Explain how the 3-Way Calendar switcher (Month, Week, Agenda) is implemented in vanilla JavaScript.",
         "The calendar switcher avoids bulky external libraries. In `dashboard_template.py`: (1) **Month View:** Dynamically computes `firstDayIndex` and `totalDays` for the active month, rendering a 7x6 CSS grid with day numbers and badges; (2) **Week View:** Calculates the 7 dates centered on the current week, rendering 7 vertical columns with time slots from 08:00 to 20:00; (3) **Agenda View:** Sorts all upcoming events chronologically and maps them to clean interactive cards. State changes update a single `currentCalendarView` enum and trigger a fast DOM redraw."),

        ("Q22: How does the Smart Inbox split-view reading pane operate?",
         "The Smart Inbox uses a responsive 2-column flexbox layout: left column contains the scrollable email list with unread badges, sender, subject, and time; right column renders the full reading pane. Clicking an email triggers `selectEmail(id)`, which populates the reading pane, generates an inline 1-click AI draft reply using the contextual reply endpoint, and provides an Obsidian note exporter."),

        ("Q23: How do you handle Cross-Origin Resource Sharing (CORS) security in FastAPI?",
         "In `server/app.py`, CORS is configured via `CORSMiddleware`. In development, `allow_origins=['*']` permits frontend testing; in production, `allow_origins` is restricted strictly to authorized origins (e.g. `http://localhost:8000`), with `allow_credentials=True`, `allow_methods=['GET', 'POST', 'PUT', 'DELETE']`, and explicit allowed headers to prevent cross-origin authorization token theft."),

        ("Q24: What is the purpose of the Executive Briefing cron daemon?",
         "In `execution/orchestration/scheduler.py`, a background cron scheduler wakes up at designated intervals (e.g. 08:00 daily). It queries unread emails, today's calendar events, and overdue tasks, prompts the reasoning LLM to synthesize a concise 3-paragraph executive briefing, saves the result to `data/latest_briefing.json`, and writes a formatted markdown summary into the Obsidian `Daily Notes/` folder."),

        ("Q25: How does LangGraph handle state channel reducers?",
         "In LangGraph, channels define how state updates from individual nodes merge into the global state. In `AgentState`, `messages: Annotated[list, add_messages]` uses the `add_messages` reducer. When a node returns `{'messages': [new_message]}`, the reducer automatically appends the message to the conversation history list rather than overwriting existing turns, preserving multi-turn context."),

        ("Q26: What is the difference between Synchronous and Asynchronous MCP servers?",
         "Synchronous MCP servers block the transport pipe while executing long-running tools, causing timeouts on the client. SovereignOS implements asynchronous non-blocking MCP execution: requests are assigned unique JSON-RPC request IDs (`id: 101`), dispatched over stdio, and registered in a pending future dictionary. The main event loop continues processing other tasks while awaiting the response notification."),

        ("Q27: How do you prevent hallucinated tool names in LLM function calling?",
         "SovereignOS enforces strict schema binding. Tools are registered with Pydantic schemas converted to JSON schemas (`tools=[{'type': 'function', 'function': {...}}]`). The system prompt explicitly instructs the LLM to only select from provided function definitions. If the LLM produces an unrecognized function name, Node 6 intercepts the KeyError and feeds a structured error message back to the LLM: 'Error: Tool X does not exist. Available tools: [...]'."),

        ("Q28: How is the chat history restored on hard browser refresh?",
         "On `DOMContentLoaded`, the UI initializes `allChatSessions` from `localStorage`. If an active session ID is found, it calls `GET /api/chat/history?session_id=...`. The backend queries SQLite and returns the chronological message array. The frontend maps each record to user/assistant chat bubbles and activates the WebSocket session with `session_id`, ensuring zero message loss across page reloads."),

        ("Q29: How do you benchmark retrieval accuracy in your Hybrid RAG engine?",
         "I created a synthetic evaluation benchmark of 100 test queries with known ground-truth document IDs. I compared: (1) Pure dense cosine search (Hit@5 = 72%); (2) Pure BM25 sparse search (Hit@5 = 68%); (3) Hybrid RRF Search (Hit@5 = 94.5%). Hybrid search demonstrated massive improvements on alphanumeric tokens, code variables, and dates."),

        ("Q30: What is your philosophy on building Autonomous AI Operating Systems?",
         "An AI OS must not be a passive chat interface; it must be an proactive, reliable executive partner. The primary engineering pillars are: (1) **Absolute Privacy:** Sensitive personal data must stay on local silicon; (2) **Robust Determinism:** State machines and safety gates must guarantee predictable execution over stochastic LLMs; (3) **Frictionless Real-time UX:** Streaming tokens, audio visualizers, and responsive multi-view panes create an interface that feels alive.")
    ]

    for q, a in sovereign_30_qa:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # ──────────────────────────────────────────────────────────────────────────
    # CHAPTER 4: COMPLETE PORTFOLIO & GITHUB PROJECTS BREAKDOWN (6-8 pages)
    # ──────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 3: Portfolio & GitHub Repositories Deep Dive", "Exhaustive engineering analysis of MacroLens Vision AI, Pal-AI, DocDispatch, JobHunter, and VideoTube", styles))
    add_md("## Chapter 3: Portfolio & GitHub Repositories Deep Dive\n\n")

    story.append(Paragraph("3.1 MacroLens Vision AI — Nutrition & Fitness Platform", styles['h2']))
    story.append(Paragraph(
        "<b>Architecture & System Overview:</b><br/>"
        "MacroLens is an AI-powered fitness and nutrition ecosystem built with the MERN stack (MongoDB, Express.js, React, Node.js), OpenRouter Vision API, JWT authentication, and Tailwind CSS. "
        "It solves the core limitation of modern nutrition apps: static generic portion conversion.<br/><br/>"
        "<b>Core Engineering Innovations:</b><br/>"
        "1. <b>Serving-Aware Calculation Engine:</b> 1,014-food Indian nutrition database where every entry defines structured serving metadata (unit type, exact gram weight, default portion). "
        "Calories and macronutrients scale dynamically based on precise gram weights.<br/>"
        "2. <b>Multimodal Meal Logging Pipeline:</b> Users upload meal photos. The frontend compresses images client-side before upload; the Node.js backend validates MIME types (<5MB), "
        "passes base64 image data to the vision model with a strict JSON schema prompt, strips markdown fences, and enforces runtime numeric boundary validation.<br/>"
        "3. <b>MongoDB Aggregation Pipelines:</b> Created compound indexes on `{ userId: 1, date: -1 }` to power aggregation pipelines (`$match -> $unwind -> $group -> $sort`) "
        "that calculate 30-day caloric, protein, carbohydrate, and fat rolling averages in sub-12ms query times.<br/>"
        "4. <b>Text Index Search with Fallback:</b> Text indexes on food names with regex substring fallback to handle typos and regional Indian food names.",
        styles['body']
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("3.2 Pal-AI — Provider-Agnostic Multi-Turn Companion", styles['h2']))
    story.append(Paragraph(
        "<b>Architecture & System Overview:</b><br/>"
        "Pal-AI is a multi-turn AI companion built on Next.js (App Router), OpenRouter Gateway, Node.js, MongoDB, and Tailwind CSS.<br/><br/>"
        "<b>Core Engineering Innovations:</b><br/>"
        "1. <b>Provider-Agnostic Adapter Pattern:</b> Unified abstraction layer allowing seamless swapping between Claude 3.5 Sonnet, GPT-4o, and DeepSeek via environment configuration.<br/>"
        "2. <b>Token-Budgeted Sliding Window Memory:</b> Monitors active token usage per session. When conversation exceeds 70% of context window capacity, an asynchronous background job summarizes older turns and updates system prompt memory while retaining the latest 5 turns verbatim.<br/>"
        "3. <b>Server-Sent Events (SSE) Streaming:</b> Streams LLM tokens smoothly using Next.js Edge Runtime handlers with minimal latency.",
        styles['body']
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("3.3 DocDispatch, JobHunter & VideoTube-Backend", styles['h2']))
    story.append(Paragraph(
        "• <b>DocDispatch (React, Redux Toolkit, Tailwind CSS):</b> Role-based healthcare scheduling platform (Doctors & Patients) featuring strict WAI-ARIA 2.1 AA accessibility compliance, modal keyboard focus trapping, and reusable design system tokens.<br/>"
        "• <b>JobHunter (Python Automation Pipeline):</b> Multi-threaded job scraping, ATS keyword analysis, and automated application workflow engine using Selenium, BeautifulSoup, and vector matching.<br/>"
        "• <b>VideoTube-Backend (Node.js, Express, MongoDB, Cloudinary):</b> Video hosting backend featuring JWT authentication, video transcoding upload pipelines, subscription aggregation pipelines, and like/comment nested document schemas.",
        styles['body']
    ))
    story.append(Spacer(1, 8))

    # ──────────────────────────────────────────────────────────────────────────
    # CHAPTER 5: OPERATING SYSTEMS & LOW-LEVEL CONCURRENCY (6-8 pages)
    # ──────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 4: Operating Systems & Low-Level Concurrency Masterclass", "Processes, Threads, Linux Kernel Internals, Virtual Memory, Memory Models, and Synchronization", styles))
    add_md("## Chapter 4: Operating Systems & Low-Level Concurrency Masterclass\n\n")

    os_master_qa = [
        ("Q1: Exhaustive Breakdown of Process Memory Layout in Virtual Address Space.",
         "When an OS executes a program (ELF on Linux, PE on Windows), it maps it into a <b>Virtual Address Space</b> (typically 48-bit address space on x86-64, giving 256TB user-space memory).<br/>"
         "• <b>Text / Code Segment:</b> Contains compiled machine instructions. Marked read-only and shareable across multiple instances of the same binary.<br/>"
         "• <b>Data Segment (Initialized):</b> Stores global, static, and constant variables initialized by the programmer (e.g. `int count = 10;`).<br/>"
         "• <b>BSS Segment (Block Started by Symbol):</b> Stores uninitialized global and static variables (e.g. `int buffer[1024];`). Initialized to zero by kernel during `execve`.<br/>"
         "• <b>Heap:</b> Dynamically allocated memory managed via `malloc`/`free` or `new`/`delete`. Grows upward from lower to higher memory addresses via `brk`/`sbrk` and `mmap` syscalls.<br/>"
         "• <b>Memory Mapping Segment:</b> Maps shared libraries (`libc.so`), DLLs, and memory-mapped files into the process space.<br/>"
         "• <b>Stack:</b> Stores function call stack frames (local variables, function arguments, return instruction pointers). Grows downward from high to low memory. Managed by Stack Pointer (`RSP`) and Base Pointer (`RBP`) registers."),

        ("Q2: Deep Dive: Process Control Block (PCB) vs Thread Control Block (TCB) & Context Switching.",
         "• <b>Process Control Block (PCB):</b> Kernel data structure containing Process ID (PID), Process State (Running, Ready, Blocked), CPU Registers (RAX, RBX, RCX, RIP), Memory Management Info (CR3 page table base register pointer), Open File Descriptor Table, Signal Handlers, and CPU Scheduling Priority.<br/>"
         "• <b>Thread Control Block (TCB):</b> Contains Thread ID (TID), Thread State, CPU Register Set (private RIP, RSP), Scheduling Priority, and Pointer to the parent process PCB.<br/>"
         "• <b>Context Switching Mechanics:</b> When an interrupt or syscall occurs: (1) CPU switches to Kernel Mode; (2) Saves current thread registers onto kernel stack; (3) Scheduler selects next thread; (4) If switching between different processes, CPU reloads the CR3 register with the new process's page table root, which flushes non-global TLB entries; (5) Restores register state and executes `iret` to return to User Mode."),

        ("Q3: Virtual Memory Architecture: Multi-Level Paging, Page Tables, MMU, TLB, and Inverted Page Tables.",
         "Virtual memory provides process memory isolation and allows processes to allocate more memory than physically available.<br/>"
         "• <b>Multi-Level Paging (x86-64 4-Level Paging):</b> A 48-bit virtual address is split into: PML4 (9 bits) $\\rightarrow$ Page Directory Pointer (9 bits) $\\rightarrow$ Page Directory (9 bits) $\\rightarrow$ Page Table (9 bits) $\\rightarrow$ Physical Offset (12 bits, indexing the 4096-byte page). This multi-level hierarchy prevents allocating empty page tables for sparse address spaces.<br/>"
         "• <b>TLB (Translation Lookaside Buffer):</b> Fully-associative hardware cache on CPU. On address translation: (1) MMU checks TLB; (2) If hit (~1 cycle), physical address is immediately available; (3) If miss, MMU traverses the 4-level page table in RAM (~10-50ns), stores translation in TLB, and proceeds.<br/>"
         "• <b>Page Fault Lifecycle:</b> (1) MMU accesses page with Present Bit = 0; (2) Generates Page Fault interrupt (Trap 14); (3) Kernel page fault handler checks if address is valid; (4) Allocates physical RAM frame; (5) Issues non-blocking disk I/O to read page from swap/file; (6) Updates Page Table Present Bit = 1; (7) Restarts faulting instruction."),

        ("Q4: Inter-Process Communication (IPC) Mechanisms & Performance Comparisons.",
         "• <b>Anonymous Pipes:</b> Half-duplex unidirectional byte stream between parent-child processes (`pipe()` syscall). Kernel buffer (typically 64KB). Fast, but limited to related processes.<br/>"
         "• <b>Named Pipes (FIFOs):</b> Full filesystem presence (`mkfifo`). Unrelated processes can communicate across user space.<br/>"
         "• <b>Unix Domain Sockets (UDS):</b> Bidirectional socket communication within the same OS kernel (`AF_UNIX`). Avoids TCP/IP checksum and network stack overhead. Fastest socket IPC.<br/>"
         "• <b>Shared Memory (`shmget`, `mmap`):</b> Maps the same physical RAM frame into virtual address spaces of two processes. <b>Fastest IPC mechanism</b> (zero-copy memory transfer), but requires synchronization via semaphores or mutexes.<br/>"
         "• <b>Message Queues (POSIX `mq_open`):</b> Kernel-managed structured message queues with priority support."),

        ("Q5: Concurrency Primitives: Mutex, Counting Semaphore, Binary Semaphore, Spinlock, Read-Write Lock, Futex.",
         "• <b>Mutex:</b> Strict ownership lock; only the thread that locks can unlock. Puts waiting threads to sleep (descheduled by kernel).<br/>"
         "• <b>Counting Semaphore:</b> Non-ownership integer counter. `wait()` (P) decrements counter (blocks if $\\le 0$); `signal()` (V) increments counter. Used to manage resource pools.<br/>"
         "• <b>Spinlock:</b> Busy-waits in a CPU loop (`while (test_and_set(&lock))`). Avoids context switch overhead. Used in kernel drivers for very short critical sections (<1μs) on multi-core CPUs.<br/>"
         "• <b>Read-Write Lock (Shared-Exclusive Lock):</b> Multiple concurrent readers allowed; exclusive single writer allowed. Optimizes read-heavy workloads.<br/>"
         "• <b>Futex (Fast Userspace Mutex):</b> Linux synchronization primitive. Attempts lock acquisition in userspace via atomic assembly instruction (`CMPXCHG`). Only traps to kernel if contention occurs, drastically reducing syscall overhead."),

        ("Q6: Python Memory Management, Reference Counting, and the Generational Cyclic Garbage Collector.",
         "Python memory management is layered:<br/>"
         "1. <b>PyMalloc:</b> Specialized allocator for small objects ($\\le 512$ bytes) using Arenas (256KB), Pools (4KB), and Blocks, avoiding OS `malloc` overhead.<br/>"
         "2. <b>Reference Counting:</b> Every Python object contains `ob_refcnt` in `PyObject` header. When `ob_refcnt == 0`, memory is deallocated immediately.<br/>"
         "3. <b>Cyclic Garbage Collector:</b> Reference counting fails on reference cycles (Object A references B, B references A). Python runs a generational cyclic GC dividing objects into Gen 0 (young), Gen 1 (middle), Gen 2 (old). It detects cycles using double-linked lists and trial reference count decrementing.")
    ]

    for q, a in os_master_qa:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # ──────────────────────────────────────────────────────────────────────────
    # CHAPTER 6: COMPUTER NETWORKS & WEB PROTOCOLS (6-8 pages)
    # ──────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 5: Computer Networks & Distributed Web Transport Masterclass", "OSI 7 Layers, TCP Congestion Control, TLS 1.3 Cryptography, HTTP/2 & HTTP/3 QUIC", styles))
    add_md("## Chapter 5: Computer Networks & Distributed Web Transport Masterclass\n\n")

    net_master_qa = [
        ("Q1: Complete Comparison: OSI 7-Layer Model vs TCP/IP 4-Layer Architecture.",
         "• <b>Layer 7 (Application):</b> HTTP, HTTPS, WebSocket, DNS, SMTP, SSH. User interaction and protocol payload formatting.<br/>"
         "• <b>Layer 6 (Presentation):</b> TLS encryption, gzip/brotli compression, ASCII/UTF-8 character encoding.<br/>"
         "• <b>Layer 5 (Session):</b> RPC session establishment, WebSockets session maintenance, token authorization.<br/>"
         "• <b>Layer 4 (Transport):</b> TCP (reliable, ordered, connection-oriented) and UDP (unreliable, datagram, connectionless). Adds Port numbers, TCP sequence numbers, checksums.<br/>"
         "• <b>Layer 3 (Network):</b> IP (IPv4 / IPv6), ICMP, BGP, OSPF. Logical addressing and router path determination (Packets).<br/>"
         "• <b>Layer 2 (Data Link):</b> Ethernet, Wi-Fi (802.11), MAC addressing, frame error checking with CRC (Frames).<br/>"
         "• <b>Layer 1 (Physical):</b> Voltage levels, fiber optic light pulses, radio frequency waves (Bits)."),

        ("Q2: TCP Congestion Control Algorithms: Slow Start, Congestion Avoidance, Fast Retransmit, and BBR.",
         "TCP regulates network throughput to prevent overwhelming network routers:<br/>"
         "• <b>Slow Start:</b> Begins with Congestion Window $\\text{CWND} = 10 \\text{ MSS}$. Doubles CWND every round-trip time (RTT) exponentially ($1 \\rightarrow 2 \\rightarrow 4 \\rightarrow 8 \\dots$) until reaching Slow Start Threshold (ssthresh).<br/>"
         "• <b>Congestion Avoidance:</b> Increases CWND linearly by $1 \\text{ MSS}$ per RTT (Additive Increase).<br/>"
         "• <b>Fast Retransmit & Fast Recovery (TCP Reno):</b> When client receives 3 duplicate ACKs, it immediately retransmits the missing segment without waiting for RTO (Retransmission Timeout), cuts ssthresh in half, and resumes linear increase (AIMD: Additive Increase Multiplicative Decrease).<br/>"
         "• <b>BBR (Bottleneck Bandwidth and RTT by Google):</b> Model-based congestion control. Measures estimated bottleneck bandwidth and min-RTT directly, maximizing throughput while keeping buffer queues empty, avoiding bufferbloat."),

        ("Q3: HTTP/1.1 vs HTTP/2 vs HTTP/3 (QUIC) In-Depth Comparison.",
         "• <b>HTTP/1.1 (1997):</b> Plaintext ASCII protocol. Persistent TCP connections (`Keep-Alive`), but suffers from <b>Head-of-Line (HoL) Blocking</b> at the application layer: only one request/response can be processed per TCP connection at a time. Browsers open 6 parallel TCP connections per domain to mitigate this.<br/>"
         "• <b>HTTP/2 (2015):</b> Binary framing protocol over single TCP connection. <b>Multiplexing:</b> multiple bidirectional streams interleaved over one connection. Header compression using <b>HPACK</b>. Server Push support. <i>Limitation:</i> TCP-level packet loss causes TCP Head-of-Line blocking for all streams.<br/>"
         "• <b>HTTP/3 (2022, QUIC):</b> Operates over <b>UDP</b>. Integrates TLS 1.3 directly into the transport layer. True independent streams: packet loss on stream A does not stall stream B. <b>0-RTT Connection Establishment</b>. Connection migration: switching from Wi-Fi to cellular does not drop active connections because connections use 64-bit Connection IDs rather than IP/port tuples."),

        ("Q4: The Complete HTTPS / TLS 1.3 Handshake and Asymmetric Cryptography.",
         "TLS 1.3 reduces handshake latency to 1-RTT:<br/>"
         "1. <b>ClientHello:</b> Client sends supported cipher suites (e.g. `TLS_AES_256_GCM_SHA384`), client random string, and Diffie-Hellman Key Share ($g^a \\pmod p$).<br/>"
         "2. <b>ServerHello:</b> Server chooses cipher suite, sends server random string, server Diffie-Hellman Key Share ($g^b \\pmod p$), and encrypted certificate chain.<br/>"
         "3. <b>Shared Secret Derivation:</b> Both compute pre-master secret $g^{ab} \\pmod p$ using **ECDHE (Elliptic Curve Diffie-Hellman Ephemeral)**. Both derive symmetric session keys (`AES-256-GCM`).<br/>"
         "4. <b>Certificate Validation:</b> Client verifies server certificate against local trusted Root Certificate Authorities (CA) using public key signatures.<br/>"
         "5. <b>Encrypted Communication:</b> All subsequent HTTP requests/responses are encrypted using symmetric session keys with authenticated encryption (AEAD)."),

        ("Q5: DNS Resolution: Step-by-Step Traversal from Browser to Authoritative Nameserver.",
         "When navigating to `https://api.example.com`:<br/>"
         "1. <b>Browser Cache:</b> Checks internal browser DNS cache (chrome://net-internals/#dns).<br/>"
         "2. <b>OS Cache:</b> Checks OS DNS resolver cache (`/etc/hosts` or Windows DNS Cache).<br/>"
         "3. <b>Recursive Resolver:</b> OS queries ISP or public recursive DNS resolver (e.g. `8.8.8.8` or `1.1.1.1`).<br/>"
         "4. <b>Root Nameserver:</b> Resolver queries root DNS server (`.` root, 13 root server IP clusters). Root returns IP of the `.com` TLD (Top-Level Domain) nameserver.<br/>"
         "5. <b>TLD Nameserver:</b> Resolver queries `.com` TLD server. TLD returns authoritative nameserver for `example.com` (e.g. Cloudflare or AWS Route53).<br/>"
         "6. <b>Authoritative Nameserver:</b> Resolver queries `example.com` authoritative nameserver. Nameserver returns the `A` (IPv4) or `AAAA` (IPv6) address record.<br/>"
         "7. <b>Caching & TTL:</b> Resolver caches record for the specified TTL (Time-To-Live) and returns IP to the browser to initiate the TCP 3-way handshake.")
    ]

    for q, a in net_master_qa:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # ──────────────────────────────────────────────────────────────────────────
    # CHAPTER 7: DATABASE MANAGEMENT SYSTEMS (6-8 pages)
    # ──────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 6: Database Management Systems & Indexing Masterclass", "B+ Trees vs HNSW Vectors, ACID Transactions, MVCC, Isolation Levels & Sharding", styles))
    add_md("## Chapter 6: Database Management Systems & Indexing Masterclass\n\n")

    db_master_qa = [
        ("Q1: B+ Tree Indexing Deep Dive — Inner Nodes, Leaf Nodes, Fan-Out, and Range Scans.",
         "A <b>B+ Tree</b> is a self-balancing $N$-ary search tree optimized for block-storage systems (PostgreSQL, MySQL InnoDB, SQLite).<br/>"
         "• <b>Structural Properties:</b> Non-leaf nodes store only search keys and child page pointers (high fan-out, typically 100–500 keys per 16KB page, keeping tree height $\\le 3-4$ for millions of records). All actual data rows/pointers reside exclusively in Leaf Nodes.<br/>"
         "• <b>Doubly-Linked Leaf Nodes:</b> All leaf nodes are linked horizontally by a doubly-linked list. For range queries (`SELECT * WHERE age BETWEEN 20 AND 30`), the engine traverses $O(\\log N)$ to find the starting leaf node, then performs sequential memory reads along the leaf chain with optimal disk prefetching.<br/>"
         "• <b>Why B+ Trees beat B-Trees:</b> B-Trees store data pointers in internal nodes, lowering fan-out and increasing tree height; B+ trees maximize fan-out and provide vastly superior range scan performance."),

        ("Q2: Vector Indexing: HNSW (Hierarchical Navigable Small World) Graph Architecture.",
         "Used in modern vector databases (Qdrant, Milvus, pgvector) for Approximate Nearest Neighbor (ANN) search over embeddings (e.g. 384/1536 dims).<br/>"
         "• <b>Multi-Layer Graph Hierarchy:</b> Inspired by Skip Lists. Layer 0 (bottom) contains all vector nodes with dense local neighbor connections. Upper layers contain exponentially fewer vectors with long-range 'highway' connections.<br/>"
         "• <b>Greedy Search Routing:</b> Search begins at the top layer. Evaluates distance (Cosine or Euclidean) to neighbors, hops to the closest neighbor, and drops down to the next layer until reaching Layer 0. Achieves $O(\\log N)$ search complexity.<br/>"
         "• <b>Trade-offs:</b> Very fast queries (<5ms) and high recall (>98%), but requires significant RAM to store graph edge lists."),

        ("Q3: Multi-Version Concurrency Control (MVCC) and How PostgreSQL / MySQL Avoid Read Locks.",
         "Traditional 2PL (Two-Phase Locking) blocks readers when a writer is active. MVCC allows <b>'Readers never block writers, and writers never block readers'</b>.<br/>"
         "• <b>Mechanics:</b> When a transaction updates a row, it does not overwrite the existing disk record. Instead, it creates a new version of the row with metadata columns: `xmin` (creating transaction ID) and `xmax` (deleting/updating transaction ID).<br/>"
         "• <b>Read Visibility Snapshot:</b> When Transaction $T$ starts with ID 105, it takes a snapshot of active transaction IDs. It only reads row versions where `xmin < 105` (committed before $T$ began) and `xmax` is either unset or $>105$.<br/>"
         "• <b>VACUUM:</b> PostgreSQL background workers clean up obsolete row versions (dead tuples) that are no longer visible to any active transaction."),

        ("Q4: Database Isolation Levels and the 5 Concurrency Anomalies.",
         "1. <b>Dirty Read:</b> Transaction A reads data modified by Transaction B before B commits. If B rolls back, A read phantom non-existent data.<br/>"
         "2. <b>Non-Repeatable Read:</b> Transaction A reads a row. Transaction B modifies that row and commits. Transaction A re-reads the row and sees different values.<br/>"
         "3. <b>Phantom Read:</b> Transaction A queries rows matching a range condition. Transaction B inserts new rows matching the condition and commits. Transaction A re-runs the range query and sees new phantom rows.<br/>"
         "4. <b>Write Skew:</b> Two concurrent transactions read overlapping datasets, satisfy a constraint locally, and make disjoint updates that together violate a global business invariant (e.g. two on-call doctors simultaneously checking out).<br/>"
         "5. <b>Serialization Anomaly:</b> The final result of concurrent transactions cannot be reproduced by any sequential execution order.<br/>"
         "• <b>Isolation Levels Matrix:</b><br/>"
         "  - <i>Read Uncommitted:</i> Vulnerable to all anomalies.<br/>"
         "  - <i>Read Committed (Default Postgres):</i> Prevents Dirty Reads.<br/>"
         "  - <i>Repeatable Read:</i> Prevents Dirty Reads and Non-Repeatable Reads (and Phantom Reads in Postgres MVCC).<br/>"
         "  - <i>Serializable:</i> Prevents all anomalies via 2PL or SSI (Serializable Snapshot Isolation).")
    ]

    for q, a in db_master_qa:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # ──────────────────────────────────────────────────────────────────────────
    # CHAPTER 8: SYSTEM DESIGN & DISTRIBUTED ARCHITECTURE (6-8 pages)
    # ──────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 7: System Design & Enterprise Architecture Masterclass", "CAP Theorem, Caching, Rate Limiting, Consistent Hashing, Saga & Microservice Patterns", styles))
    add_md("## Chapter 7: System Design & Enterprise Architecture Masterclass\n\n")

    sys_master_qa = [
        ("Q1: Consistent Hashing with Virtual Nodes — Architecture and Mathematical Proof.",
         "• <b>Problem:</b> In standard mod hashing ($\\text{Server} = \\text{Hash}(K) \\pmod N$), adding or removing a server changes $N$, causing nearly 100% of keys to remap, resulting in massive cache misses and database thundering herds.<br/>"
         "• <b>Consistent Hashing Mechanism:</b> Maps both server IDs and data keys onto a circular hash ring ($0 \\text{ to } 2^{32}-1$). A key is assigned to the first server whose position is $\\ge \\text{key position}$ moving clockwise. When a server is added or removed, only $K/N$ keys need remapping on average.<br/>"
         "• <b>Virtual Nodes:</b> To prevent non-uniform data distribution (hot spots), each physical server is mapped to $V$ virtual nodes (e.g. $V=256$) distributed randomly across the ring. This balances load evenly and ensures proportional hand-off when nodes fail."),

        ("Q2: Rate Limiting Algorithms: Token Bucket, Leaky Bucket, Sliding Window Log, and Sliding Window Counter.",
         "• <b>Token Bucket:</b> Tokens added at rate $r$ up to capacity $b$. Request consumes 1 token. Allows bursts up to capacity $b$. Memory efficient ($O(1)$ space). Standard for API gateways (AWS, Stripe).<br/>"
         "• <b>Leaky Bucket:</b> Requests enter FIFO queue, leak out at constant rate. Smooths bursts into uniform flow. Drops requests on queue overflow. Used in traffic shaping.<br/>"
         "• <b>Sliding Window Log:</b> Stores timestamped log of requests in Redis Sorted Set (`ZSET`). Prunes logs older than $(now - window)$ using `ZREMRANGEBYSCORE`, counts remaining with `ZCARD`. Accurate, but high memory overhead ($O(N)$).<br/>"
         "• <b>Sliding Window Counter:</b> Combines previous window count and current window count weighted by elapsed time: $\\text{Count} = \\text{prev} \\times (1 - t) + \\text{curr}$. Eliminates boundary burst spikes with $O(1)$ memory."),

        ("Q3: Distributed Transactions: Two-Phase Commit (2PC) vs Saga Pattern (Orchestration vs Choreography).",
         "• <b>Two-Phase Commit (2PC):</b> Coordinator sends `Prepare` to all nodes. If all vote `Yes`, coordinator sends `Commit`. Strong consistency, but blocking: coordinator failure leaves nodes locked permanently.<br/>"
         "• <b>Saga Pattern (Eventual Consistency):</b> Sequence of local transactions where each step updates its local DB and publishes an event. If a step fails, the Saga executes <b>Compensating Transactions</b> in reverse order.<br/>"
         "  - <i>Choreography:</i> Services publish and subscribe to domain events directly. Decentralized, but difficult to track flow.<br/>"
         "  - <i>Orchestration:</i> Centralized Saga Orchestrator tells participants which local transaction to execute. Easier to monitor and debug.")
    ]

    for q, a in sys_master_qa:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # ──────────────────────────────────────────────────────────────────────────
    # CHAPTER 9: MODERN AI & LLM SYSTEMS ENGINEERING (6-8 pages)
    # ──────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 8: Modern AI & LLM Systems Engineering Masterclass", "Transformer Attention Mathematics, KV Caching, Quantization, RAGAS & Agent Protocols", styles))
    add_md("## Chapter 8: Modern AI & LLM Systems Engineering Masterclass\n\n")

    ai_master_qa = [
        ("Q1: Complete Mathematical Breakdown of Multi-Head Self-Attention in Transformers.",
         "Given input token matrix $X \\in \\mathbb{R}^{N \\times d_{\\text{model}}}$, we project using learned weights $W_Q, W_K, W_V \\in \\mathbb{R}^{d_{\\text{model}} \\times d_k}$:<br/>"
         "$$Q = X W_Q, \\quad K = X W_K, \\quad V = X W_V$$"
         "<b>Attention Formula:</b>"
         "$$\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{Q K^T}{\\sqrt{d_k}}\\right) V$$"
         "• $Q K^T \\in \\mathbb{R}^{N \\times N}$ computes dot-product similarity between every token query and key.<br/>"
         "• $\\frac{1}{\\sqrt{d_k}}$ scaling factor: As dimension $d_k$ grows large, dot products scale with magnitude $d_k$, pushing softmax into extreme regions where gradients are near-zero (vanishing gradients). Dividing by $\\sqrt{d_k}$ preserves unit variance.<br/>"
         "• $\\text{softmax}(\\dots)$ applies $\\frac{e^{z_{ij}}}{\\sum_j e^{z_{ij}}}$ across rows, yielding probability distribution over sequence positions.<br/>"
         "• Multiplying by $V$ computes the final contextual token representations.<br/>"
         "• <b>Multi-Head Attention:</b> Runs $h$ distinct attention heads in parallel and concatenates outputs: $\\text{MHA}(Q, K, V) = \\text{Concat}(\\text{head}_1, \\dots, \\text{head}_h) W_O$."),

        ("Q2: The KV Cache in LLM Inference: Memory Bandwidth Bottlenecks and PagedAttention.",
         "• <b>The Problem:</b> In autoregressive decoding, generating token $t+1$ requires attending to all prior tokens $1 \\dots t$. Recomputing $K$ and $V$ for all past tokens at every step requires $O(N^2)$ compute.<br/>"
         "• <b>KV Cache Solution:</b> Caches Key and Value tensors for past tokens in GPU VRAM. For token $t+1$, only compute new $Q_{t+1}, K_{t+1}, V_{t+1}$, append $K, V$ to cache, and compute attention.<br/>"
         "• <b>Memory Bandwidth Bound:</b> Generating a single token requires transferring the entire multi-gigabyte KV cache from High Bandwidth Memory (HBM) to SRAM while executing only a few arithmetic operations per byte ($O(1)$ arithmetic intensity). This makes LLM generation memory-bandwidth bound rather than compute bound.<br/>"
         "• <b>PagedAttention (vLLM):</b> Standard KV caches allocate contiguous VRAM blocks per request, causing 60-80% memory waste due to internal/external fragmentation. PagedAttention divides the KV cache into fixed-size virtual memory blocks (pages) mapped non-contiguously, enabling near-zero memory waste and $4\\times$ higher serving throughput.")
    ]

    for q, a in ai_master_qa:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # ──────────────────────────────────────────────────────────────────────────
    # CHAPTER 10 & 11: DATA STRUCTURES, ALGORITHMS & LATENCY CHEATSHEET (4-6 pages)
    # ──────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 9: Data Structures, Complexity Matrix & System Design Formulas", "Big-O Analysis, Classic Algorithmic Patterns, Latency Numbers & Estimation Rules", styles))
    add_md("## Chapter 9: Data Structures, Complexity Matrix & System Design Formulas\n\n")

    story.append(Paragraph("9.1 Classic Data Structures Complexity Matrix", styles['h2']))
    ds_matrix = [
        ["Data Structure", "Access (Avg)", "Search (Avg)", "Insert (Avg)", "Delete (Avg)", "Space"],
        ["Array / Dynamic Array", "O(1)", "O(N)", "O(N)", "O(N)", "O(N)"],
        ["Singly Linked List", "O(N)", "O(N)", "O(1)", "O(1)", "O(N)"],
        ["Hash Table (Chaining)", "N/A", "O(1)", "O(1)", "O(1)", "O(N)"],
        ["Binary Search Tree (Balanced)", "O(log N)", "O(log N)", "O(log N)", "O(log N)", "O(N)"],
        ["B+ Tree Index", "O(log N)", "O(log N)", "O(log N)", "O(log N)", "O(N)"],
        ["Trie (Prefix Tree)", "O(L)", "O(L)", "O(L)", "O(L)", "O(N * L)"],
        ["Min / Max Heap (Priority Q)", "O(1) peek", "O(N)", "O(log N)", "O(log N)", "O(N)"]
    ]
    t_ds = make_table(ds_matrix[0], ds_matrix[1:], [140, 75, 75, 75, 75, 75], styles)
    story.append(t_ds)
    story.append(Spacer(1, 8))

    story.append(Paragraph("9.2 System Design Quantitative Estimation Formulas", styles['h2']))
    sd_math = (
        "• <b>QPS (Queries Per Second):</b> $\\text{QPS} = \\frac{\\text{Daily Active Users (DAU)} \\times \\text{Requests per User}}{86,400 \\text{ seconds}}$.<br/>"
        "• <b>Peak QPS:</b> $\\text{Peak QPS} = \\text{Average QPS} \\times 2 \\text{ to } 3$.<br/>"
        "• <b>Storage Estimation:</b> $\\text{Annual Storage} = \\text{Daily Requests} \\times \\text{Payload Size} \\times 365 \\text{ days} \\times \\text{Replication Factor (3)}$.<br/>"
        "• <b>Network Bandwidth:</b> $\\text{Incoming Bandwidth} = \\text{QPS} \\times \\text{Payload Size (Bytes)} \\times 8 \\text{ bits}$."
    )
    story.append(Paragraph(sd_math, styles['body']))
    story.append(Spacer(1, 8))

    story.append(Paragraph("9.3 Latency Numbers Every Programmer Must Know", styles['h2']))
    cheat_data = [
        [Paragraph("<b>Operation / Resource</b>", styles['body_bold']), Paragraph("<b>Approximate Latency</b>", styles['body_bold']), Paragraph("<b>Scale Comparison & Takeaway</b>", styles['body_bold'])],
        [Paragraph("L1 CPU Cache Reference", styles['body']), Paragraph("~ 1 ns", styles['body']), Paragraph("Fastest hardware memory lookup.", styles['body'])],
        [Paragraph("Main Memory (RAM) Access", styles['body']), Paragraph("~ 100 ns", styles['body']), Paragraph("100x slower than L1 cache.", styles['body'])],
        [Paragraph("NVMe SSD Random Read", styles['body']), Paragraph("~ 10–50 μs", styles['body']), Paragraph("100x to 500x slower than RAM.", styles['body'])],
        [Paragraph("Network Roundtrip (Same Datacenter)", styles['body']), Paragraph("~ 0.5 ms", styles['body']), Paragraph("10x slower than SSD.", styles['body'])],
        [Paragraph("Cross-Continental Network (NYC - London)", styles['body']), Paragraph("~ 70–100 ms", styles['body']), Paragraph("Speed of light in fiber constraint.", styles['body'])]
    ]
    t_cheat = Table(cheat_data, colWidths=[160, 120, 260])
    t_cheat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [COLOR_BG_LIGHT, COLOR_CARD_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_cheat)

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Master Encyclopedia PDF successfully compiled at: {pdf_path}")

    with open(md_path, "w", encoding="utf-8") as f:
        f.writelines(md_lines)
    print(f"Master Encyclopedia Markdown successfully compiled at: {md_path}")

if __name__ == "__main__":
    build_encyclopedia()
