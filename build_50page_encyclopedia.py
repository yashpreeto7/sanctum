"""
50-Page Master Technical Interview Engineering Textbook & Comprehensive Dossier.
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib import colors
from pdf_setup import get_styles, NumberedCanvas, COLOR_PRIMARY, COLOR_SECONDARY, COLOR_ACCENT, COLOR_BRAND, COLOR_PURPLE, COLOR_CARD_BG, COLOR_BG_LIGHT, COLOR_BORDER
from large_doc_helpers import create_section_header, make_qa, make_table

def build_50page_encyclopedia():
    pdf_path = os.path.abspath("Yashpreet_Master_Interview_Preparation_Guide.pdf")
    md_path = os.path.abspath("INTERVIEW_PREPARATION_MASTER_GUIDE.md")

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=34,
        rightMargin=34,
        topMargin=44,
        bottomMargin=44
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
    # CHAPTER 1: CANDIDATE POSITIONING & BEHAVIORAL STAR PLAYBOOK (Pages 1-4)
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
    # CHAPTER 2: SOVEREIGN OS ARCHITECTURAL BLUEPRINT & SOURCE CODE WALKTHROUGH (Pages 5-14)
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

    # Let's add detailed code explanations
    sovereign_deep_modules = [
        ("server/app.py (FastAPI Gateway & WebSocket Streaming)",
         "<b>Core Responsibilities:</b> Serves the single-page reactive dashboard, manages REST APIs for calendar/inbox/approvals, persists chat history in SQLite, and handles WebSocket streaming sessions.<br/>"
         "<b>Key Implementation Details:</b><br/>"
         "• <code>@asynccontextmanager async def lifespan(app)</code>: Manages background watcher daemons (Folder Watcher, Scheduler) on startup and cleanly drains task queues on shutdown.<br/>"
         "• <code>@app.websocket('/ws/chat')</code>: Connects the browser client to LangGraph's <code>astream_events(version='v1')</code>. Emits structured JSON events: <code>node_progress</code> (updating UI pulsing pills), <code>tool_start</code>, <code>token</code> (~55 chunks/sec), and <code>done</code>.<br/>"
         "• <code>/api/calendar/event (GET, POST, PUT, DELETE)</code>: CRUD endpoints for offline/online calendar events with tombstone deletion support.<br/>"
         "• <code>/api/approvals/{id}/decision (POST)</code>: Resolves pending Human-In-The-Loop approval tokens, unpausing suspended LangGraph executions."),

        ("execution/orchestration/agent_engine.py (LangGraph State Machine DAG)",
         "<b>Core Responsibilities:</b> Defines the state machine topology, agent state schema, node execution logic, and conditional edges.<br/>"
         "<b>Key Implementation Details:</b><br/>"
         "• <code>class AgentState(TypedDict)</code>: State payload containing <code>messages: Annotated[list, add_messages]</code>, <code>context_docs: list[str]</code>, <code>planned_tool: str</code>, <code>tool_args: dict</code>, <code>approval_required: bool</code>, <code>risk_level: str</code>.<br/>"
         "• <code>build_agent_graph()</code>: Compiles the 5-tier state graph: <code>quarantine -> triaging -> [fast_reply | (retrieval -> reasoning -> hitl_gate -> tool_execution -> reasoning)]</code>.<br/>"
         "• Uses <code>MemorySaver</code> checkpointer for session persistence, allowing state recovery across crashes."),

        ("execution/security/quarantine.py (Quarantine Security Gate)",
         "<b>Core Responsibilities:</b> Protects against prompt injections, jailbreaks, Canary leakage, and unauthorized desktop privilege escalations.<br/>"
         "<b>Key Implementation Details:</b><br/>"
         "• <b>Regex Heuristics:</b> Fast regex pattern matching for known override strings ('ignore previous instructions', 'system override', 'reveal prompt').<br/>"
         "• <b>Zero-Shot Canary Tokens:</b> Injects high-entropy random GUID canary tokens into system prompt boundaries. If the output attempts to leak the canary, execution is halted immediately.<br/>"
         "• <b>Risk Scoring:</b> Categorizes queries into LOW (chit-chat), MEDIUM (read-only search), and HIGH (destructive file/calendar/email operations)."),

        ("execution/rag/hybrid_retriever.py (Hybrid Vector Search Engine)",
         "<b>Core Responsibilities:</b> Provides unified dense + sparse document retrieval across personal notes, documentation, and chat memories.<br/>"
         "<b>Key Implementation Details:</b><br/>"
         "• <b>Dense Vector Search:</b> Embeds documents using <code>sentence-transformers/all-MiniLM-L6-v2</code> (384 dimensions) and stores vectors in local Qdrant collection with HNSW index.<br/>"
         "• <b>Sparse Lexical Search:</b> Inverted index scored using BM25 ($k_1=1.5, b=0.75$).<br/>"
         "• <b>Reciprocal Rank Fusion (RRF):</b> Merges top-k rankings: $RRF(d) = \\sum_{m} \\frac{1}{60 + rank_m(d)}$. Guarantees keyword precision and semantic recall."),

        ("execution/tools/calendar_connector.py (Offline-First Calendar Engine)",
         "<b>Core Responsibilities:</b> Synchronizes events with Google Calendar API while maintaining a 100% functional offline JSON cache.<br/>"
         "<b>Key Implementation Details:</b><br/>"
         "• <b>Composite Keys:</b> Index events locally by composite tuple <code>(summary, start_time[:16])</code> to prevent duplication across repeated sync passes.<br/>"
         "• <b>Tombstone Ledger:</b> Offline deletions append records to <code>deleted_calendar_events.json</code>. Sync logic processes tombstones first against remote Google API before upserting active events."),

        ("execution/tools/gmail_connector.py (Gmail Triage & Dispatch Engine)",
         "<b>Core Responsibilities:</b> Fetches unread emails, parses RFC 2822 / MIME message structures, classifies priority, and drafts replies.<br/>"
         "<b>Key Implementation Details:</b><br/>"
         "• Decodes base64url-encoded message bodies and extracts plain text from multi-part MIME payloads.<br/>"
         "• LLM triaging classifies emails into URGENT, ACTIONABLE, NEWSLETTER, or SPAM, synthesizing 1-click contextual reply drafts saved directly into Obsidian vault."),

        ("execution/tools/obsidian_workspace.py (Obsidian Vault Markdown Engine)",
         "<b>Core Responsibilities:</b> Bi-directional synchronization with local Obsidian markdown notes.<br/>"
         "<b>Key Implementation Details:</b><br/>"
         "• Parses Markdown AST to extract YAML frontmatter metadata (tags, created_date, status).<br/>"
         "• Header-level chunking: Slices markdown by `# H1` and `## H2` headings so each chunk maintains semantic integrity before vector embedding.<br/>"
         "• Appends daily log entries and executive briefings into `Daily Notes/` with ISO timestamps."),

        ("execution/tools/mcp_manager.py (Model Context Protocol Host)",
         "<b>Core Responsibilities:</b> Anthropic MCP client implementation over JSON-RPC 2.0 stdio transport.<br/>"
         "<b>Key Implementation Details:</b><br/>"
         "• Launches sandboxed Node.js / Python MCP servers (`@modelcontextprotocol/server-filesystem`, `@modelcontextprotocol/server-sqlite`) as subprocesses.<br/>"
         "• Handshakes via `tools/list` on startup, converting MCP JSON schemas into LangChain tool definitions at runtime.<br/>"
         "• Dispatches calls asynchronously via `tools/call` over stdin/stdout pipes with configurable timeouts."),

        ("execution/tools/folder_watcher.py (Automated File Ingestion)",
         "<b>Core Responsibilities:</b> Monitors specified directories using OS filesystem events (`watchdog`) and automatically parses and vectorizes dropped files.<br/>"
         "<b>Key Implementation Details:</b><br/>"
         "• Supports `.pdf` (pypdf/pdfplumber), `.txt`, `.md`, `.json`, and `.py` source files.<br/>"
         "• Chunks text, generates embeddings, and upserts payloads into Qdrant collection with file path and modification timestamp metadata."),

        ("server/dashboard_template.py (Reactive Cyber HUD Frontend)",
         "<b>Core Responsibilities:</b> High-performance Single Page Application (SPA) dashboard styled with modern cyber aesthetics.<br/>"
         "<b>Key Implementation Details:</b><br/>"
         "• Native JavaScript DOM rendering with zero bloated framework overhead.<br/>"
         "• WebSocket client with exponential backoff auto-reconnection and conversation session switching.<br/>"
         "• Web Audio API `AnalyserNode` frequency spectrum visualizer (CAVA-style music equalizer).<br/>"
         "• Collapsible tool execution detail cards and 3-way Calendar view switcher (Month, Week, Agenda).")
    ]

    for title, desc in sovereign_deep_modules:
        story.append(Paragraph(f"<b>{title}</b>", styles['h3']))
        story.append(Paragraph(desc, styles['body']))
        story.append(Spacer(1, 4))
        add_md(f"#### {title}\n{desc.replace('<b>', '**').replace('</b>', '**').replace('<br/>', '\n')}\n\n")

    # ──────────────────────────────────────────────────────────────────────────
    # CHAPTER 3: 30 SOVEREIGN OS INTERVIEW QUESTIONS
    # ──────────────────────────────────────────────────────────────────────────
    story.append(Paragraph("2.3 Top 30 Technical Interview Q&As on SovereignOS", styles['h2']))
    add_md("### 2.3 Top 30 Technical Interview Q&As on SovereignOS\n\n")

    for q, a in sovereign_30_qa:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # ──────────────────────────────────────────────────────────────────────────
    # CHAPTER 4: COMPLETE PORTFOLIO BREAKDOWN (Pages 15-20)
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

    for q, a in macrolens_qa:
        story.extend(make_qa(q, a, styles))

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
    # CHAPTER 5: OPERATING SYSTEMS & LOW-LEVEL CONCURRENCY (Pages 21-27)
    # ──────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 4: Operating Systems & Low-Level Concurrency Masterclass", "Processes, Threads, Linux Kernel Internals, Virtual Memory, Memory Models, and Synchronization", styles))
    add_md("## Chapter 4: Operating Systems & Low-Level Concurrency Masterclass\n\n")

    for q, a in os_master_qa:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # Additional deep OS Q&As
    os_extra_qa = [
        ("Q7: Linux I/O Multiplexing: `select` vs `poll` vs `epoll` (Level-Triggered vs Edge-Triggered).",
         "• <b>select():</b> $O(N)$ linear scan over bitmap of file descriptors. Limited to `FD_SETSIZE` (typically 1024). Memory must be re-initialized before each call.<br/>"
         "• <b>poll():</b> $O(N)$ linear scan over array of `pollfd` structs. Removes 1024 FD limit, but still requires copying array between user space and kernel space on every call.<br/>"
         "• <b>epoll() (Linux kernel 2.6+):</b> $O(1)$ event-driven multiplexer. Stores monitored FDs in a kernel red-black tree (`epoll_ctl`) and uses a ready list populated by kernel device interrupts. `epoll_wait` returns only ready FDs.<br/>"
         "• <b>Level-Triggered (LT) vs Edge-Triggered (ET):</b> LT signals readiness as long as buffer has data; ET signals only when state transitions from unready to ready (requires non-blocking sockets reading in a loop until `EAGAIN`/`EWOULDBLOCK`)."),

        ("Q8: Linux Completely Fair Scheduler (CFS) and Virtual Runtime (`vruntime`).",
         "CFS is the default Linux CPU process scheduler for normal tasks (`SCHED_OTHER`).<br/>"
         "• <b>vruntime (Virtual Runtime):</b> Measures amount of CPU execution time allocated to a task, scaled inversely by its `nice` priority (higher nice = slower vruntime accumulation).<br/>"
         "• <b>Red-Black Tree:</b> CFS maintains tasks in a Red-Black Tree sorted by `vruntime`. The leftmost node has the smallest `vruntime` (most starved of CPU). CFS always selects the leftmost node to run next in $O(1)$ time, maintaining perfect proportional fairness across all tasks.")
    ]
    for q, a in os_extra_qa:
        story.extend(make_qa(q, a, styles))

    # ──────────────────────────────────────────────────────────────────────────
    # CHAPTER 6: COMPUTER NETWORKS & DISTRIBUTED TRANSPORT (Pages 28-34)
    # ──────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 5: Computer Networks & Distributed Web Transport Masterclass", "OSI 7 Layers, TCP Congestion Control, TLS 1.3 Cryptography, HTTP/2 & HTTP/3 QUIC", styles))
    add_md("## Chapter 5: Computer Networks & Distributed Web Transport Masterclass\n\n")

    for q, a in net_master_qa:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # Additional deep Network Q&As
    net_extra_qa = [
        ("Q6: Deep Dive into WebSocket Protocol Framing (RFC 6455).",
         "WebSockets initiate via an HTTP 101 Upgrade handshake with `Sec-WebSocket-Key` (SHA-1 hashed with magic GUID `258EAFA5-E914-47DA-95CA-C5AB0DC85B11`).<br/>"
         "• <b>Frame Format:</b> (1) `FIN` bit (1 bit: indicates final fragment); (2) `Opcode` (4 bits: 0x1 text, 0x2 binary, 0x8 close, 0x9 ping, 0xA pong); (3) `MASK` bit (1 bit: client-to-server frames MUST be masked with 4-byte XOR mask to prevent cache poisoning in intermediaries); (4) `Payload Length` (7 bits, 7+16 bits for <=64KB, 7+64 bits for >64KB).<br/>"
         "• <b>Overhead:</b> Minimal 2 to 14 bytes per frame vs hundreds of bytes in HTTP headers."),

        ("Q7: Cross-Origin Resource Sharing (CORS), Preflight OPTIONS, and Security Pitfalls.",
         "CORS is a browser security mechanism enforcing the Same-Origin Policy (Same Scheme, Host, Port).<br/>"
         "• <b>Simple Requests:</b> GET, POST, HEAD with standard headers (`text/plain`, `multipart/form-data`, `application/x-www-form-urlencoded`). Browser sends request with `Origin` header; server responds with `Access-Control-Allow-Origin`.<br/>"
         "• <b>Preflight Requests:</b> Custom headers (`Authorization`, `X-Custom-Header`) or non-simple content-types (`application/json`) trigger an automated `OPTIONS` preflight request checking `Access-Control-Allow-Methods` and `Access-Control-Allow-Headers` before dispatching the real payload.<br/>"
         "• <b>Security Pitfall:</b> Using `Access-Control-Allow-Origin: *` alongside `Access-Control-Allow-Credentials: true` is strictly prohibited by browsers to prevent cross-site session hijacking.")
    ]
    for q, a in net_extra_qa:
        story.extend(make_qa(q, a, styles))

    # ──────────────────────────────────────────────────────────────────────────
    # CHAPTER 7: DATABASE MANAGEMENT SYSTEMS & STORAGE (Pages 35-41)
    # ──────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 6: Database Management Systems & Indexing Masterclass", "B+ Trees vs HNSW Vectors, ACID Transactions, MVCC, Isolation Levels & Sharding", styles))
    add_md("## Chapter 6: Database Management Systems & Indexing Masterclass\n\n")

    for q, a in db_master_qa:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # Additional deep DBMS Q&As
    db_extra_qa = [
        ("Q5: Write-Ahead Logging (WAL) and Crash Recovery Algorithms (ARIES).",
         "• <b>WAL Rule:</b> Before any modified in-memory database page (dirty page) is flushed to disk, the corresponding log record describing the change MUST be written and fsynced to non-volatile log storage.<br/>"
         "• <b>ARIES Recovery Algorithm:</b> Executes in 3 passes after a crash:<br/>"
         "  1. <i>Analysis Pass:</i> Scans log forward from last checkpoint to determine active transactions and dirty pages at time of crash.<br/>"
         "  2. <i>Redo Pass:</i> Scans forward from earliest dirty page log sequence number (LSN) and replays all committed and uncommitted operations to restore state.<br/>"
         "  3. <i>Undo Pass:</i> Scans backward, undoing the operations of all active (uncommitted) transactions and writing Compensation Log Records (CLRs)."),

        ("Q6: SQL Join Algorithms: Nested Loop Join, Hash Join, and Sort-Merge Join.",
         "• <b>Nested Loop Join:</b> For each outer row, scans inner table. $O(M \\times N)$. Optimal when outer table is very small and inner table has an index ($O(M \\log N)$).<br/>"
         "• <b>Hash Join:</b> Builds an in-memory hash table on the smaller table's join key, then streams and probes the larger table. $O(M + N)$ time and $O(\\min(M, N))$ memory. Best for large unsorted equi-joins.<br/>"
         "• <b>Sort-Merge Join:</b> Sorts both tables by join key ($O(M \\log M + N \\log N)$), then merges sequentially ($O(M + N)$). Best when data is already sorted by index or clustered key.")
    ]
    for q, a in db_extra_qa:
        story.extend(make_qa(q, a, styles))

    # ──────────────────────────────────────────────────────────────────────────
    # CHAPTER 8: SYSTEM DESIGN & DISTRIBUTED ARCHITECTURE (Pages 42-47)
    # ──────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 7: System Design & Enterprise Architecture Masterclass", "CAP Theorem, Caching, Rate Limiting, Consistent Hashing, Saga & Microservice Patterns", styles))
    add_md("## Chapter 7: System Design & Enterprise Architecture Masterclass\n\n")

    for q, a in sys_master_qa:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # Additional deep System Design Q&As
    sys_extra_qa = [
        ("Q4: Cache Stampede (Thundering Herd) Solutions: Mutex Locking vs Probabilistic Early Expiration (XFetch).",
         "• <b>Problem:</b> When a popular hot cache key expires, thousands of concurrent requests miss the cache simultaneously and query the database at once, causing DB failure.<br/>"
         "• <b>Mutex Lock (Single-Flight):</b> The first worker that detects cache miss acquires a distributed lock (Redis `SET key value NX EX 5`), queries DB, and updates cache. Other workers wait or retry.<br/>"
         "• <b>Probabilistic Early Expiration (XFetch Algorithm):</b> Computes an early recomputation trigger: $\\Delta - \\beta \\times \\ln(rand()) > \\text{TTL}$, where $\\Delta$ is computation time and $\\beta > 0$. As TTL nears expiration, incoming requests probabilistically refresh the cache in the background before it officially expires."),

        ("Q5: Distributed Idempotency in Payment & Order Processing Systems.",
         "• <b>Idempotency Key:</b> Client generates a unique UUID (e.g. `Idempotency-Key: 7b8e...`) in request headers.<br/>"
         "• <b>Processing Flow:</b> (1) Server checks Redis/Postgres for existing idempotency key; (2) If found with status `COMPLETED`, returns cached response immediately; (3) If found with `PROCESSING`, returns HTTP 409 Conflict; (4) If not found, inserts key with status `PROCESSING` within atomic transaction, executes payment, updates status to `COMPLETED`, and saves response payload.")
    ]
    for q, a in sys_extra_qa:
        story.extend(make_qa(q, a, styles))

    # ──────────────────────────────────────────────────────────────────────────
    # CHAPTER 9: MODERN AI & LLM SYSTEMS ENGINEERING (Pages 48-52)
    # ──────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 8: Modern AI & LLM Systems Engineering Masterclass", "Transformer Attention Mathematics, KV Caching, Quantization, RAGAS & Agent Protocols", styles))
    add_md("## Chapter 8: Modern AI & LLM Systems Engineering Masterclass\n\n")

    for q, a in ai_master_qa:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # Additional AI Q&As
    ai_extra_qa = [
        ("Q5: Deep Dive: Quantization Techniques (FP16 vs INT8 vs INT4 - GPTQ, AWQ, GGUF).",
         "Quantization reduces memory footprint and increases inference throughput by lowering precision of model weights and activations.<br/>"
         "• <b>Post-Training Quantization (PTQ):</b> Converts weights after training without retraining.<br/>"
         "• <b>GPTQ (Generalized Post-Training Quantization):</b> Layer-wise second-order Taylor approximation minimizing MSE loss between full-precision and quantized weights ($O(W^T H W)$).<br/>"
         "• <b>AWQ (Activation-aware Weight Quantization):</b> Observes that only 1% of salient weight channels protect model accuracy; preserves salient weights in higher precision and quantizes remaining 99%.<br/>"
         "• <b>GGUF (GPT-Generated Unified Format):</b> Binary file format used by `llama.cpp` and Ollama storing quantized weights, tokenizer vocabulary, and hyperparameter metadata in a single portable file for CPU/GPU offloading."),

        ("Q6: Advanced Agentic Design Patterns: ReAct vs Plan-and-Solve vs Reflection vs Multi-Agent Swarms.",
         "• <b>ReAct (Reasoning + Acting):</b> Interleaves reasoning steps ('Thought') with tool invocations ('Action') and environment feedback ('Observation') in a cyclical loop.<br/>"
         "• <b>Plan-and-Solve:</b> Decomposes a complex goal into an explicit step-by-step plan first, then executes steps sequentially, updating the plan upon error.<br/>"
         "• <b>Reflection / Self-Correction:</b> Agent evaluates its own generated output against test cases or critique rubrics, producing critique feedback and iterating.<br/>"
         "• <b>Multi-Agent Supervisor:</b> Central controller routes tasks to specialized domain agents (Coder, Searcher, Reviewer), aggregates findings, and produces the final answer.")
    ]
    for q, a in ai_extra_qa:
        story.extend(make_qa(q, a, styles))

    # ──────────────────────────────────────────────────────────────────────────
    # CHAPTER 10: ALGORITHMIC PATTERNS & DATA STRUCTURES (Pages 53-56)
    # ──────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 9: Core Algorithmic Patterns & LeetCode High-Frequency Solutions", "Mastery of 10 Fundamental Algorithmic Paradigms with Clean Code & Complexity Analysis", styles))
    add_md("## Chapter 9: Core Algorithmic Patterns & LeetCode High-Frequency Solutions\n\n")

    story.append(Paragraph("9.1 Classic Data Structures Complexity Matrix", styles['h2']))
    t_ds = make_table(ds_matrix[0], ds_matrix[1:], [140, 75, 75, 75, 75, 75], styles)
    story.append(t_ds)
    story.append(Spacer(1, 8))

    algo_patterns = [
        ("1. Two Pointers (e.g. 3Sum, Container With Most Water)",
         "<b>Core Concept:</b> Maintain left and right indices converging toward each other in a sorted array, reducing $O(N^2)$ brute force to $O(N)$.<br/>"
         "<code>def two_sum_sorted(nums, target):<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;l, r = 0, len(nums) - 1<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;while l < r:<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;curr = nums[l] + nums[r]<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if curr == target: return [l, r]<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;elif curr < target: l += 1<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else: r -= 1<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;return []</code>"),

        ("2. Sliding Window (e.g. Longest Substring Without Repeating Characters)",
         "<b>Core Concept:</b> Expand right pointer to include elements; shrink left pointer when window condition is violated. Achieves $O(N)$ linear time.<br/>"
         "<code>def length_of_longest_substring(s: str) -> int:<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;char_map, max_len, l = {}, 0, 0<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;for r, char in enumerate(s):<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if char in char_map and char_map[char] >= l:<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;l = char_map[char] + 1<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;char_map[char] = r<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;max_len = max(max_len, r - l + 1)<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;return max_len</code>"),

        ("3. Monotonic Stack (e.g. Next Greater Element, Daily Temperatures)",
         "<b>Core Concept:</b> Maintain a stack of indices with strictly monotonic values. When a larger element is found, pop and resolve all smaller pending elements in $O(N)$ time.<br/>"
         "<code>def daily_temperatures(temperatures: list[int]) -> list[int]:<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;res = [0] * len(temperatures)<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;stack = []  # indices<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;for i, t in enumerate(temperatures):<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;while stack and t > temperatures[stack[-1]]:<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;prev_idx = stack.pop()<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;res[prev_idx] = i - prev_idx<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;stack.append(i)<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;return res</code>"),

        ("4. Graph BFS / Dijkstra's Shortest Path Algorithm",
         "<b>Core Concept:</b> Use Min-Heap (Priority Queue) to greedily expand shortest tentative distance nodes in $O((V + E) \\log V)$ time.<br/>"
         "<code>import heapq<br/>"
         "def dijkstra(n, edges, src):<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;adj = {i: [] for i in range(n)}<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;for u, v, w in edges: adj[u].append((v, w))<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;dist = {i: float('inf') for i in range(n)}<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;dist[src] = 0; pq = [(0, src)]<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;while pq:<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;d, u = heapq.heappop(pq)<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if d > dist[u]: continue<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for v, w in adj[u]:<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if dist[u] + w < dist[v]:<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dist[v] = dist[u] + w<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;heapq.heappush(pq, (dist[v], v))<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;return dist</code>")
    ]

    for title, code_snippet in algo_patterns:
        story.append(Paragraph(f"<b>{title}</b>", styles['h3']))
        story.append(Paragraph(code_snippet, styles['body']))
        story.append(Spacer(1, 4))

    # ──────────────────────────────────────────────────────────────────────────
    # CHAPTER 11: INTERVIEW DAY QUICK REFERENCE & FORMULAS (Pages 57-58)
    # ──────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 10: Interview Day Fast Reference, Latency Numbers & Estimation Formulas", "Key numerical formulas, latency numbers, and top 10 interview pitfalls to avoid", styles))
    add_md("## Chapter 10: Interview Day Fast Reference, Latency Numbers & Estimation Formulas\n\n")

    story.append(Paragraph("10.1 Latency Numbers Every Software Engineer Must Memorize", styles['h2']))
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
    story.append(Spacer(1, 8))

    story.append(Paragraph("10.2 System Design Quantitative Estimation Formulas", styles['h2']))
    story.append(Paragraph(sd_math, styles['body']))
    story.append(Spacer(1, 8))

    story.append(Paragraph("10.3 Top 10 Red Flags in Technical Interviews and How to Avoid Them", styles['h2']))
    red_flags = [
        "1. <b>Jumping into code without clarifying inputs and constraints:</b> Always confirm data types, scale ($N$), negative numbers, null values, and edge cases first.",
        "2. <b>Coding in total silence:</b> Narrate your thought process out loud. Interviewers care more about your problem-solving decomposition than raw syntax recall.",
        "3. <b>Assuming pure dense vector search is universally optimal:</b> Always defend Hybrid Search (Dense Vectors + BM25 Lexical) when discussing search engines.",
        "4. <b>Ignoring single points of failure in System Design:</b> Always mention load balancers, database read replicas, replication lag, and circuit breakers.",
        "5. <b>Claiming your project has no trade-offs:</b> Be proactive and transparent about technical constraints (e.g. local 7B quantization latency vs cloud 70B models) and how you engineered fallbacks.",
        "6. <b>Neglecting Database Indexing costs:</b> Mention that while indexes speed up `SELECT` reads ($O(\\log N)$), they incur write penalties on `INSERT`/`UPDATE` and consume memory.",
        "7. <b>Confusing Concurrency with Parallelism:</b> Concurrency is dealing with lots of things at once (structure); parallelism is doing lots of things at once (execution).",
        "8. <b>Writing brute force without stating time complexity:</b> State the brute force complexity first ($O(N^2)$), then guide the interviewer to the optimized approach ($O(N \\log N)$ or $O(N)$).",
        "9. <b>Forgetting error handling in API design:</b> Always return standard HTTP status codes (200, 201, 400, 401, 403, 404, 409, 429, 500) and structured JSON error responses.",
        "10. <b>Not asking thoughtful questions at the end:</b> Ask questions about engineering culture, deployment frequency, architectural challenges, and team velocity."
    ]
    for rf in red_flags:
        story.append(Paragraph(rf, styles['body']))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"50-Page Master Encyclopedia PDF successfully compiled at: {pdf_path}")

    with open(md_path, "w", encoding="utf-8") as f:
        f.writelines(md_lines)
    print(f"50-Page Master Encyclopedia Markdown successfully compiled at: {md_path}")

if __name__ == "__main__":
    build_50page_encyclopedia()
