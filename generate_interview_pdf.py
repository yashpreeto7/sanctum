"""
Comprehensive In-Depth Technical Interview Master Dossier Generator for Yashpreet.
Builds:
1. Yashpreet_Master_Interview_Preparation_Guide.pdf (ReportLab Multi-Page Document)
2. INTERVIEW_PREPARATION_MASTER_GUIDE.md (Full Markdown Compendium)
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# Palette Definition
COLOR_PRIMARY = colors.HexColor("#0f172a")    # Slate 900
COLOR_SECONDARY = colors.HexColor("#1e293b")  # Slate 800
COLOR_ACCENT = colors.HexColor("#0284c7")     # Sky 600
COLOR_BRAND = colors.HexColor("#d97706")      # Amber 600
COLOR_PURPLE = colors.HexColor("#7c3aed")     # Violet 600
COLOR_EMERALD = colors.HexColor("#059669")    # Emerald 600
COLOR_BG_LIGHT = colors.HexColor("#f8fafc")   # Slate 50
COLOR_CARD_BG = colors.HexColor("#f1f5f9")    # Slate 100
COLOR_TEXT = colors.HexColor("#334155")       # Slate 700
COLOR_MUTED = colors.HexColor("#64748b")      # Slate 500
COLOR_BORDER = colors.HexColor("#cbd5e1")     # Slate 300
COLOR_CODE_BG = colors.HexColor("#1e1e2e")    # Dark Catppuccin
COLOR_CODE_BORDER = colors.HexColor("#313244")

class NumberedCanvas(canvas.Canvas):
    """Adds running headers and 'Page X of Y' dynamic footers across all pages."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(COLOR_MUTED)

        # Header on pages > 1
        if self._pageNumber > 1:
            self.drawString(44, 752, "Yashpreet — Technical Interview Master Dossier & Engineering Manual")
            self.drawRightString(612 - 44, 752, "SovereignOS • MERN • Core CS • AI Systems")
            self.setStrokeColor(COLOR_BORDER)
            self.setLineWidth(0.5)
            self.line(44, 744, 612 - 44, 744)

        # Footer on all pages
        self.setStrokeColor(COLOR_BORDER)
        self.setLineWidth(0.5)
        self.line(44, 42, 612 - 44, 42)
        
        self.drawString(44, 30, "Confidential • Prepared for Technical Interview • VIT Bhopal CSE (2026)")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 44, 30, page_str)
        self.restoreState()


def build_pdf(pdf_path):
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=38,
        rightMargin=38,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=COLOR_PRIMARY,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=COLOR_ACCENT,
        spaceAfter=10
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=COLOR_PRIMARY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=COLOR_SECONDARY,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'SectionH3',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13.5,
        textColor=COLOR_BRAND,
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=COLOR_TEXT,
        spaceAfter=4
    )

    body_bold = ParagraphStyle(
        'BodyDarkBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    qa_q_style = ParagraphStyle(
        'QA_Question',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=COLOR_PRIMARY,
        spaceBefore=6,
        spaceAfter=2,
        keepWithNext=True
    )

    qa_a_style = ParagraphStyle(
        'QA_Answer',
        parent=body_style,
        fontSize=8.2,
        leading=11.8,
        textColor=COLOR_TEXT,
        leftIndent=6,
        spaceAfter=5
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=body_style,
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12.5,
        textColor=COLOR_PRIMARY
    )

    story = []

    # ──────────────────────────────────────────────────────────────────────────
    # TITLE & HEADER
    # ──────────────────────────────────────────────────────────────────────────
    story.append(Paragraph("Yashpreet — Technical Interview Master Engineering Dossier", title_style))
    story.append(Paragraph("Exhaustive Codebase Breakdown • Architecture • Core CS Foundations • System Design • AI Engineering", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_ACCENT, spaceBefore=2, spaceAfter=8))

    meta_table_data = [
        [
            Paragraph("<b>Candidate:</b> Yashpreet", body_style),
            Paragraph("<b>Education:</b> B.Tech in CSE (VIT Bhopal, CGPA: 8.47/10)", body_style),
            Paragraph("<b>Target Roles:</b> SDE / Full-Stack / AI Systems", body_style)
        ],
        [
            Paragraph("<b>Email:</b> yash09preet@gmail.com", body_style),
            Paragraph("<b>GitHub:</b> github.com/yashpreeto7 (22 Repos)", body_style),
            Paragraph("<b>LinkedIn:</b> linkedin.com/in/yashpreeto7", body_style)
        ]
    ]
    meta_table = Table(meta_table_data, colWidths=[160, 220, 156])
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
    story.append(Spacer(1, 8))

    # ──────────────────────────────────────────────────────────────────────────
    # MODULE 1: STRATEGIC ELEVATOR PITCH & STAR SCENARIOS
    # ──────────────────────────────────────────────────────────────────────────
    story.append(Paragraph("Module 1: Candidate Positioning & Behavioral STAR Playbook", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.75, color=COLOR_BORDER, spaceBefore=1, spaceAfter=6))

    story.append(Paragraph("1.1 The 90-Second High-Impact Self-Introduction", h2_style))
    intro_p = (
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
    story.append(Paragraph(intro_p, callout_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("1.2 Behavioral Scenarios Matrix (STAR Method)", h2_style))
    star_data = [
        [
            Paragraph("<b>Scenario & Competency</b>", body_bold),
            Paragraph("<b>Situation & Task (S/T)</b>", body_bold),
            Paragraph("<b>Action & Engineering Solution (A)</b>", body_bold),
            Paragraph("<b>Result & Impact (R)</b>", body_bold)
        ],
        [
            Paragraph("<b>Debugging Under Pressure (Concurrency)</b>", body_style),
            Paragraph("During WebSocket streaming in SovereignOS, sub-agents executing background tools caused async event-loop deadlocks and delayed first-token delivery by 3-5 seconds.", body_style),
            Paragraph("Refactored the async pipeline to use LangGraph's <code>astream_events(version='v1')</code>, streaming node progress events asynchronously while buffering tool execution in decoupled coroutines.", body_style),
            Paragraph("First-token latency dropped from <b>4.2s to 120ms</b> with steady 55 tokens/sec emission. 100% deadlock elimination.", body_style)
        ],
        [
            Paragraph("<b>System Design Under Ambiguity (Search Engine)</b>", body_style),
            Paragraph("Needed a search engine for local desktop documents and code that could find exact filenames/symbols as well as broad conceptual semantics.", body_style),
            Paragraph("Designed a <b>Hybrid RAG pipeline</b> combining Qdrant dense cosine similarity (<code>all-MiniLM-L6-v2</code>) with BM25 sparse keyword ranking via Reciprocal Rank Fusion ($k=60$).", body_style),
            Paragraph("Search recall jumped by <b>34%</b> compared to pure vector search, especially on code symbols, file paths, and dates.", body_style)
        ],
        [
            Paragraph("<b>Security & Risk Management (Adversarial AI)</b>", body_style),
            Paragraph("Unchecked emails or untrusted notes injected into agent context could trigger unauthorized destructive actions (e.g. deleting files, sending mass emails).", body_style),
            Paragraph("Built a multi-layer <b>Quarantine Security Gate</b>: zero-shot canary checks, regex sanitization, and async Human-In-The-Loop (HITL) approval tokens for destructive tools.", body_style),
            Paragraph("Neutralized 100% of prompt injection test suites; prevented autonomous high-risk operations without explicit user confirmation.", body_style)
        ]
    ]
    star_table = Table(star_data, colWidths=[105, 135, 185, 111])
    star_table.setStyle(TableStyle([
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
    story.append(star_table)
    story.append(Spacer(1, 8))

    # ──────────────────────────────────────────────────────────────────────────
    # MODULE 2: SOVEREIGN OS ARCHITECTURAL DEEP DIVE
    # ──────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Module 2: Flagship Project Deep Dive — SovereignOS", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.75, color=COLOR_BORDER, spaceBefore=1, spaceAfter=6))

    story.append(Paragraph("2.1 High-Level Architecture & File-by-File Engineering Breakdown", h2_style))
    story.append(Paragraph(
        "SovereignOS is an autonomous, local-first personal AI operating system. The codebase is engineered across clean architectural layers:",
        body_style
    ))

    codebase_files = [
        [
            Paragraph("<b>Module / File Path</b>", body_bold),
            Paragraph("<b>Architectural Layer</b>", body_bold),
            Paragraph("<b>Key Classes / Functions</b>", body_bold),
            Paragraph("<b>Core Engineering Role</b>", body_bold)
        ],
        [
            Paragraph("<code>server/app.py</code>", body_style),
            Paragraph("API & Networking Gateway", body_style),
            Paragraph("<code>websocket_chat</code>, <code>ConnectionManager</code>, <code>Lifespan</code>", body_style),
            Paragraph("FastAPI ASGI server, WebSockets streaming, background scheduler daemons, SQLite chat persistence, and REST endpoints.", body_style)
        ],
        [
            Paragraph("<code>execution/orchestration/agent_engine.py</code>", body_style),
            Paragraph("LangGraph State Machine", body_style),
            Paragraph("<code>AgentState</code>, <code>build_graph</code>, <code>quarantine_node</code>, <code>reasoning_node</code>", body_style),
            Paragraph("5-tier cyclical state graph with conditional edges, channel reducers, checkpointing, and tool planning loops.", body_style)
        ],
        [
            Paragraph("<code>execution/security/quarantine.py</code>", body_style),
            Paragraph("Security & Threat Gate", body_style),
            Paragraph("<code>QuarantineSecurityGate</code>, <code>evaluate_threat</code>, <code>canary_check</code>", body_style),
            Paragraph("Detects prompt injection, jailbreak attempts, system overrides, and assigns risk levels (LOW, MEDIUM, HIGH).", body_style)
        ],
        [
            Paragraph("<code>execution/rag/hybrid_retriever.py</code>", body_style),
            Paragraph("Hybrid Vector Search", body_style),
            Paragraph("<code>HybridRAGRetriever</code>, <code>qdrant_search</code>, <code>bm25_rank</code>, <code>reciprocal_rank_fusion</code>", body_style),
            Paragraph("Combines Qdrant dense vector cosine similarity (<code>all-MiniLM-L6-v2</code>) with BM25 sparse keyword ranking via RRF ($k=60$).", body_style)
        ],
        [
            Paragraph("<code>execution/tools/calendar_connector.py</code>", body_style),
            Paragraph("Calendar Sync & Offline Engine", body_style),
            Paragraph("<code>GoogleCalendarConnector</code>, <code>_upsert_local_event</code>, <code>_record_tombstone</code>", body_style),
            Paragraph("Google Calendar API integration with offline JSON caching, composite-key deduplication, and tombstone deletion.", body_style)
        ],
        [
            Paragraph("<code>execution/tools/gmail_connector.py</code>", body_style),
            Paragraph("Gmail Triage & Dispatch", body_style),
            Paragraph("<code>GmailConnector</code>, <code>list_unread_messages</code>, <code>send_email</code>, <code>draft_reply</code>", body_style),
            Paragraph("Google Gmail API integration, MIME message decoding, unread email ML classification, and contextual AI draft generation.", body_style)
        ],
        [
            Paragraph("<code>execution/tools/mcp_manager.py</code>", body_style),
            Paragraph("Model Context Protocol (MCP)", body_style),
            Paragraph("<code>MCPManager</code>, <code>MCPClient</code>, <code>start_server</code>, <code>call_tool</code>", body_style),
            Paragraph("Launches sandboxed background MCP servers over JSON-RPC 2.0 stdio, dynamically mounting external tool schemas.", body_style)
        ],
        [
            Paragraph("<code>execution/tools/obsidian_workspace.py</code>", body_style),
            Paragraph("Knowledge Vault Parser", body_style),
            Paragraph("<code>ObsidianVaultConnector</code>, <code>parse_markdown_ast</code>, <code>extract_frontmatter</code>", body_style),
            Paragraph("AST Markdown parser, frontmatter extractor, header-level note chunker, and bidirectional daily log appender.", body_style)
        ],
        [
            Paragraph("<code>server/dashboard_template.py</code>", body_style),
            Paragraph("Frontend UI & Audio Engine", body_style),
            Paragraph("<code>DASHBOARD_HTML</code>, <code>handleWsMessage</code>, <code>startMusicVisualizerLoop</code>", body_style),
            Paragraph("Single-page reactive cyber HUD, WebSockets streaming consumer, Web Audio AnalyserNode spectrum visualizer, theme switcher.", body_style)
        ]
    ]
    cb_table = Table(codebase_files, colWidths=[120, 95, 135, 186])
    cb_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [COLOR_BG_LIGHT, COLOR_CARD_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(cb_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("2.2 Deep Dive Technical Interview Q&A on SovereignOS", h2_style))

    sovereign_qa = [
        ("Q1: Walk me through the exact lifecycle of a user prompt from input to streaming response in SovereignOS.",
         "<b>Answer:</b><br/>"
         "1. <b>Transport:</b> Prompt arrives at <code>/ws/chat</code> via WebSocket JSON payload (<code>command, session_id, thread_id</code>).<br/>"
         "2. <b>State Initialization:</b> <code>initial_state</code> is created with <code>AgentState</code> (messages, chat history, retrieval context).<br/>"
         "3. <b>Node 1 (Quarantine):</b> Evaluates prompt for injection/jailbreak tokens via regex rules + zero-shot canary checks. Sets <code>risk_level</code> (LOW, MEDIUM, HIGH).<br/>"
         "4. <b>Node 2 (Triaging):</b> Classifies query intent. If chit-chat, routes directly to final output. If actionable, routes to retrieval.<br/>"
         "5. <b>Node 3 (Hybrid RAG):</b> Embeds query via <code>all-MiniLM-L6-v2</code>, queries Qdrant dense index + BM25 sparse index, and combines top results using Reciprocal Rank Fusion ($k=60$).<br/>"
         "6. <b>Node 4 (Reasoning):</b> Invokes local Qwen 2.5 7B with retrieved context. Emits structured tool plan or direct answer.<br/>"
         "7. <b>Node 5 (HITL Policy Gate):</b> Checks if tool requires user confirmation (e.g. file deletion). If yes, pauses graph and sends approval request token via WebSocket.<br/>"
         "8. <b>Node 6 (Tool Execution):</b> Executes approved tool (MCP, Gmail, Calendar, Obsidian) and feeds observation back to Node 4.<br/>"
         "9. <b>Streaming Emission:</b> Output is streamed word-by-word (~55 chunks/sec) over WebSocket with final markdown formatting on <code>done</code> event."),

        ("Q2: Why did you implement Hybrid Search (Qdrant + BM25 + RRF) instead of pure vector search?",
         "<b>Answer:</b> Pure dense vector search computes cosine similarity in embedding space. While effective for semantic concepts ('how to get better sleep' $\\rightarrow$ 'sleep hygiene tips'), it fails catastrophically on exact keyword queries ('meeting on 2026-08-31', 'function selectChatSession', 'error 10048'). BM25 provides exact token frequency/inverse document frequency weighting. By combining both with <b>Reciprocal Rank Fusion</b>: $RRF(d) = \\sum \\frac{1}{k + rank_i(d)}$ (with $k=60$), technical tokens and exact dates receive highest priority, while semantic synonyms fill remaining context slots."),

        ("Q3: How do you handle offline sync in Google Calendar without duplicate events or resurrecting deleted events?",
         "<b>Answer:</b> Offline operations maintain two local stores: <code>local_calendar_events.json</code> (active events) and <code>deleted_calendar_events.json</code> (tombstones). Each event is indexed by a unique ID and a composite key: <code>(summary, start_time[:16])</code>. When coming online: (1) Tombstones are processed first against Google Calendar API to ensure offline-deleted items are removed remotely; (2) Active events are upserted matching on composite keys rather than blind insertion, guaranteeing zero duplication even across network disconnects.")
    ]

    for q, a in sovereign_qa:
        story.append(Paragraph(q, qa_q_style))
        story.append(Paragraph(a, qa_a_style))

    # ──────────────────────────────────────────────────────────────────────────
    # MODULE 3: OTHER PORTFOLIO PROJECTS
    # ──────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Module 3: Portfolio Projects In-Depth Analysis", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.75, color=COLOR_BORDER, spaceBefore=1, spaceAfter=6))

    story.append(Paragraph("3.1 MacroLens Vision AI — Nutrition & Fitness Platform", h2_style))
    story.append(Paragraph(
        "<b>Stack:</b> MERN (MongoDB, Express.js, React, Node.js), OpenRouter Vision API, JWT, bcrypt, Tailwind CSS.<br/>"
        "<b>System Architecture & Innovations:</b><br/>"
        "• <b>Serving-Aware Calculation Engine:</b> Most nutrition apps store flat calorie values per generic item (e.g. '1 bowl'). MacroLens engineered a 1,014-item Indian nutrition database where every entry defines structured serving metadata (unit type, exact gram weight, default portion). The backend computes exact macros dynamically from gram weights.<br/>"
        "• <b>Multimodal Vision Pipeline:</b> Users upload meal photos. The backend validates MIME type and file size (<5MB), passes base64 image data to an OpenRouter multimodal LLM with a strict JSON schema prompt, parses JSON output with regex markdown fence striping, and enforces runtime numeric boundary validation.<br/>"
        "• <b>MongoDB Aggregation Pipelines:</b> Compound indexing on <code>(userId, date)</code> powers high-speed aggregation pipelines computing daily rolling averages, micronutrient distribution, and caloric deficit/surplus with sub-15ms execution.",
        body_style
    ))

    story.append(Paragraph("<b>Likely Interview Question & Model Answer:</b>", h3_style))
    story.append(Paragraph("<b>Q: How did you optimize MongoDB queries for calculating daily nutrition totals across months of data?</b>", qa_q_style))
    story.append(Paragraph("<b>A:</b> Storing individual food log items as separate flat documents would require scanning thousands of rows for a monthly dashboard. I created a compound index on <code>{ userId: 1, date: -1 }</code>. In the aggregation pipeline: (1) <code>$match</code> filters by <code>userId</code> and date range using the compound index; (2) <code>$unwind</code> deconstructs logged foods; (3) <code>$group</code> aggregates daily sums for calories, protein, carbs, and fats; (4) <code>$sort</code> by date. Query latency remained under 12ms even with 10,000+ logged items.", qa_a_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("3.2 Pal-AI — Provider-Agnostic Multi-Turn Companion", h2_style))
    story.append(Paragraph(
        "<b>Stack:</b> Next.js, OpenRouter Gateway, Node.js, MongoDB, Tailwind CSS.<br/>"
        "<b>Key Innovations:</b><br/>"
        "• <b>Provider-Agnostic Routing:</b> Abstract adapter architecture allows swapping between Claude 3.5 Sonnet, GPT-4o, and DeepSeek via configuration without refactoring routes.<br/>"
        "• <b>Sliding Context Memory:</b> Monitors token count per session. When conversation exceeds 70% of model window capacity, an asynchronous background worker triggers a summarization LLM call on older turns and compresses them into a persistent memory block injected into the system prompt.",
        body_style
    ))

    # ──────────────────────────────────────────────────────────────────────────
    # MODULE 4: CORE CS FOUNDATIONS (EXHAUSTIVE)
    # ──────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Module 4: Core CS Foundations — Technical Interview Q&A", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.75, color=COLOR_BORDER, spaceBefore=1, spaceAfter=6))

    story.append(Paragraph("4.1 Operating Systems & Concurrency", h2_style))

    cs_os_deep = [
        ("Q1: Process vs Thread — Memory Layout, Context Switching, and Kernel Data Structures.",
         "<b>Answer:</b> A <b>Process</b> is an independent executing program with its own private virtual memory space (Text, Data, BSS, Heap, Stack), managed by a Process Control Block (PCB) in the kernel containing PID, page table base register (CR3 on x86), file descriptors, and CPU registers. Processes are strictly isolated. A <b>Thread</b> is the basic unit of CPU execution within a process; all threads share the process's Text, Data, Heap, and file descriptors, but maintain a private Thread Control Block (TCB) with private Stack and Program Counter (PC). Context switching threads is much faster than processes because the MMU page directory does not need to be reloaded and CPU L1/L2 caches are not invalidated."),

        ("Q2: Deep Dive into the Python GIL (Global Interpreter Lock) — How it Works and How to Bypass It.",
         "<b>Answer:</b> The GIL is a mutex in CPython that ensures only one native thread executes Python bytecode at any given moment. CPython's memory management uses reference counting, which is inherently non-thread-safe without locks; the GIL prevents race conditions on reference counts. For <b>I/O-bound workloads</b> (FastAPI, WebSockets, DB queries), Python threads release the GIL when entering C syscalls (like <code>recv</code> or <code>send</code>), allowing high concurrency via <code>asyncio</code>. For <b>CPU-bound workloads</b> (vector embeddings, data munging), true parallelism requires <code>multiprocessing</code> (spawning distinct OS processes with separate Python heaps and GILs) or offloading to C/C++/Rust extensions (like NumPy or PyTorch)."),

        ("Q3: How does Async/Await and the Event Loop work under the hood? (Epoll / Kqueue / IOCP)",
         "<b>Answer:</b> <code>asyncio</code> provides single-threaded cooperative multitasking. When an async function calls <code>await</code> on an I/O operation (e.g. network socket), it suspends and yields execution back to the Event Loop. The Event Loop registers the socket's file descriptor with the OS kernel's I/O multiplexer: <code>epoll</code> on Linux, <code>kqueue</code> on macOS/BSD, or <code>IOCP</code> on Windows. The kernel monitors readiness in hardware/driver ring buffers. When data arrives, the kernel notifies the event loop, which moves the coroutine from the waiting queue to the ready queue and resumes its execution frame.")
    ]

    for q, a in cs_os_deep:
        story.append(Paragraph(q, qa_q_style))
        story.append(Paragraph(a, qa_a_style))

    story.append(Paragraph("4.2 Computer Networks", h2_style))

    cs_net_deep = [
        ("Q4: Explain the TCP 3-Way Handshake, 4-Way Teardown, and the significance of TIME_WAIT.",
         "<b>Answer:</b><br/>"
         "• <b>Connection (3-Way):</b> (1) Client $\\rightarrow$ Server: <code>SYN</code> (seq=x); (2) Server $\\rightarrow$ Client: <code>SYN-ACK</code> (seq=y, ack=x+1); (3) Client $\\rightarrow$ Server: <code>ACK</code> (ack=y+1). State: <code>ESTABLISHED</code>.<br/>"
         "• <b>Teardown (4-Way):</b> (1) Active closer sends <code>FIN</code>; (2) Passive closer sends <code>ACK</code> (enters <code>CLOSE_WAIT</code>); (3) Passive closer sends its own <code>FIN</code>; (4) Active closer sends <code>ACK</code> and enters <code>TIME_WAIT</code>.<br/>"
         "• <b>Why TIME_WAIT is essential:</b> The active closer waits for $2 \\times \\text{MSL}$ (Maximum Segment Lifetime, typically 60s) for two reasons: (a) To allow the final ACK to reach the server in case it was lost (so the server doesn't retransmit FIN and receive a RST); (b) To let lingering duplicate packets in the network expire before the same socket address `(IP, port)` is reused by a new connection."),

        ("Q5: Compare WebSockets, Server-Sent Events (SSE), and HTTP Long-Polling with performance trade-offs.",
         "<b>Answer:</b><br/>"
         "• <b>WebSockets (RFC 6455):</b> Full-duplex bidirectional communication over a single persistent TCP connection initiated via HTTP 101 Switching Protocols. Lowest framing overhead (2-14 bytes per frame). Best for interactive chat, gaming, and bidirectional agent control.<br/>"
         "• <b>Server-Sent Events (SSE):</b> Unidirectional (Server $\\rightarrow$ Client) streaming over standard HTTP (<code>text/event-stream</code>). Built-in browser reconnection and event IDs. Ideal for LLM token streaming and stock feeds.<br/>"
         "• <b>HTTP Long-Polling:</b> Client opens HTTP request; server hangs open until data is available, then closes. Requires repeated TCP/TLS handshakes and full HTTP header re-transmission. High latency and overhead; legacy fallback.")
    ]

    for q, a in cs_net_deep:
        story.append(Paragraph(q, qa_q_style))
        story.append(Paragraph(a, qa_a_style))

    story.append(Paragraph("4.3 Database Management Systems & Indexing", h2_style))

    cs_db_deep = [
        ("Q6: Compare B+ Tree Indexing in Relational Databases with Vector HNSW Indexing in Qdrant.",
         "<b>Answer:</b><br/>"
         "• <b>B+ Tree Index:</b> Self-balancing N-ary tree where all data records/pointers reside strictly in leaf nodes linked by a doubly-linked list. Non-leaf nodes only store search keys. Provides $O(\\log N)$ lookup, insertion, deletion, and optimal sequential cache locality for range queries (<code>BETWEEN a AND b</code>).<br/>"
         "• <b>HNSW (Hierarchical Navigable Small World):</b> Multi-layer proximity graph index for high-dimensional vectors (e.g. 384 or 1536 dims). Higher layers contain sparse long-range highway links (like skip-lists); bottom layer contains dense local nearest neighbors. Provides $O(\\log N)$ approximate nearest neighbor (ANN) search via Greedy Routing, scaling efficiently to millions of embeddings."),

        ("Q7: Explain ACID Properties, Transaction Isolation Levels, and Common Concurrency Anomalies.",
         "<b>Answer:</b><br/>"
         "• <b>ACID:</b> Atomicity (All-or-nothing via WAL), Consistency (State constraints preserved), Isolation (Concurrent transactions don't cross-contaminate), Durability (Committed data survives crashes).<br/>"
         "• <b>Isolation Levels & Anomalies:</b><br/>"
         "  - <i>Read Uncommitted:</i> Vulnerable to Dirty Reads (reading uncommitted data that later rolls back).<br/>"
         "  - <i>Read Committed:</i> Prevents Dirty Reads, but vulnerable to Non-Repeatable Reads (row values change between reads).<br/>"
         "  - <i>Repeatable Read:</i> Uses MVCC snapshots; prevents Non-Repeatable Reads, but may suffer Phantom Reads (new rows inserted).<br/>"
         "  - <i>Serializable:</i> Highest level; executed via Two-Phase Locking (2PL) or Serializable Snapshot Isolation (SSI). Complete anomaly prevention.")
    ]

    for q, a in cs_db_deep:
        story.append(Paragraph(q, qa_q_style))
        story.append(Paragraph(a, qa_a_style))

    # ──────────────────────────────────────────────────────────────────────────
    # MODULE 5: MODERN AI & LLM SYSTEMS ENGINEERING
    # ──────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Module 5: Modern AI & LLM Systems Engineering", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.75, color=COLOR_BORDER, spaceBefore=1, spaceAfter=6))

    ai_deep = [
        ("Q1: Explain the Mathematical Mechanics of Transformer Scaled Dot-Product Self-Attention.",
         "<b>Answer:</b> Input token embeddings $X$ are multiplied by learned weight matrices $W_Q, W_K, W_V$ to generate Query ($Q$), Key ($K$), and Value ($V$) matrices. The attention formula is: "
         "$$\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{Q K^T}{\\sqrt{d_k}}\\right) V$$"
         "• $Q K^T$ calculates similarity dot-products between all token pairs in the sequence (sequence length $N \\times N$).<br/>"
         "• Division by $\\sqrt{d_k}$ (where $d_k$ is key dimension) prevents dot products from growing excessively large, which would push the softmax into regions with near-zero gradients.<br/>"
         "• Softmax normalizes scores into an attention weight distribution summing to 1 across rows.<br/>"
         "• Multiplying by $V$ produces a context-aware weighted sum of value vectors for each token position."),

        ("Q2: What is the KV Cache in LLM Inference and why is generation memory-bandwidth bound?",
         "<b>Answer:</b> In autoregressive generation, generating each new token requires attending to all prior tokens in the sequence. Without caching, the model would recompute Keys and Values for all past tokens at every step ($O(N^2)$ redundant compute). The <b>KV Cache</b> stores computed Key and Value tensors in GPU VRAM across generation steps, so only the single new token's Query needs to be projected. Because modern GPUs have massive compute capability but limited memory bandwidth, transferring large KV caches between HBM and SRAM makes token generation memory-bandwidth bound rather than compute bound."),

        ("Q3: How do you evaluate a RAG Pipeline in Production? (The RAG Triad / RAGAS Framework)",
         "<b>Answer:</b><br/>"
         "1. <b>Context Precision / Relevance:</b> Measures whether retrieved text chunks are concise and directly relevant to the user query without irrelevant noise.<br/>"
         "2. <b>Faithfulness / Groundedness:</b> Measures whether every factual claim in the LLM's answer can be verified directly against the retrieved context (detects hallucinations).<br/>"
         "3. <b>Answer Relevance:</b> Measures whether the generated output directly addresses the user's question and intent regardless of whether context was provided.")
    ]

    for q, a in ai_deep:
        story.append(Paragraph(q, qa_q_style))
        story.append(Paragraph(a, qa_a_style))

    # ──────────────────────────────────────────────────────────────────────────
    # MODULE 6: INTERVIEW DAY QUICK REFERENCE CHEAT-SHEET
    # ──────────────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 8))
    story.append(Paragraph("Module 6: Interview Day Quick Reference & Latency Cheat-Sheet", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.75, color=COLOR_BORDER, spaceBefore=1, spaceAfter=6))

    cheat_data = [
        [
            Paragraph("<b>Operation / Resource</b>", body_bold),
            Paragraph("<b>Approximate Latency</b>", body_bold),
            Paragraph("<b>Scale Comparison & Takeaway</b>", body_bold)
        ],
        [
            Paragraph("<b>L1 CPU Cache Reference</b>", body_style),
            Paragraph("~ 1 ns", body_style),
            Paragraph("Fastest hardware memory lookup.", body_style)
        ],
        [
            Paragraph("<b>Main Memory (RAM) Access</b>", body_style),
            Paragraph("~ 100 ns", body_style),
            Paragraph("100x slower than L1 cache.", body_style)
        ],
        [
            Paragraph("<b>NVMe SSD Random Read</b>", body_style),
            Paragraph("~ 10–50 μs", body_style),
            Paragraph("100x to 500x slower than RAM.", body_style)
        ],
        [
            Paragraph("<b>Network Roundtrip (Same Datacenter)</b>", body_style),
            Paragraph("~ 0.5 ms", body_style),
            Paragraph("10x slower than SSD.", body_style)
        ],
        [
            Paragraph("<b>Cross-Continental Network (NYC - London)</b>", body_style),
            Paragraph("~ 70–100 ms", body_style),
            Paragraph("Speed of light in fiber constraint.", body_style)
        ]
    ]
    cheat_table = Table(cheat_data, colWidths=[160, 120, 256])
    cheat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [COLOR_BG_LIGHT, COLOR_CARD_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(cheat_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated PDF at: {pdf_path}")

if __name__ == "__main__":
    output_pdf = os.path.abspath("Yashpreet_Master_Interview_Preparation_Guide.pdf")
    build_pdf(output_pdf)
