"""
Massive 40-50+ Page Technical Engineering Textbook & Interview Guide for Yashpreet.
Generates:
1. Yashpreet_Master_Interview_Preparation_Guide.pdf
2. INTERVIEW_PREPARATION_MASTER_GUIDE.md
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib import colors
from pdf_setup import get_styles, NumberedCanvas, COLOR_PRIMARY, COLOR_SECONDARY, COLOR_ACCENT, COLOR_BRAND, COLOR_PURPLE, COLOR_CARD_BG, COLOR_BG_LIGHT, COLOR_BORDER
from large_doc_helpers import create_section_header, make_qa, make_table

def build_massive_pdf_and_md():
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
    # COVER / HEADER
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Yashpreet — Technical Interview Master Engineering Compendium", styles['title']))
    story.append(Paragraph("The Definitive 360° Technical Textbook & Interview Guide • SDE / Full-Stack / AI Systems", styles['subtitle']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_ACCENT, spaceBefore=2, spaceAfter=8))

    meta_table_data = [
        [
            Paragraph("<b>Candidate:</b> Yashpreet", styles['body']),
            Paragraph("<b>Education:</b> B.Tech in CSE (VIT Bhopal, CGPA: 8.47/10)", styles['body']),
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

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 1: CANDIDATE POSITIONING & BEHAVIORAL STAR PLAYBOOK
    # ══════════════════════════════════════════════════════════════════════════
    story.extend(create_section_header("Chapter 1: Candidate Positioning, Narrative & Behavioral STAR Playbook", "Strategic communication frameworks for leadership and technical rounds", styles))
    add_md("## Chapter 1: Candidate Positioning, Narrative & Behavioral STAR Playbook\n")

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
    add_md("### 1.1 The 90-Second High-Impact Self-Introduction\n\n> " + pitch_text.replace("<i>", "").replace("</i>", "") + "\n\n")

    story.append(Paragraph("1.2 The Complete 10-Scenario Behavioral STAR Playbook", styles['h2']))
    add_md("### 1.2 The Complete 10-Scenario Behavioral STAR Playbook\n\n")

    star_scenarios = [
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
         "Delivered an optimal balance of strict data privacy, offline autonomy, and frontier intelligence when available.")
    ]

    for title, s_t, a, r in star_scenarios:
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

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 2: SOVEREIGN OS — COMPLETE TECHNICAL REFERENCE MANUAL
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 2: SovereignOS — Flagship Engineering Reference Manual", "Exhaustive file-by-file codebase walkthrough, state graph DAG, and 20 deep interview Q&As", styles))
    add_md("## Chapter 2: SovereignOS — Flagship Engineering Reference Manual\n\n")

    story.append(Paragraph("2.1 Architectural Philosophy: The Local-First Command Center", styles['h2']))
    arch_phil = (
        "Modern cloud-centric AI assistants suffer from three fatal flaws: (1) **Privacy Violations** — sending confidential emails, financial notes, and local files to remote LLM APIs; "
        "(2) **No Desktop Execution Autonomy** — inability to interact with native local filesystems, offline calendars, and private notes; "
        "(3) **Synchronous Fragility** — brittle linear chains that crash on API timeouts without state persistence. "
        "<b>SovereignOS</b> was engineered as a local-first autonomous command center. It combines a 5-tier cyclical LangGraph state machine, "
        "a zero-shot quarantine security gate, hybrid vector RAG (Qdrant + BM25), and sandboxed Model Context Protocol (MCP) execution."
    )
    story.append(Paragraph(arch_phil, styles['body']))
    story.append(Spacer(1, 6))
    add_md(f"### 2.1 Architectural Philosophy: The Local-First Command Center\n\n{arch_phil}\n\n")

    story.append(Paragraph("2.2 File-by-File Codebase Deep Dive", styles['h2']))
    add_md("### 2.2 File-by-File Codebase Deep Dive\n\n")

    codebase_details = [
        ("1. server/app.py (FastAPI Gateway & WebSocket Streaming)",
         "<b>Core Responsibilities:</b> Serves the single-page reactive dashboard, manages REST APIs for calendar/inbox/approvals, persists chat history in SQLite, and handles WebSocket streaming sessions.<br/>"
         "<b>Key Implementation Details:</b><br/>"
         "• <code>@asynccontextmanager async def lifespan(app)</code>: Manages background watcher daemons (Folder Watcher, Scheduler) on startup and cleanly drains task queues on shutdown.<br/>"
         "• <code>@app.websocket('/ws/chat')</code>: Connects the browser client to LangGraph's <code>astream_events(version='v1')</code>. Emits structured JSON events: <code>node_progress</code> (updating UI pulsing pills), <code>tool_start</code>, <code>token</code> (~55 chunks/sec), and <code>done</code>.<br/>"
         "• <code>/api/calendar/event (GET, POST, PUT, DELETE)</code>: CRUD endpoints for offline/online calendar events with tombstone deletion support.<br/>"
         "• <code>/api/approvals/{id}/decision (POST)</code>: Resolves pending Human-In-The-Loop approval tokens, unpausing suspended LangGraph executions."),

        ("2. execution/orchestration/agent_engine.py (LangGraph State Machine DAG)",
         "<b>Core Responsibilities:</b> Defines the state machine topology, agent state schema, node execution logic, and conditional edges.<br/>"
         "<b>Key Implementation Details:</b><br/>"
         "• <code>class AgentState(TypedDict)</code>: State payload containing <code>messages: Annotated[list, add_messages]</code>, <code>context_docs: list[str]</code>, <code>planned_tool: str</code>, <code>tool_args: dict</code>, <code>approval_required: bool</code>, <code>risk_level: str</code>.<br/>"
         "• <code>build_agent_graph()</code>: Compiles the 5-tier state graph: <code>quarantine -> triaging -> [fast_reply | (retrieval -> reasoning -> hitl_gate -> tool_execution -> reasoning)]</code>.<br/>"
         "• Uses <code>MemorySaver</code> checkpointer for session persistence, allowing state recovery across crashes."),

        ("3. execution/security/quarantine.py (Quarantine Security Gate)",
         "<b>Core Responsibilities:</b> Protects against prompt injections, jailbreaks, Canary leakage, and unauthorized desktop privilege escalations.<br/>"
         "<b>Key Implementation Details:</b><br/>"
         "• <b>Regex Heuristics:</b> Fast regex pattern matching for known override strings ('ignore previous instructions', 'system override', 'reveal prompt').<br/>"
         "• <b>Zero-Shot Canary Tokens:</b> Injects high-entropy random GUID canary tokens into system prompt boundaries. If the output attempts to leak the canary, execution is halted immediately.<br/>"
         "• <b>Risk Scoring:</b> Categorizes queries into LOW (chit-chat), MEDIUM (read-only search), and HIGH (destructive file/calendar/email operations)."),

        ("4. execution/rag/hybrid_retriever.py (Hybrid Vector Search Engine)",
         "<b>Core Responsibilities:</b> Provides unified dense + sparse document retrieval across personal notes, documentation, and chat memories.<br/>"
         "<b>Key Implementation Details:</b><br/>"
         "• <b>Dense Vector Search:</b> Embeds documents using <code>sentence-transformers/all-MiniLM-L6-v2</code> (384 dimensions) and stores vectors in local Qdrant collection with HNSW index.<br/>"
         "• <b>Sparse Lexical Search:</b> Inverted index scored using BM25 ($k_1=1.5, b=0.75$).<br/>"
         "• <b>Reciprocal Rank Fusion (RRF):</b> Merges top-k rankings: $RRF(d) = \\sum_{m} \\frac{1}{60 + rank_m(d)}$. Guarantees keyword precision and semantic recall."),

        ("5. execution/tools/calendar_connector.py (Offline-First Calendar Engine)",
         "<b>Core Responsibilities:</b> Synchronizes events with Google Calendar API while maintaining a 100% functional offline JSON cache.<br/>"
         "<b>Key Implementation Details:</b><br/>"
         "• <b>Composite Keys:</b> Index events locally by composite tuple <code>(summary, start_time[:16])</code> to prevent duplication across repeated sync passes.<br/>"
         "• <b>Tombstone Ledger:</b> Offline deletions append records to <code>deleted_calendar_events.json</code>. Sync logic processes tombstones first against remote Google API before upserting active events."),

        ("6. execution/tools/gmail_connector.py (Gmail Triage & Dispatch Engine)",
         "<b>Core Responsibilities:</b> Fetches unread emails, parses RFC 2822 / MIME message structures, classifies priority, and drafts replies.<br/>"
         "<b>Key Implementation Details:</b><br/>"
         "• Decodes base64url-encoded message bodies and extracts plain text from multi-part MIME payloads.<br/>"
         "• LLM triaging classifies emails into URGENT, ACTIONABLE, NEWSLETTER, or SPAM, synthesizing 1-click contextual reply drafts saved directly into Obsidian vault."),

        ("7. execution/tools/obsidian_workspace.py (Obsidian Vault Markdown Engine)",
         "<b>Core Responsibilities:</b> Bi-directional synchronization with local Obsidian markdown notes.<br/>"
         "<b>Key Implementation Details:</b><br/>"
         "• Parses Markdown AST to extract YAML frontmatter metadata (tags, created_date, status).<br/>"
         "• Header-level chunking: Slices markdown by `# H1` and `## H2` headings so each chunk maintains semantic integrity before vector embedding.<br/>"
         "• Appends daily log entries and executive briefings into `Daily Notes/` with ISO timestamps."),

        ("8. execution/tools/mcp_manager.py (Model Context Protocol Host)",
         "<b>Core Responsibilities:</b> Anthropic MCP client implementation over JSON-RPC 2.0 stdio transport.<br/>"
         "<b>Key Implementation Details:</b><br/>"
         "• Launches sandboxed Node.js / Python MCP servers (`@modelcontextprotocol/server-filesystem`, `@modelcontextprotocol/server-sqlite`) as subprocesses.<br/>"
         "• Handshakes via `tools/list` on startup, converting MCP JSON schemas into LangChain tool definitions at runtime.<br/>"
         "• Dispatches calls asynchronously via `tools/call` over stdin/stdout pipes with configurable timeouts."),

        ("9. execution/tools/folder_watcher.py (Automated File Ingestion)",
         "<b>Core Responsibilities:</b> Monitors specified directories using OS filesystem events (`watchdog`) and automatically parses and vectorizes dropped files.<br/>"
         "<b>Key Implementation Details:</b><br/>"
         "• Supports `.pdf` (pypdf/pdfplumber), `.txt`, `.md`, `.json`, and `.py` source files.<br/>"
         "• Chunks text, generates embeddings, and upserts payloads into Qdrant collection with file path and modification timestamp metadata."),

        ("10. server/dashboard_template.py (Reactive Cyber HUD Frontend)",
         "<b>Core Responsibilities:</b> High-performance Single Page Application (SPA) dashboard styled with modern cyber aesthetics.<br/>"
         "<b>Key Implementation Details:</b><br/>"
         "• Native JavaScript DOM rendering with zero bloated framework overhead.<br/>"
         "• WebSocket client with exponential backoff auto-reconnection and conversation session switching.<br/>"
         "• Web Audio API `AnalyserNode` frequency spectrum visualizer (CAVA-style music equalizer).<br/>"
         "• Collapsible tool execution detail cards and 3-way Calendar view switcher (Month, Week, Agenda).")
    ]

    for title, desc in codebase_details:
        story.append(Paragraph(f"<b>{title}</b>", styles['h3']))
        story.append(Paragraph(desc, styles['body']))
        story.append(Spacer(1, 4))
        add_md(f"#### {title}\n{desc.replace('<b>', '**').replace('</b>', '**').replace('<br/>', '\n')}\n\n")

    # ══════════════════════════════════════════════════════════════════════════
    # 20 DEEP INTERVIEW Q&AS ON SOVEREIGN OS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("2.3 Top 20 Technical Interview Q&As on SovereignOS", styles['h2']))
    add_md("### 2.3 Top 20 Technical Interview Q&As on SovereignOS\n\n")

    sovereign_20_qa = [
        ("Q1: Why LangGraph instead of traditional linear LangChain chains or while loops?",
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
         "The current architecture is optimized for single-user desktop privacy. To scale to a multi-tenant enterprise system: (1) Replace SQLite with PostgreSQL / TimescaleDB with connection pooling (PgBouncer); (2) Transition local Qdrant to a distributed Qdrant cluster with sharded collections; (3) Decouple agent graph execution from the web server using Celery/RabbitMQ or Redis Streams worker pools; (4) Introduce role-based access control (RBAC) and OAuth2 OIDC multi-tenancy.")
    ]

    for q, a in sovereign_20_qa:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 3: PORTFOLIO PROJECTS IN-DEPTH ANALYSIS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 3: Portfolio Projects In-Depth Analysis", "Detailed architectural breakdown of MacroLens Vision AI, Pal-AI, DocDispatch, and JobHunter", styles))
    add_md("## Chapter 3: Portfolio Projects In-Depth Analysis\n\n")

    story.append(Paragraph("3.1 MacroLens Vision AI — Nutrition & Fitness Platform", styles['h2']))
    story.append(Paragraph(
        "<b>Stack:</b> MERN (MongoDB, Express.js, React, Node.js), OpenRouter Vision API, JWT, bcrypt, Tailwind CSS.<br/>"
        "<b>Architectural Deep Dive & Key Innovations:</b><br/>"
        "• <b>Serving-Aware Calculation Engine:</b> Most nutrition apps store flat calorie numbers per generic food item (e.g. '1 roti = 100 cal'). MacroLens engineered a 1,014-item Indian food database where each entry defines structured serving metadata (unit type, exact gram weight, default portion). The backend computes exact calories and macronutrients dynamically based on user-entered gram weights or piece counts.<br/>"
        "• <b>Multimodal Meal Logging:</b> Integrated OpenRouter multimodal LLMs. The frontend compresses images client-side before upload; the Node.js backend validates MIME types (<5MB), passes base64 image data to the vision model with a strict JSON schema prompt, strips markdown fences, and enforces runtime numeric boundary validation.<br/>"
        "• <b>MongoDB Aggregation Pipelines:</b> Created compound indexes on <code>{ userId: 1, date: -1 }</code> to power aggregation pipelines (<code>$match -> $unwind -> $group -> $sort</code>) that calculate 30-day caloric, protein, carbohydrate, and fat rolling averages in sub-12ms query times.",
        styles['body']
    ))
    story.append(Spacer(1, 6))

    macrolens_qa = [
        ("Q1: How do you handle schema hallucinations when an LLM Vision API returns food analysis?",
         "LLMs frequently return markdown wrappers (```json) or hallucinate non-standard keys. I implemented a 3-layer validation pipeline: (1) System prompt with strict JSON schema and few-shot examples; (2) Regex pre-processor that strips markdown ticks and fixes trailing commas; (3) Joi/Zod runtime schema validator in Node.js checking numeric constraints (e.g. protein >= 0, calories <= 5000). If validation fails, it triggers an immediate retry with temperature=0.1 or prompts the user for manual confirmation."),

        ("Q2: Walk me through the MongoDB aggregation pipeline for daily nutrition totals.",
         "The pipeline executes in 4 stages: (1) `$match`: Filters meal logs by `userId` and ISO date range `[start_date, end_date]` utilizing the compound index `{ userId: 1, date: -1 }`; (2) `$unwind`: Deconstructs the `foods` array into separate document streams; (3) `$group`: Groups by `date` and computes `$sum` for `calories`, `protein`, `carbs`, and `fats`; (4) `$sort`: Orders chronologically by date. Execution time is under 12ms across thousands of documents.")
    ]
    for q, a in macrolens_qa:
        story.extend(make_qa(q, a, styles))

    story.append(Paragraph("3.2 Pal-AI — Provider-Agnostic Multi-Turn Companion", styles['h2']))
    story.append(Paragraph(
        "<b>Stack:</b> Next.js (App Router), OpenRouter Gateway, Node.js, MongoDB, Tailwind CSS.<br/>"
        "<b>Key Innovations:</b><br/>"
        "• <b>Provider-Agnostic Adapter:</b> Abstracted LLM communication into a unified adapter pattern, allowing instant switching between Claude 3.5 Sonnet, GPT-4o, and DeepSeek without modifying business logic.<br/>"
        "• <b>Sliding Context Window with Summarization:</b> Built a token-budgeted memory manager. When conversation history reaches 70% of model window capacity, an asynchronous worker summarizes older turns, appending the summary into system instructions while retaining recent conversation turns verbatim.",
        styles['body']
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("3.3 DocDispatch & JobHunter", styles['h2']))
    story.append(Paragraph(
        "• <b>DocDispatch (React, Redux Toolkit, Tailwind CSS):</b> Healthcare scheduling portal with dual-portal doctor/patient workflows, audited for strict WCAG 2.1 AA accessibility (focus trapping, ARIA landmarks, keyboard navigation).<br/>"
        "• <b>JobHunter (Python Automation):</b> Automated job scraping and ATS resume matching pipeline utilizing Beautiful Soup, Selenium, and keyword vector scoring.",
        styles['body']
    ))
    story.append(Spacer(1, 8))

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 4: CORE COMPUTER SCIENCE FOUNDATIONS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 4: Core Computer Science Foundations", "Operating Systems, Concurrency, Computer Networks, DBMS & System Design", styles))
    add_md("## Chapter 4: Core Computer Science Foundations\n\n")

    story.append(Paragraph("4.1 Operating Systems & Low-Level Concurrency", styles['h2']))

    cs_os_full = [
        ("Q1: Process vs Thread — Memory Layout, Context Switching, and Kernel Data Structures.",
         "A <b>Process</b> is an independent executing program with its own private virtual memory address space consisting of: (1) <b>Text/Code Segment</b> (read-only machine code); (2) <b>Data Segment</b> (initialized globals/statics); (3) <b>BSS Segment</b> (uninitialized globals/statics); (4) <b>Heap</b> (dynamically allocated memory growing upward); (5) <b>Stack</b> (local variables, call frames, return addresses growing downward). Processes are isolated by hardware MMU page tables; IPC (pipes, shared memory, sockets) is required for communication.<br/>"
         "A <b>Thread</b> is the smallest unit of CPU execution within a process. All threads share the parent process's Text, Data, Heap, and file descriptor table, but possess their own private Thread Control Block (TCB) containing private Stack, Stack Pointer, and Program Counter (PC).<br/>"
         "<b>Context Switching:</b> Thread context switching is substantially faster than process context switching because the CPU does not need to reload virtual memory page directory registers (CR3 on x86), preventing expensive TLB (Translation Lookaside Buffer) invalidation and cache thrashing."),

        ("Q2: Explain the Python Global Interpreter Lock (GIL) — Mechanics, Rationale, and Workarounds.",
         "The GIL is a mutual exclusion lock used by CPython to ensure only one native OS thread executes Python bytecode at a time. It was designed because CPython's memory management relies on reference counting, which is inherently non-thread-safe without fine-grained locking (which would introduce immense single-threaded performance overhead).<br/>"
         "• <b>I/O-Bound Workloads:</b> When a Python thread performs an I/O syscall (network read/write, disk access, `time.sleep`), it releases the GIL. Other threads or `asyncio` coroutines can execute, making `asyncio` and `threading` highly efficient for I/O.<br/>"
         "• <b>CPU-Bound Workloads:</b> For compute-heavy tasks (vector calculations, data transformation), multi-threading suffers from lock contention without speedup. True parallelism requires <b>Multiprocessing</b> (spawning separate OS processes with independent Python runtimes and GILs) or offloading compute to native C/Rust extensions (like NumPy, PyTorch, or Polars)."),

        ("Q3: How Async/Await and the Event Loop work under the hood (Epoll, Kqueue, IOCP).",
         "<code>asyncio</code> implements <b>single-threaded cooperative multitasking</b> using generators and coroutines. When an async function reaches an `await` on an uncompleted future (e.g. network read), it yields execution back to the Event Loop. The Event Loop registers the socket's file descriptor with OS kernel multiplexing primitives: <code>epoll</code> on Linux, <code>kqueue</code> on macOS/BSD, or <code>IOCP</code> on Windows.<br/>"
         "The OS kernel uses hardware interrupts and network driver ring buffers to detect socket readiness. When data arrives, the kernel notifies the event loop, which moves the suspended coroutine from the waiting queue to the ready queue and resumes execution from its saved stack frame."),

        ("Q4: The 4 Coffman Conditions for Deadlock and how to eliminate them.",
         "A deadlock occurs if and only if all four Coffman conditions hold simultaneously:<br/>"
         "1. <b>Mutual Exclusion:</b> Resources cannot be shared simultaneously.<br/>"
         "2. <b>Hold and Wait:</b> A process holds at least one resource while waiting to acquire another.<br/>"
         "3. <b>No Preemption:</b> Resources cannot be forcibly confiscated from a process holding them.<br/>"
         "4. <b>Circular Wait:</b> A closed chain of processes exists where each process waits for a resource held by the next ($P_0 \\rightarrow P_1 \\rightarrow \\dots \\rightarrow P_n \\rightarrow P_0$).<br/>"
         "<b>Elimination:</b> Prevent circular wait by enforcing a strict global resource ordering rule (processes must acquire locks in ascending numerical order of resource ID)."),

        ("Q5: Virtual Memory, Paging, Page Faults, and the Translation Lookaside Buffer (TLB).",
         "Virtual memory maps a process's virtual address space to physical RAM using fixed-size blocks called <b>Pages</b> (typically 4KB). The Memory Management Unit (MMU) translates virtual addresses to physical frames using hierarchical Page Tables.<br/>"
         "The <b>TLB (Translation Lookaside Buffer)</b> is a high-speed hardware cache on the CPU that stores recent virtual-to-physical address translations. If a translation is in TLB (TLB Hit), translation takes ~1 cycle. If not (TLB Miss), the MMU walks the multi-level page table in RAM (~10-50ns).<br/>"
         "A <b>Page Fault</b> occurs when a process accesses a page marked invalid in the page table. The CPU triggers an interrupt (trap to kernel), the OS locates the page in swap/disk, allocates a physical frame, reads the page into RAM, updates the page table, and resumes the instruction.")
    ]

    for q, a in cs_os_full:
        story.extend(make_qa(q, a, styles))

    story.append(Paragraph("4.2 Computer Networks & Distributed Communication", styles['h2']))

    cs_net_full = [
        ("Q6: Explain the TCP 3-Way Handshake, 4-Way Teardown, and TIME_WAIT state.",
         "• <b>3-Way Handshake:</b> (1) Client $\\rightarrow$ Server: `SYN` (seq=x); (2) Server $\\rightarrow$ Client: `SYN-ACK` (seq=y, ack=x+1); (3) Client $\\rightarrow$ Server: `ACK` (ack=y+1). State becomes `ESTABLISHED`. Synchronizes sequence numbers and establishes window sizes.<br/>"
         "• <b>4-Way Teardown:</b> (1) Active closer sends `FIN`; (2) Passive closer sends `ACK` (enters `CLOSE_WAIT`); (3) Passive closer finishes sending pending data and sends `FIN`; (4) Active closer sends `ACK` and enters `TIME_WAIT`.<br/>"
         "• <b>Why TIME_WAIT (2*MSL) is critical:</b> (a) Ensures the final ACK is received by the server (if lost, server retransmits FIN, and client can resend ACK rather than sending RST); (b) Allows lingering duplicate packets in the network to expire so they don't corrupt a future connection reusing the same `(IP, port)` tuple."),

        ("Q7: Compare WebSockets, Server-Sent Events (SSE), and HTTP Long-Polling.",
         "• <b>WebSockets (RFC 6455):</b> Full-duplex bidirectional communication over a single persistent TCP connection initiated via HTTP 101 Switching Protocols. Lowest framing overhead (2-14 bytes per frame). Best for interactive chat, gaming, and bidirectional agent control.<br/>"
         "• <b>Server-Sent Events (SSE):</b> Unidirectional (Server $\\rightarrow$ Client) streaming over standard HTTP (`text/event-stream`). Built-in browser reconnection, event IDs, and HTTP/2 multiplexing. Ideal for LLM token streaming and financial tickers.<br/>"
         "• <b>HTTP Long-Polling:</b> Client opens HTTP request; server hangs open until data is available, then closes. Requires repeated TCP/TLS handshakes and full HTTP header re-transmission. High latency and overhead; legacy fallback."),

        ("Q8: Deep Dive into the TLS 1.3 Handshake and Modern HTTPS Security.",
         "TLS 1.3 reduces handshake latency to 1-RTT (one round-trip time):<br/>"
         "1. <b>ClientHello:</b> Sends supported cipher suites + client random + key share (Diffie-Hellman public key parameters).<br/>"
         "2. <b>ServerHello:</b> Selects cipher suite + sends server random + key share + server certificate + encrypted extensions.<br/>"
         "3. Both parties compute the shared secret using **ECDHE (Elliptic Curve Diffie-Hellman Ephemeral)**, generating symmetric session keys (`AES-256-GCM` or `ChaCha20-Poly1305`). All subsequent HTTP payload is encrypted with zero further handshake overhead.")
    ]

    for q, a in cs_net_full:
        story.extend(make_qa(q, a, styles))

    story.append(Paragraph("4.3 Database Management Systems (DBMS) & Distributed Storage", styles['h2']))

    cs_db_full = [
        ("Q9: Compare B+ Tree Indexing in Relational DBs with Vector HNSW Indexing in Qdrant.",
         "• <b>B+ Tree Index:</b> Self-balancing N-ary tree where all data records/pointers reside strictly in leaf nodes linked by a doubly-linked list. Non-leaf nodes only store search keys. Provides $O(\\log N)$ lookup, insertion, deletion, and optimal sequential cache locality for range queries (`BETWEEN a AND b`).<br/>"
         "• <b>HNSW (Hierarchical Navigable Small World):</b> Multi-layer proximity graph index for high-dimensional vectors (e.g. 384 or 1536 dims). Higher layers contain sparse long-range highway links (like skip-lists); bottom layer contains dense local nearest neighbors. Provides $O(\\log N)$ approximate nearest neighbor (ANN) search via Greedy Routing, scaling efficiently to millions of embeddings."),

        ("Q10: Explain ACID Transactions, Isolation Levels, and Concurrency Anomalies.",
         "• <b>ACID:</b> Atomicity (All-or-nothing via WAL), Consistency (State constraints preserved), Isolation (Concurrent transactions don't cross-contaminate), Durability (Committed data survives crashes).<br/>"
         "• <b>Isolation Levels & Anomalies:</b><br/>"
         "  - <i>Read Uncommitted:</i> Vulnerable to Dirty Reads (reading uncommitted data that later rolls back).<br/>"
         "  - <i>Read Committed:</i> Prevents Dirty Reads, but vulnerable to Non-Repeatable Reads (row values change between reads).<br/>"
         "  - <i>Repeatable Read:</i> Uses MVCC snapshots; prevents Non-Repeatable Reads, but may suffer Phantom Reads (new rows inserted).<br/>"
         "  - <i>Serializable:</i> Highest level; executed via Two-Phase Locking (2PL) or Serializable Snapshot Isolation (SSI). Complete anomaly prevention."),

        ("Q11: Explain the CAP Theorem and PACELC Theorem with concrete real-world systems.",
         "<b>CAP Theorem</b> states that under a network partition (**P**), a distributed system can guarantee either **Consistency (C)** (every read receives most recent write) or **Availability (A)** (every non-failing node returns a non-error response), but not both.<br/>"
         "<b>PACELC</b> extends CAP: If there is a Partition (**P**), trade **A** vs **C**; **Else (E)**, trade Latency (**L**) vs Consistency (**C**). For example, MongoDB default is PC/EC (favors consistency over latency), while Cassandra is PA/EL (favors availability and low latency).")
    ]

    for q, a in cs_db_full:
        story.extend(make_qa(q, a, styles))

    story.append(Paragraph("4.4 System Design & Software Architecture", styles['h2']))

    cs_sys_full = [
        ("Q12: Explain Caching Strategies (Cache-Aside, Write-Through, Write-Back) and Eviction Policies.",
         "• <b>Cache-Aside:</b> Application reads from cache; on miss, reads from DB and writes to cache. On write, updates DB and invalidates cache entry. Most common.<br/>"
         "• <b>Write-Through:</b> Application writes to cache; cache synchronously writes to DB before confirming. Strong consistency, higher write latency.<br/>"
         "• <b>Write-Behind (Write-Back):</b> Application writes to cache; cache asynchronously batches writes to DB. Low write latency, risk of data loss on cache crash.<br/>"
         "• <b>Eviction Policies:</b> LRU (Least Recently Used via Doubly-Linked List + Hash Map), LFU (Least Frequently Used), FIFO, and 2Q (Two-Queue)."),

        ("Q13: Compare Rate Limiting Algorithms (Token Bucket, Leaky Bucket, Sliding Window Counter).",
         "• <b>Token Bucket:</b> Tokens added at rate $r$ up to capacity $b$. Request consumes 1 token. Allows bursts up to capacity $b$. Memory efficient. Used in AWS and Stripe.<br/>"
         "• <b>Leaky Bucket:</b> Requests enter FIFO queue, leak out at constant rate. Smooths bursts into uniform flow. Drops requests on queue overflow.<br/>"
         "• <b>Sliding Window Counter:</b> Combines previous window count and current window count weighted by elapsed time: $\\text{Count} = \\text{prev} \\times (1 - t) + \\text{curr}$. Eliminates boundary burst spikes with low memory.")
    ]

    for q, a in cs_sys_full:
        story.extend(make_qa(q, a, styles))

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 5: MODERN AI & LLM SYSTEMS ENGINEERING
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 5: Modern AI & LLM Systems Engineering", "Transformer Mathematics, KV Caching, Advanced RAG, and Agentic Design Patterns", styles))
    add_md("## Chapter 5: Modern AI & LLM Systems Engineering\n\n")

    ai_full = [
        ("Q1: Explain the Mathematical Mechanics of Scaled Dot-Product Attention in Transformers.",
         "Input embeddings $X$ are projected using weight matrices $W_Q, W_K, W_V$ into Query ($Q$), Key ($K$), and Value ($V$) matrices. The attention formula is: "
         "$$\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{Q K^T}{\\sqrt{d_k}}\\right) V$$"
         "• $Q K^T$ computes similarity dot-products between all token pairs in the sequence (matrix of size $N \\times N$).<br/>"
         "• Dividing by $\\sqrt{d_k}$ (where $d_k$ is the key dimension) prevents dot products from growing excessively large, which would push softmax into regions with near-zero gradients.<br/>"
         "• Softmax normalizes scores into an attention weight distribution summing to 1 across rows.<br/>"
         "• Multiplying by $V$ computes a context-aware weighted sum of value vectors for each token position."),

        ("Q2: What is the KV Cache in LLM Inference and why is generation memory-bandwidth bound?",
         "In autoregressive generation, generating each new token requires attending to all prior tokens in the sequence. Without caching, the model would recompute Keys and Values for all past tokens at every step ($O(N^2)$ redundant compute). The <b>KV Cache</b> stores computed Key and Value tensors in GPU VRAM across generation steps, so only the single new token's Query needs to be projected.<br/>"
         "Because modern GPUs have massive compute capability (TFLOPS) but limited memory bandwidth (GB/s), transferring large KV caches between HBM and SRAM makes token generation memory-bandwidth bound rather than compute bound."),

        ("Q3: Explain the RAG Triad / RAGAS Evaluation Framework for Production RAG.",
         "The RAG Triad evaluates three core metrics:<br/>"
         "1. <b>Context Precision / Relevance:</b> Measures the fraction of retrieved chunks that are genuinely relevant to answering the user query (detects retrieval noise).<br/>"
         "2. <b>Faithfulness / Groundedness:</b> Measures whether all factual claims in the generated response can be directly inferred from the retrieved context (detects hallucinations).<br/>"
         "3. <b>Answer Relevance:</b> Measures whether the generated answer directly addresses the user's specific question and intent."),

        ("Q4: Compare Multi-Head Attention (MHA), Multi-Query Attention (MQA), and Grouped-Query Attention (GQA).",
         "• <b>MHA (Multi-Head Attention):</b> Every attention head has its own private Query ($Q$), Key ($K$), and Value ($V$) projections. High expressiveness, but large KV cache memory footprint.<br/>"
         "• <b>MQA (Multi-Query Attention):</b> All Query heads share a single common Key and Value head. Drastically reduces KV cache size by $h\\times$, but can degrade model capacity on complex reasoning.<br/>"
         "• <b>GQA (Grouped-Query Attention):</b> Compromise used in LLaMA 3 and Qwen 2.5. Groups Query heads into $g$ groups, with each group sharing a single Key and Value head. Maintains MHA quality with MQA inference speed.")
    ]

    for q, a in ai_full:
        story.extend(make_qa(q, a, styles))

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 6: FAST CHEAT-SHEET & COMPLEXITY MATRIX
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 8))
    story.extend(create_section_header("Chapter 6: Fast Cheat-Sheet, Complexity Matrix & Latency Numbers", "Crucial reference numbers and big-O formulas for immediate recall", styles))
    add_md("## Chapter 6: Fast Cheat-Sheet, Complexity Matrix & Latency Numbers\n\n")

    cheat_data = [
        [
            Paragraph("<b>Operation / Resource</b>", styles['body_bold']),
            Paragraph("<b>Approximate Latency</b>", styles['body_bold']),
            Paragraph("<b>Scale Comparison & Mental Model</b>", styles['body_bold'])
        ],
        [
            Paragraph("<b>L1 CPU Cache Reference</b>", styles['body']),
            Paragraph("~ 1 ns", styles['body']),
            Paragraph("Fastest hardware memory lookup.", styles['body'])
        ],
        [
            Paragraph("<b>Main Memory (RAM) Access</b>", styles['body']),
            Paragraph("~ 100 ns", styles['body']),
            Paragraph("100x slower than L1 cache.", styles['body'])
        ],
        [
            Paragraph("<b>NVMe SSD Random Read</b>", styles['body']),
            Paragraph("~ 10–50 μs", styles['body']),
            Paragraph("100x to 500x slower than RAM.", styles['body'])
        ],
        [
            Paragraph("<b>Network Roundtrip (Same Datacenter)</b>", styles['body']),
            Paragraph("~ 0.5 ms", styles['body']),
            Paragraph("10x slower than SSD.", styles['body'])
        ],
        [
            Paragraph("<b>Cross-Continental Network (NYC - London)</b>", styles['body']),
            Paragraph("~ 70–100 ms", styles['body']),
            Paragraph("Speed of light in fiber constraint.", styles['body'])
        ]
    ]
    cheat_table = Table(cheat_data, colWidths=[160, 120, 260])
    cheat_table.setStyle(TableStyle([
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
    story.append(cheat_table)

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF Successfully built at: {pdf_path}")

    # Write Markdown
    with open(md_path, "w", encoding="utf-8") as f:
        f.writelines(md_lines)
    print(f"Markdown Successfully built at: {md_path}")

if __name__ == "__main__":
    build_massive_pdf_and_md()
