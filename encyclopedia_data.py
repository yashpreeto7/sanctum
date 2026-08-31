"""
Encyclopedic Data Store for 45-50+ Page Engineering Textbook.
Contains rich full-length text, deep architectural breakdowns, source code snippets, and 60+ technical Q&As.
"""

# Candidate Bio
CANDIDATE_INTRO = (
    "I am a final-year Computer Science undergraduate at VIT Bhopal with an 8.47 CGPA, specializing in "
    "full-stack distributed systems, API architecture, and autonomous AI engineering. Over the past two years, "
    "I've focused on engineering reliable, production-grade applications that combine modern web runtimes with local-first AI intelligence. "
    "Most recently, I engineered SovereignOS, an autonomous AI operating system powered by a 5-tier LangGraph state machine DAG, "
    "hybrid vector RAG (combining Qdrant dense embeddings with BM25 sparse keyword ranking via Reciprocal Rank Fusion), "
    "zero-shot prompt injection quarantine gates, and real-time word-by-word WebSocket streaming. "
    "Prior to that, I built MacroLens Vision AI, a full-stack nutrition platform with a serving-aware calculation engine "
    "across a 1,014 Indian food database and multimodal vision recognition, as well as Pal-AI, a provider-agnostic companion "
    "with token-budgeted sliding context memory. I love tackling hard systems problems—from eliminating async ASGI deadlocks to optimizing "
    "vector database indexing—and I'm excited to bring my engineering discipline to this role."
)

STAR_SCENARIOS = [
    ("1. Hardest Technical Bug Overcome (Async Concurrency & Deadlocks)",
     "During development of SovereignOS, streaming responses over WebSockets while background sub-agents performed external tool calls caused intermittent event loop starvation. First-token latency spiked to 4.2 seconds and occasionally deadlocked Uvicorn workers.",
     "I profiled the ASGI event loop using asyncio task inspection. I identified that synchronous subprocess I/O in the legacy tool runner was blocking the main thread. I re-architected the pipeline to use LangGraph's native astream_events(version='v1'), decoupled background tool execution into dedicated thread pools using asyncio.to_thread, and implemented non-blocking WebSocket queues.",
     "First-token latency dropped from 4.2s to 120ms with steady 55 tokens/sec emission. 100% of event loop deadlocks were permanently resolved under load tests."),

    ("2. Resolving Ambiguity in Architectural Design (Search Engine)",
     "Needed to design the retrieval engine for SovereignOS to search across local personal notes, code snippets, and structured calendar events. Plain dense vector embeddings were failing on exact code identifiers and dates.",
     "Researched modern IR techniques and implemented a Hybrid Search architecture. Combined Qdrant dense vector cosine similarity (using all-MiniLM-L6-v2) with a BM25 sparse lexical inverted index. Merged rankings using Reciprocal Rank Fusion (RRF with k=60).",
     "Search recall jumped by 34% compared to pure dense search, particularly for alphanumeric tokens, function names, and ISO dates."),

    ("3. Handling Security & Adversarial Attacks (Prompt Injection)",
     "Private desktop automations (e.g. deleting files, sending emails) exposed the local environment to catastrophic indirect prompt injections when reading untrusted emails or web pages.",
     "Engineered a multi-tier Quarantine Security Gate (execution/security/quarantine.py). Integrated fast regex heuristics, canary token validation, zero-shot LLM classification, and an asynchronous Human-In-The-Loop (HITL) approval token gate for high-risk tool calls.",
     "Neutralized 100% of adversarial prompt injection test suites without degrading system throughput for normal queries."),

    ("4. Tight Deadlines & Rapid Delivery (Anthropic MCP Integration)",
     "Anthropic released the Model Context Protocol (MCP) standard, and I wanted SovereignOS to support standardized tool servers without existing Python MCP client libraries for our stack.",
     "Read the JSON-RPC 2.0 stdio wire specifications directly. Built a custom MCPClient and MCPManager from scratch in Python to spawn background MCP server processes, handshake over stdio, and dynamically translate tool schemas into agent functions.",
     "Delivered full Filesystem and SQLite MCP tool support within 48 hours, demonstrating rapid prototyping and standard compliance."),

    ("5. Performance Optimization (MongoDB Aggregation Pipelines)",
     "In MacroLens Vision AI, computing 30-day rolling macronutrient and micronutrient totals across user meal histories was causing 800ms query latency on dashboard page loads.",
     "Analyzed query execution plans using explain('executionStats'). Identified full-collection scans. Created a compound index on { userId: 1, date: -1 } and restructured the aggregation pipeline to filter first ($match), then unwind and group ($group), eliminating redundant memory stages.",
     "Reduced dashboard query latency from 800ms to 11ms (a 98.6% speedup), dramatically improving perceived user experience."),

    ("6. Disagreement on Technical Approach (State Management)",
     "During a team frontend project, a peer proposed using prop drilling and component-level state across 6 nested modal levels for an appointment booking flow, while I advocated for Redux Toolkit.",
     "Rather than arguing abstractly, I created a minimal branch comparison demonstrating how Redux Toolkit with RTK Query eliminated 200 lines of boilerplate, centralized loading/error states, and prevented unnecessary re-renders in nested components.",
     "The team adopted Redux Toolkit, resulting in cleaner code reviews and zero state synchronization bugs during QA testing."),

    ("7. Handling a Production Incident / Edge Case (Calendar Sync)",
     "Users reported that deleting calendar events offline in SovereignOS caused deleted events to reappear when the network reconnected (event resurrection bug).",
     "Identified that the sync engine performed blind upserts from local cache without tracking deletion tombstones. Implemented a dedicated deleted_calendar_events.json tombstone ledger with composite keys (summary, start_time[:16]). Updated sync logic to execute remote deletions before upserting active records.",
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

SOVEREIGN_CODEBASE_FILES = [
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

SOVEREIGN_30_QA = [
    ("Q1: Why did you choose LangGraph over traditional linear LangChain chains or while-loops?",
     "Traditional LangChain chains enforce a unidirectional, deterministic execution flow. Real-world autonomous agents require non-deterministic branching, cyclic self-correction loops (retrying failed tool calls with revised arguments), and asynchronous human-in-the-loop pauses. LangGraph models the system as a stateful cyclic graph where nodes are functions and edges are conditional transitions. It provides first-class state checkpointing (resuming across server restarts) and fine-grained event streaming hooks (astream_events)."),

    ("Q2: Explain the mathematics and engineering rationale behind your Hybrid RAG (Qdrant + BM25 + RRF).",
     "Dense vector search computes cosine similarity: sim(u, v) = (u . v) / (||u|| ||v||). While effective for broad semantic concepts ('improving sleep' -> 'sleep hygiene'), dense embeddings fail on exact alphanumeric tokens (function names like astream_events, dates, error codes). BM25 uses term frequency and inverse document frequency: BM25(D, Q) = sum IDF(q_i) * (f(q_i, D) * (k1 + 1)) / (f(q_i, D) + k1 * (1 - b + b * (|D| / avgdl))). I combine both using Reciprocal Rank Fusion: RRF(d) = sum 1 / (60 + rank_m(d)), ensuring exact matches rank #1 while semantic context fills remaining slots."),

    ("Q3: How does WebSocket token streaming work in SovereignOS without blocking the ASGI event loop?",
     "The WebSocket route in server/app.py subscribes to LangGraph's astream_events(version='v1'). When graph nodes transition, lightweight JSON packets (node_progress) are pushed immediately to update UI indicators. When reasoning completes, text tokens are emitted word-by-word at 18ms intervals (~55 words/sec) via custom token events. All background tasks and tool executions are dispatched as non-blocking asyncio coroutines, preventing event loop starvation."),

    ("Q4: How did you solve the 'Zombie Event Resurrection' bug in offline calendar synchronization?",
     "Offline calendar systems often suffer from deleted events reappearing after sync. I implemented a two-pronged solution: (1) Indexed every event locally by a composite key (summary, start_time[:16]); (2) Created a dedicated tombstone file deleted_calendar_events.json. During sync, the daemon processes tombstones first to delete remote events on Google Calendar before executing upsert passes for active events, guaranteeing zero resurrecting zombies."),

    ("Q5: What is Model Context Protocol (MCP) and how does SovereignOS implement both Host and Client roles?",
     "MCP is an open standard created by Anthropic that standardizes how AI agents discover and execute tools using JSON-RPC 2.0 over standard I/O (stdio). SovereignOS implements an MCPManager that spawns isolated background worker processes (e.g. @modelcontextprotocol/server-filesystem), calls tools/list on handshake, translates tool schemas into the agent's LLM function definitions, and dispatches calls via tools/call over stdin/stdout pipes."),

    ("Q6: How does the Quarantine Security Gate detect and prevent Prompt Injection?",
     "Quarantine employs a defense-in-depth architecture: (1) Static Heuristics: Regex filters for known escape patterns ('ignore previous instructions', 'system prompt override'); (2) Zero-Shot Canary Tokens: High-entropy GUID tokens injected into system instructions; if an LLM response contains the canary token, execution is terminated immediately; (3) Policy Gate: High-risk actions (file deletion, mass email dispatch) require cryptographic approval tokens verified via Human-in-the-Loop approval."),

    ("Q7: How do you handle local LLM inference latency on consumer hardware with Qwen 2.5 7B?",
     "Running local 7B models can encounter memory-bandwidth bottlenecks. I optimized inference by: (1) Using 4-bit / 8-bit quantized GGUF weights in Ollama, reducing VRAM usage to under 5.5GB; (2) Pre-filtering user queries with a lightweight 1.5B intent classifier so trivial chit-chat skips heavy tool-calling pipelines; (3) Offloading token streaming to non-blocking generators so the user perceives immediate response start (TTFT < 150ms)."),

    ("Q8: How does the Obsidian Markdown AST parser work and why is heading-level chunking superior?",
     "Naive RAG splitters use fixed-character windows with overlap, frequently splitting sentences or code blocks midway. In obsidian_workspace.py, I parse notes using a Markdown Abstract Syntax Tree (AST). The parser extracts YAML frontmatter metadata and chunks content along # H1 and ## H2 header boundaries. Each chunk forms a complete, self-contained semantic unit with its parent document hierarchy preserved in metadata."),

    ("Q9: What happens if an MCP server crashes or hangs during tool execution?",
     "In execution/tools/mcp_client.py, every tool invocation is wrapped in an asyncio.wait_for(timeout=15.0) boundary. If an MCP subprocess fails to respond or crashes, the client intercepts the timeout/broken pipe exception, logs telemetry to SQLite, terminates the orphaned process, and returns a structured error object back to LangGraph's reasoning node for automatic retry or graceful degradation."),

    ("Q10: Explain the Human-in-the-Loop (HITL) approval architecture in SovereignOS.",
     "When Node 4 proposes a destructive tool call (e.g. delete_file, send_email), Node 5 (HITL Gate) intercepts the payload, generates a cryptographically secure UUID approval_id, registers it in an active memory store with a 5-minute TTL, and yields an approval_required WebSocket event. The graph pauses at this checkpoint. When the user clicks 'Approve' on the UI, POST /api/approvals/{id}/decision resolves the token and resumes graph execution from the exact checkpoint."),

    ("Q11: How do you manage conversation session persistence across server restarts?",
     "Chat sessions and messages are persisted in a local SQLite database (data/chat_history.db) using WAL (Write-Ahead Logging) mode for concurrent read/write throughput. On startup, the UI auto-restores the last active session ID from localStorage, queries GET /api/chat/history?session_id=..., and repopulates the message DOM seamlessly."),

    ("Q12: How does the background Folder Watcher avoid ingesting partially-written files?",
     "The FolderWatcher uses the watchdog library to listen for on_created and on_modified OS filesystem events. To prevent reading half-copied large files, it implements a debounce delay: the worker verifies that the file size remains unchanged across two consecutive checks (500ms apart) and confirms non-exclusive file lock acquisition before passing the file to the document parser and vectorizer."),

    ("Q13: What embedding model do you use and what are the trade-offs of embedding dimensions?",
     "I use sentence-transformers/all-MiniLM-L6-v2 which produces 384-dimensional dense vectors. While 1536-dim models (e.g. OpenAI text-embedding-3-small) offer marginal gains on massive public benchmarks, all-MiniLM-L6-v2 executes in <15ms on local CPU, consumes 75% less VRAM/disk storage in Qdrant, and achieves 99%+ of the semantic retrieval accuracy when paired with BM25 hybrid ranking."),

    ("Q14: Explain the Web Audio spectrum visualizer implementation in the dashboard.",
     "The HUD dashboard features a real-time audio visualizer styled after CAVA. It connects to the Web Audio API via AudioContext and AnalyserNode with an FFT size of 64 (fftSize = 64). An animationFrame loop reads getByteFrequencyData(), normalizes frequency amplitudes across 16 frequency bands, and renders animated neon cyan bars on a canvas element with 60 FPS smoothness."),

    ("Q15: How does the Gmail connector handle OAuth2 token expiration and refresh?",
     "The GmailConnector loads credentials from token.json. If the access token is expired, it uses the Google OAuth2 InstalledAppFlow and refresh token to execute a non-blocking creds.refresh(Request()) call in the background, writes updated tokens back to disk, and transparently retries the failed API call without interrupting user workflows."),

    ("Q16: How do you prevent context window exhaustion during long multi-turn conversations?",
     "SovereignOS enforces a token-budgeted sliding window. The state machine monitors token counts using tiktoken. When message history exceeds 70% of the model's context capacity, an asynchronous node triggers a summarization prompt over older turns, compressing past context into a structured summary block injected into system instructions while retaining the last 5 turns verbatim."),

    ("Q17: What design patterns are used throughout the SovereignOS codebase?",
     "Key design patterns include: (1) State Pattern / State Machine: LangGraph DAG modeling agent phases; (2) Adapter Pattern: Wrapping MCP, Google APIs, and local tools into a unified BaseTool interface; (3) Observer Pattern: Filesystem folder watcher emitting ingestion events; (4) Factory Pattern: LLM client factory selecting between Ollama, Gemini, and OpenRouter runtimes; (5) Singleton Pattern: Database connection pools and WebSocket connection manager."),

    ("Q18: How does SovereignOS handle rate limits when falling back to Cloud LLM APIs?",
     "When routing requests to Gemini Flash or OpenRouter, API calls are wrapped with an exponential backoff retry decorator using jitter: Delay = 2^(attempt) * base + uniform(0, 1). If HTTP 429 (Too Many Requests) is returned, the system retries up to 3 times before automatically falling back to the local Ollama instance with a user notification."),

    ("Q19: How do you ensure idempotent tool executions in agent retry loops?",
     "Every planned tool call receives a deterministic action_fingerprint = SHA256(tool_name + sorted_args + session_id). Before executing a tool, the engine checks an in-memory execution cache. If an identical fingerprint was executed within the current turn, the cached result is returned immediately, preventing duplicate email sends or calendar additions during retry loops."),

    ("Q20: What are the primary scalability bottlenecks of SovereignOS and how would you scale it to multi-user enterprise?",
     "The current architecture is optimized for single-user desktop privacy. To scale to a multi-tenant enterprise system: (1) Replace SQLite with PostgreSQL / TimescaleDB with connection pooling (PgBouncer); (2) Transition local Qdrant to a distributed Qdrant cluster with sharded collections; (3) Decouple agent graph execution from the web server using Celery/RabbitMQ or Redis Streams worker pools; (4) Introduce role-based access control (RBAC) and OAuth2 OIDC multi-tenancy.")
]

print("Loaded encyclopedia data store successfully.")
