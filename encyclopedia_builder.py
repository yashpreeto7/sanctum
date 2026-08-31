"""
Full 45-50+ Page Engineering Master Textbook & Technical Interview Guide Builder.
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
from encyclopedia_data import CANDIDATE_INTRO, STAR_SCENARIOS, SOVEREIGN_CODEBASE_FILES, SOVEREIGN_30_QA

def generate_full_encyclopedia():
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
    # TITLE & HEADER
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

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 1: CANDIDATE POSITIONING & BEHAVIORAL PLAYBOOK
    # ══════════════════════════════════════════════════════════════════════════
    story.extend(create_section_header("Chapter 1: Candidate Positioning, Narrative & Behavioral STAR Playbook", "Comprehensive communication strategy and high-impact scenario breakdowns", styles))
    add_md("## Chapter 1: Candidate Positioning, Narrative & Behavioral STAR Playbook\n\n")

    story.append(Paragraph("1.1 The 90-Second High-Impact Self-Introduction", styles['h2']))
    story.append(Paragraph(f"<i>\"{CANDIDATE_INTRO}\"</i>", styles['callout']))
    story.append(Spacer(1, 8))
    add_md(f"### 1.1 The 90-Second High-Impact Self-Introduction\n\n> {CANDIDATE_INTRO}\n\n")

    story.append(Paragraph("1.2 The Complete 10-Scenario Behavioral STAR Playbook", styles['h2']))
    add_md("### 1.2 The Complete 10-Scenario Behavioral STAR Playbook\n\n")

    for title, s_t, a, r in STAR_SCENARIOS:
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
    # CHAPTER 2: SOVEREIGN OS ARCHITECTURAL MANUAL
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 2: SovereignOS — Flagship Engineering Reference Manual", "Exhaustive file-by-file codebase walkthrough, state graph DAG, and 20 deep interview Q&As", styles))
    add_md("## Chapter 2: SovereignOS — Flagship Engineering Reference Manual\n\n")

    for title, desc in SOVEREIGN_CODEBASE_FILES:
        story.append(Paragraph(f"<b>{title}</b>", styles['h3']))
        story.append(Paragraph(desc, styles['body']))
        story.append(Spacer(1, 4))
        add_md(f"#### {title}\n{desc.replace('<b>', '**').replace('</b>', '**').replace('<br/>', '\n')}\n\n")

    story.append(Paragraph("2.3 Top 20 Technical Interview Q&As on SovereignOS", styles['h2']))
    add_md("### 2.3 Top 20 Technical Interview Q&As on SovereignOS\n\n")

    for q, a in SOVEREIGN_30_QA:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 3: PORTFOLIO PROJECTS DEEP DIVE
    # ══════════════════════════════════════════════════════════════════════════
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

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 4: OPERATING SYSTEMS & LOW-LEVEL CONCURRENCY
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 4: Operating Systems & Low-Level Concurrency Masterclass", "Processes, Threads, Linux Kernel Internals, Virtual Memory, Memory Models, and Synchronization", styles))
    add_md("## Chapter 4: Operating Systems & Low-Level Concurrency Masterclass\n\n")

    os_qas = [
        ("Q1: Process vs Thread — Memory Layout, Context Switching, and Kernel Data Structures.",
         "A <b>Process</b> is an independent executing program with its own private virtual memory space (Text, Data, BSS, Heap, Stack), managed by a Process Control Block (PCB) in the kernel containing PID, page table base register (CR3 on x86), file descriptors, and CPU registers. Processes are strictly isolated.<br/>"
         "A <b>Thread</b> is the basic unit of CPU execution within a process; all threads share the process's Text, Data, Heap, and file descriptors, but maintain a private Thread Control Block (TCB) with private Stack and Program Counter (PC).<br/>"
         "<b>Context Switching:</b> Thread context switching is substantially faster than process switching because the CPU does not need to reload virtual memory page directory registers (CR3 on x86), preventing expensive TLB invalidation and cache thrashing."),

        ("Q2: Explain the Python Global Interpreter Lock (GIL) — Mechanics, Rationale, and Workarounds.",
         "The GIL is a mutual exclusion lock used by CPython to ensure only one native OS thread executes Python bytecode at a time. It was designed because CPython's memory management relies on reference counting, which is inherently non-thread-safe without locks.<br/>"
         "• <b>I/O-Bound Workloads:</b> When a Python thread performs an I/O syscall (network read/write, disk access), it releases the GIL. Other threads or `asyncio` coroutines can execute, making `asyncio` and `threading` highly efficient for I/O.<br/>"
         "• <b>CPU-Bound Workloads:</b> For compute-heavy tasks (vector calculations, data transformation), multi-threading suffers from lock contention. True parallelism requires <b>Multiprocessing</b> (spawning separate OS processes with independent Python runtimes and GILs) or offloading compute to native C/Rust extensions (like NumPy, PyTorch)."),

        ("Q3: How Async/Await and the Event Loop work under the hood (Epoll, Kqueue, IOCP).",
         "<code>asyncio</code> implements <b>single-threaded cooperative multitasking</b> using generators and coroutines. When an async function reaches an `await` on an uncompleted future, it yields execution back to the Event Loop. The Event Loop registers the socket's file descriptor with OS kernel multiplexing primitives: <code>epoll</code> on Linux, <code>kqueue</code> on macOS/BSD, or <code>IOCP</code> on Windows.<br/>"
         "The OS kernel uses hardware interrupts and network driver ring buffers to detect socket readiness. When data arrives, the kernel notifies the event loop, which moves the suspended coroutine from the waiting queue to the ready queue and resumes execution from its saved stack frame."),

        ("Q4: The 4 Coffman Conditions for Deadlock and how to eliminate them.",
         "A deadlock occurs if and only if all four Coffman conditions hold simultaneously: (1) Mutual Exclusion; (2) Hold and Wait; (3) No Preemption; (4) Circular Wait.<br/>"
         "<b>Elimination:</b> Prevent circular wait by enforcing a strict global resource ordering rule (processes must acquire locks in ascending numerical order of resource ID)."),

        ("Q5: Virtual Memory, Paging, Page Faults, and the Translation Lookaside Buffer (TLB).",
         "Virtual memory maps a process's virtual address space to physical RAM using fixed-size blocks called <b>Pages</b> (typically 4KB). The Memory Management Unit (MMU) translates virtual addresses to physical frames using hierarchical Page Tables.<br/>"
         "The <b>TLB (Translation Lookaside Buffer)</b> is a high-speed hardware cache on the CPU that stores recent virtual-to-physical address translations. If a translation is in TLB (TLB Hit), translation takes ~1 cycle. If not (TLB Miss), the MMU walks the multi-level page table in RAM (~10-50ns).<br/>"
         "A <b>Page Fault</b> occurs when a process accesses a page marked invalid in the page table. The CPU triggers an interrupt (trap to kernel), the OS allocates a physical frame, reads the page from disk, updates the page table, and resumes instruction execution.")
    ]

    for q, a in os_qas:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 5: COMPUTER NETWORKS & DISTRIBUTED TRANSPORT
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 5: Computer Networks & Distributed Web Transport Masterclass", "OSI 7 Layers, TCP Congestion Control, TLS 1.3 Cryptography, HTTP/2 & HTTP/3 QUIC", styles))
    add_md("## Chapter 5: Computer Networks & Distributed Web Transport Masterclass\n\n")

    net_qas = [
        ("Q1: Complete Comparison: OSI 7-Layer Model vs TCP/IP 4-Layer Architecture.",
         "• <b>Layer 7 (Application):</b> HTTP, HTTPS, WebSocket, DNS, SMTP, SSH. User interaction and protocol payload formatting.<br/>"
         "• <b>Layer 6 (Presentation):</b> TLS encryption, gzip/brotli compression, ASCII/UTF-8 character encoding.<br/>"
         "• <b>Layer 5 (Session):</b> RPC session establishment, WebSockets session maintenance, token authorization.<br/>"
         "• <b>Layer 4 (Transport):</b> TCP (reliable, ordered, connection-oriented) and UDP (unreliable, datagram, connectionless). Adds Port numbers, TCP sequence numbers, checksums.<br/>"
         "• <b>Layer 3 (Network):</b> IP (IPv4 / IPv6), ICMP, BGP, OSPF. Logical addressing and router path determination (Packets).<br/>"
         "• <b>Layer 2 (Data Link):</b> Ethernet, Wi-Fi (802.11), MAC addressing, frame error checking with CRC (Frames).<br/>"
         "• <b>Layer 1 (Physical):</b> Voltage levels, fiber optic light pulses, radio frequency waves (Bits)."),

        ("Q2: TCP 3-Way Handshake, 4-Way Teardown, and TIME_WAIT State.",
         "• <b>3-Way Handshake:</b> (1) Client $\\rightarrow$ Server: `SYN` (seq=x); (2) Server $\\rightarrow$ Client: `SYN-ACK` (seq=y, ack=x+1); (3) Client $\\rightarrow$ Server: `ACK` (ack=y+1). State becomes `ESTABLISHED`. Synchronizes sequence numbers and establishes window sizes.<br/>"
         "• <b>4-Way Teardown:</b> (1) Active closer sends `FIN`; (2) Passive closer sends `ACK` (enters `CLOSE_WAIT`); (3) Passive closer finishes sending pending data and sends `FIN`; (4) Active closer sends `ACK` and enters `TIME_WAIT`.<br/>"
         "• <b>Why TIME_WAIT (2*MSL) is critical:</b> (a) Ensures the final ACK is received by the server; (b) Allows lingering duplicate packets in the network to expire before the `(IP, port)` tuple is reused."),

        ("Q3: HTTP/1.1 vs HTTP/2 vs HTTP/3 (QUIC) In-Depth Comparison.",
         "• <b>HTTP/1.1 (1997):</b> Plaintext ASCII protocol. Persistent TCP connections (`Keep-Alive`), but suffers from Head-of-Line (HoL) Blocking at the application layer.<br/>"
         "• <b>HTTP/2 (2015):</b> Binary framing protocol over single TCP connection. Multiplexing multiple bidirectional streams. Header compression using HPACK.<br/>"
         "• <b>HTTP/3 (2022, QUIC):</b> Operates over <b>UDP</b>. True independent streams without TCP Head-of-Line blocking. 0-RTT Connection Establishment and seamless connection migration across network handoffs."),

        ("Q4: The Complete HTTPS / TLS 1.3 Handshake and Asymmetric Cryptography.",
         "TLS 1.3 reduces handshake latency to 1-RTT:<br/>"
         "1. <b>ClientHello:</b> Client sends supported cipher suites + client random + Diffie-Hellman Key Share.<br/>"
         "2. <b>ServerHello:</b> Server chooses cipher suite + sends server random + server Diffie-Hellman Key Share + encrypted certificate chain.<br/>"
         "3. <b>Shared Secret Derivation:</b> Both compute pre-master secret using **ECDHE (Elliptic Curve Diffie-Hellman Ephemeral)**, generating symmetric session keys (`AES-256-GCM`). All subsequent payload is encrypted with zero further handshake overhead.")
    ]

    for q, a in net_qas:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 6: DATABASE MANAGEMENT SYSTEMS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 6: Database Management Systems & Indexing Masterclass", "B+ Trees vs HNSW Vectors, ACID Transactions, MVCC, Isolation Levels & Sharding", styles))
    add_md("## Chapter 6: Database Management Systems & Indexing Masterclass\n\n")

    db_qas = [
        ("Q1: B+ Tree Indexing Deep Dive — Inner Nodes, Leaf Nodes, Fan-Out, and Range Scans.",
         "A <b>B+ Tree</b> is a self-balancing $N$-ary search tree optimized for block-storage systems (PostgreSQL, MySQL InnoDB, SQLite).<br/>"
         "• <b>Structural Properties:</b> Non-leaf nodes store only search keys and child page pointers (high fan-out, typically 100–500 keys per 16KB page, keeping tree height $\\le 3-4$ for millions of records). All actual data rows/pointers reside exclusively in Leaf Nodes.<br/>"
         "• <b>Doubly-Linked Leaf Nodes:</b> All leaf nodes are linked horizontally by a doubly-linked list. For range queries (`SELECT * WHERE age BETWEEN 20 AND 30`), the engine traverses $O(\\log N)$ to find the starting leaf node, then performs sequential memory reads along the leaf chain with optimal disk prefetching."),

        ("Q2: Vector Indexing: HNSW (Hierarchical Navigable Small World) Graph Architecture.",
         "Used in modern vector databases (Qdrant, Milvus, pgvector) for Approximate Nearest Neighbor (ANN) search over embeddings (e.g. 384/1536 dims).<br/>"
         "• <b>Multi-Layer Graph Hierarchy:</b> Inspired by Skip Lists. Layer 0 (bottom) contains all vector nodes with dense local neighbor connections. Upper layers contain exponentially fewer vectors with long-range 'highway' connections.<br/>"
         "• <b>Greedy Search Routing:</b> Search begins at the top layer. Evaluates distance (Cosine or Euclidean) to neighbors, hops to the closest neighbor, and drops down to the next layer until reaching Layer 0. Achieves $O(\\log N)$ search complexity."),

        ("Q3: Multi-Version Concurrency Control (MVCC) and How PostgreSQL / MySQL Avoid Read Locks.",
         "Traditional 2PL (Two-Phase Locking) blocks readers when a writer is active. MVCC allows <b>'Readers never block writers, and writers never block readers'</b>.<br/>"
         "• <b>Mechanics:</b> When a transaction updates a row, it does not overwrite the existing disk record. Instead, it creates a new version of the row with metadata columns: `xmin` (creating transaction ID) and `xmax` (deleting/updating transaction ID).<br/>"
         "• <b>Read Visibility Snapshot:</b> When Transaction $T$ starts with ID 105, it takes a snapshot of active transaction IDs. It only reads row versions where `xmin < 105` and `xmax` is either unset or $>105$.")
    ]

    for q, a in db_qas:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 7: SYSTEM DESIGN & ARCHITECTURE
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 7: System Design & Enterprise Architecture Masterclass", "CAP Theorem, Caching, Rate Limiting, Consistent Hashing, Saga & Microservice Patterns", styles))
    add_md("## Chapter 7: System Design & Enterprise Architecture Masterclass\n\n")

    sys_qas = [
        ("Q1: Consistent Hashing with Virtual Nodes — Architecture and Mathematical Proof.",
         "• <b>Problem:</b> In standard mod hashing ($\\text{Server} = \\text{Hash}(K) \\pmod N$), adding or removing a server changes $N$, causing nearly 100% of keys to remap, resulting in massive cache misses.<br/>"
         "• <b>Consistent Hashing Mechanism:</b> Maps both server IDs and data keys onto a circular hash ring ($0 \\text{ to } 2^{32}-1$). A key is assigned to the first server whose position is $\\ge \\text{key position}$ moving clockwise. When a server is added or removed, only $K/N$ keys need remapping on average.<br/>"
         "• <b>Virtual Nodes:</b> Maps each physical server to $V$ virtual nodes (e.g. $V=256$) distributed randomly across the ring. This balances load evenly and ensures proportional hand-off when nodes fail."),

        ("Q2: Rate Limiting Algorithms: Token Bucket, Leaky Bucket, Sliding Window Counter.",
         "• <b>Token Bucket:</b> Tokens added at rate $r$ up to capacity $b$. Request consumes 1 token. Allows bursts up to capacity $b$. Memory efficient ($O(1)$ space). Standard for API gateways (AWS, Stripe).<br/>"
         "• <b>Leaky Bucket:</b> Requests enter FIFO queue, leak out at constant rate. Smooths bursts into uniform flow. Drops requests on queue overflow.<br/>"
         "• <b>Sliding Window Counter:</b> Combines previous window count and current window count weighted by elapsed time: $\\text{Count} = \\text{prev} \\times (1 - t) + \\text{curr}$. Eliminates boundary burst spikes with $O(1)$ memory.")
    ]

    for q, a in sys_qas:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 8: MODERN AI & LLM SYSTEMS ENGINEERING
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 8: Modern AI & LLM Systems Engineering Masterclass", "Transformer Attention Mathematics, KV Caching, Quantization, RAGAS & Agent Protocols", styles))
    add_md("## Chapter 8: Modern AI & LLM Systems Engineering Masterclass\n\n")

    ai_qas = [
        ("Q1: Complete Mathematical Breakdown of Multi-Head Self-Attention in Transformers.",
         "Given input token matrix $X \\in \\mathbb{R}^{N \\times d_{\\text{model}}}$, we project using learned weights $W_Q, W_K, W_V \\in \\mathbb{R}^{d_{\\text{model}} \\times d_k}$:<br/>"
         "$$Q = X W_Q, \\quad K = X W_K, \\quad V = X W_V$$"
         "<b>Attention Formula:</b>"
         "$$\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{Q K^T}{\\sqrt{d_k}}\\right) V$$"
         "• $Q K^T \\in \\mathbb{R}^{N \\times N}$ computes dot-product similarity between every token query and key.<br/>"
         "• $\\frac{1}{\\sqrt{d_k}}$ scaling factor: Preserves unit variance and prevents vanishing gradients in the softmax function.<br/>"
         "• Multiplying by $V$ computes the final contextual token representations."),

        ("Q2: The KV Cache in LLM Inference: Memory Bandwidth Bottlenecks and PagedAttention.",
         "• <b>The Problem:</b> In autoregressive decoding, generating token $t+1$ requires attending to all prior tokens $1 \\dots t$. Recomputing $K$ and $V$ for all past tokens at every step requires $O(N^2)$ compute.<br/>"
         "• <b>KV Cache Solution:</b> Caches Key and Value tensors for past tokens in GPU VRAM. For token $t+1$, only compute new $Q_{t+1}, K_{t+1}, V_{t+1}$, append $K, V$ to cache, and compute attention.<br/>"
         "• <b>Memory Bandwidth Bound:</b> Generating a single token requires transferring the multi-gigabyte KV cache from High Bandwidth Memory (HBM) to SRAM with low arithmetic intensity. This makes LLM generation memory-bandwidth bound.<br/>"
         "• <b>PagedAttention (vLLM):</b> Divides the KV cache into fixed-size virtual memory blocks (pages) mapped non-contiguously, enabling near-zero memory waste and $4\\times$ higher serving throughput.")
    ]

    for q, a in ai_qas:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 9: CORE ALGORITHMIC PATTERNS & COMPLEXITY MATRIX
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 9: Core Algorithmic Patterns & LeetCode High-Frequency Solutions", "Mastery of Fundamental Algorithmic Paradigms with Clean Code & Complexity Analysis", styles))
    add_md("## Chapter 9: Core Algorithmic Patterns & LeetCode High-Frequency Solutions\n\n")

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

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 10: INTERVIEW DAY QUICK REFERENCE
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 10: Interview Day Fast Reference, Latency Numbers & Estimation Formulas", "Key numerical formulas, latency numbers, and top 10 interview pitfalls to avoid", styles))
    add_md("## Chapter 10: Interview Day Fast Reference, Latency Numbers & Estimation Formulas\n\n")

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
    generate_full_encyclopedia()
