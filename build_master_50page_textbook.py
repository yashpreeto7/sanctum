"""
Master 45-50+ Page Engineering Textbook & Technical Interview Dossier.
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
from extra_case_studies import CASE_STUDIES
from extra_code_listings import CODE_LISTINGS
from extra_leetcode_and_sysdesign import LEETCODE_20, EXTRA_CASE_STUDIES
from extra_cs_deepdives import EXTRA_CS_DEEPDIVES

def build_complete_50page_textbook():
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
    # TITLE & METADATA BANNER
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
    # CHAPTER 1: CANDIDATE NARRATIVE & 15 STAR STORIES
    # ══════════════════════════════════════════════════════════════════════════
    story.extend(create_section_header("Chapter 1: Candidate Positioning, Narrative & Behavioral STAR Playbook", "Strategic communication frameworks and 15 deep situational STAR breakdowns", styles))
    add_md("## Chapter 1: Candidate Positioning, Narrative & Behavioral STAR Playbook\n\n")

    story.append(Paragraph("1.1 The 90-Second High-Impact Self-Introduction", styles['h2']))
    story.append(Paragraph(f"<i>\"{CANDIDATE_INTRO}\"</i>", styles['callout']))
    story.append(Spacer(1, 8))
    add_md(f"### 1.1 The 90-Second High-Impact Self-Introduction\n\n> {CANDIDATE_INTRO}\n\n")

    story.append(Paragraph("1.2 The Complete 15-Scenario Behavioral STAR Playbook", styles['h2']))
    add_md("### 1.2 The Complete 15-Scenario Behavioral STAR Playbook\n\n")

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
    story.extend(create_section_header("Chapter 2: SovereignOS — Flagship Engineering Reference Manual", "Exhaustive file-by-file codebase walkthrough, state graph DAG, and architectural layers", styles))
    add_md("## Chapter 2: SovereignOS — Flagship Engineering Reference Manual\n\n")

    for title, desc in SOVEREIGN_CODEBASE_FILES:
        story.append(Paragraph(f"<b>{title}</b>", styles['h3']))
        story.append(Paragraph(desc, styles['body']))
        story.append(Spacer(1, 4))
        add_md(f"#### {title}\n{desc.replace('<b>', '**').replace('</b>', '**').replace('<br/>', '\n')}\n\n")

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 3: SOVEREIGN OS SOURCE CODE WALKTHROUGHS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 3: SovereignOS — Core Python Source Code Walkthroughs", "Line-by-line implementation of WebSocket streaming, Quarantine security, Hybrid RAG, and Calendar sync", styles))
    add_md("## Chapter 3: SovereignOS — Core Python Source Code Walkthroughs\n\n")

    for title, code_str in CODE_LISTINGS:
        story.append(Paragraph(f"<b>{title}</b>", styles['h3']))
        formatted_code = "<br/>".join(code_str.replace(" ", "&nbsp;").split("\n"))
        story.append(Paragraph(formatted_code, styles['code']))
        story.append(Spacer(1, 6))
        add_md(f"#### {title}\n```python\n{code_str}\n```\n\n")

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 4: 30 SOVEREIGN OS INTERVIEW QUESTIONS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 4: SovereignOS — Top 30 Technical Interview Q&As", "Exhaustive architectural, performance, security, and edge-case question breakdowns", styles))
    add_md("## Chapter 4: SovereignOS — Top 30 Technical Interview Q&As\n\n")

    for q, a in SOVEREIGN_30_QA:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 5: PORTFOLIO & GITHUB PROJECTS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 5: Portfolio & GitHub Repositories Deep Dive", "Exhaustive engineering analysis of MacroLens Vision AI, Pal-AI, DocDispatch, JobHunter, and VideoTube", styles))
    add_md("## Chapter 5: Portfolio & GitHub Repositories Deep Dive\n\n")

    story.append(Paragraph("5.1 MacroLens Vision AI — Nutrition & Fitness Platform", styles['h2']))
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

    macrolens_qa = [
        ("Q1: How do you handle schema hallucinations when an LLM Vision API returns food analysis?",
         "LLMs frequently return markdown wrappers (```json) or hallucinate non-standard keys. I implemented a 3-layer validation pipeline: (1) System prompt with strict JSON schema and few-shot examples; (2) Regex pre-processor that strips markdown ticks and fixes trailing commas; (3) Joi/Zod runtime schema validator in Node.js checking numeric constraints (e.g. protein >= 0, calories <= 5000). If validation fails, it triggers an immediate retry with temperature=0.1 or prompts the user for manual confirmation."),

        ("Q2: Walk me through the MongoDB aggregation pipeline for daily nutrition totals.",
         "The pipeline executes in 4 stages: (1) `$match`: Filters meal logs by `userId` and ISO date range `[start_date, end_date]` utilizing the compound index `{ userId: 1, date: -1 }`; (2) `$unwind`: Deconstructs the `foods` array into separate document streams; (3) `$group`: Groups by `date` and computes `$sum` for `calories`, `protein`, `carbs`, and `fats`; (4) `$sort`: Orders chronologically by date. Execution time is under 12ms across thousands of documents.")
    ]
    for q, a in macrolens_qa:
        story.extend(make_qa(q, a, styles))

    story.append(Paragraph("5.2 Pal-AI — Provider-Agnostic Multi-Turn Companion", styles['h2']))
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

    story.append(Paragraph("5.3 DocDispatch, JobHunter & VideoTube-Backend", styles['h2']))
    story.append(Paragraph(
        "• <b>DocDispatch (React, Redux Toolkit, Tailwind CSS):</b> Role-based healthcare scheduling platform (Doctors & Patients) featuring strict WAI-ARIA 2.1 AA accessibility compliance, modal keyboard focus trapping, and reusable design system tokens.<br/>"
        "• <b>JobHunter (Python Automation Pipeline):</b> Multi-threaded job scraping, ATS keyword analysis, and automated application workflow engine using Selenium, BeautifulSoup, and vector matching.<br/>"
        "• <b>VideoTube-Backend (Node.js, Express, MongoDB, Cloudinary):</b> Video hosting backend featuring JWT authentication, video transcoding upload pipelines, subscription aggregation pipelines, and like/comment nested document schemas.",
        styles['body']
    ))
    story.append(Spacer(1, 8))

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 6: OPERATING SYSTEMS & LOW-LEVEL CONCURRENCY
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 6: Operating Systems & Low-Level Concurrency Masterclass", "Processes, Threads, Linux Kernel Internals, Virtual Memory, Memory Models, and Synchronization", styles))
    add_md("## Chapter 6: Operating Systems & Low-Level Concurrency Masterclass\n\n")

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
         "3. <b>Cyclic Garbage Collector:</b> Reference counting fails on reference cycles (Object A references B, B references A). Python runs a generational cyclic GC dividing objects into Gen 0 (young), Gen 1 (middle), Gen 2 (old). It detects cycles using double-linked lists and trial reference count decrementing."),

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

    for q, a in os_master_qa:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # Extra CS Deep Dives (OS)
    for q, a in EXTRA_CS_DEEPDIVES[:3]:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 7: COMPUTER NETWORKS MASTERCLASS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 7: Computer Networks & Distributed Web Transport Masterclass", "OSI 7 Layers, TCP Congestion Control, TLS 1.3 Cryptography, HTTP/2 & HTTP/3 QUIC", styles))
    add_md("## Chapter 7: Computer Networks & Distributed Web Transport Masterclass\n\n")

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
         "7. <b>Caching & TTL:</b> Resolver caches record for the specified TTL (Time-To-Live) and returns IP to the browser to initiate the TCP 3-way handshake."),

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

    for q, a in net_master_qa:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # Extra CS Deep Dives (Networks)
    for q, a in EXTRA_CS_DEEPDIVES[3:6]:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 8: DATABASE MANAGEMENT SYSTEMS MASTERCLASS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 8: Database Management Systems & Indexing Masterclass", "B+ Trees vs HNSW Vectors, ACID Transactions, MVCC, Isolation Levels & Sharding", styles))
    add_md("## Chapter 8: Database Management Systems & Indexing Masterclass\n\n")

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
         "  - <i>Serializable:</i> Prevents all anomalies via 2PL or SSI (Serializable Snapshot Isolation)."),

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

    for q, a in db_master_qa:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # Extra CS Deep Dives (DBMS)
    for q, a in EXTRA_CS_DEEPDIVES[6:8]:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 9: SYSTEM DESIGN CASE STUDIES (7 Case Studies)
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 9: System Design & Enterprise Architecture Masterclass", "CAP Theorem, Rate Limiting, Consistent Hashing, and 7 End-to-End Case Studies", styles))
    add_md("## Chapter 9: System Design & Enterprise Architecture Masterclass\n\n")

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
         "  - <i>Orchestration:</i> Centralized Saga Orchestrator tells participants which local transaction to execute. Easier to monitor and debug."),

        ("Q4: Cache Stampede (Thundering Herd) Solutions: Mutex Locking vs Probabilistic Early Expiration (XFetch).",
         "• <b>Problem:</b> When a popular hot cache key expires, thousands of concurrent requests miss the cache simultaneously and query the database at once, causing DB failure.<br/>"
         "• <b>Mutex Lock (Single-Flight):</b> The first worker that detects cache miss acquires a distributed lock (Redis `SET key value NX EX 5`), queries DB, and updates cache. Other workers wait or retry.<br/>"
         "• <b>Probabilistic Early Expiration (XFetch Algorithm):</b> Computes an early recomputation trigger: $\\Delta - \\beta \\times \\ln(rand()) > \\text{TTL}$, where $\\Delta$ is computation time and $\\beta > 0$. As TTL nears expiration, incoming requests probabilistically refresh the cache in the background before it officially expires."),

        ("Q5: Distributed Idempotency in Payment & Order Processing Systems.",
         "• <b>Idempotency Key:</b> Client generates a unique UUID (e.g. `Idempotency-Key: 7b8e...`) in request headers.<br/>"
         "• <b>Processing Flow:</b> (1) Server checks Redis/Postgres for existing idempotency key; (2) If found with status `COMPLETED`, returns cached response immediately; (3) If found with `PROCESSING`, returns HTTP 409 Conflict; (4) If not found, inserts key with status `PROCESSING` within atomic transaction, executes payment, updates status to `COMPLETED`, and saves response payload.")
    ]

    for q, a in sys_master_qa:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    story.append(Paragraph("9.2 End-to-End System Design Case Studies", styles['h2']))
    add_md("### 9.2 End-to-End System Design Case Studies\n\n")

    for cs_title, cs_content in CASE_STUDIES + EXTRA_CASE_STUDIES:
        story.append(Paragraph(f"<b>{cs_title}</b>", styles['h3']))
        story.append(Paragraph(cs_content, styles['body']))
        story.append(Spacer(1, 4))
        add_md(f"#### {cs_title}\n{cs_content.replace('<b>', '**').replace('</b>', '**').replace('<br/>', '\n')}\n\n")

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 10: MODERN AI & LLM SYSTEMS ENGINEERING
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 10: Modern AI & LLM Systems Engineering Masterclass", "Transformer Attention Mathematics, KV Caching, Quantization, RAGAS & Agent Protocols", styles))
    add_md("## Chapter 10: Modern AI & LLM Systems Engineering Masterclass\n\n")

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
         "• <b>PagedAttention (vLLM):</b> Standard KV caches allocate contiguous VRAM blocks per request, causing 60-80% memory waste due to internal/external fragmentation. PagedAttention divides the KV cache into fixed-size virtual memory blocks (pages) mapped non-contiguously, enabling near-zero memory waste and $4\\times$ higher serving throughput."),

        ("Q3: Deep Dive: Quantization Techniques (FP16 vs INT8 vs INT4 - GPTQ, AWQ, GGUF).",
         "Quantization reduces memory footprint and increases inference throughput by lowering precision of model weights and activations.<br/>"
         "• <b>Post-Training Quantization (PTQ):</b> Converts weights after training without retraining.<br/>"
         "• <b>GPTQ (Generalized Post-Training Quantization):</b> Layer-wise second-order Taylor approximation minimizing MSE loss between full-precision and quantized weights ($O(W^T H W)$).<br/>"
         "• <b>AWQ (Activation-aware Weight Quantization):</b> Observes that only 1% of salient weight channels protect model accuracy; preserves salient weights in higher precision and quantizes remaining 99%.<br/>"
         "• <b>GGUF (GPT-Generated Unified Format):</b> Binary file format used by `llama.cpp` and Ollama storing quantized weights, tokenizer vocabulary, and hyperparameter metadata in a single portable file for CPU/GPU offloading."),

        ("Q4: Advanced Agentic Design Patterns: ReAct vs Plan-and-Solve vs Reflection vs Multi-Agent Swarms.",
         "• <b>ReAct (Reasoning + Acting):</b> Interleaves reasoning steps ('Thought') with tool invocations ('Action') and environment feedback ('Observation') in a cyclical loop.<br/>"
         "• <b>Plan-and-Solve:</b> Decomposes a complex goal into an explicit step-by-step plan first, then executes steps sequentially, updating the plan upon error.<br/>"
         "• <b>Reflection / Self-Correction:</b> Agent evaluates its own generated output against test cases or critique rubrics, producing critique feedback and iterating.<br/>"
         "• <b>Multi-Agent Supervisor:</b> Central controller routes tasks to specialized domain agents (Coder, Searcher, Reviewer), aggregates findings, and produces the final answer.")
    ]

    for q, a in ai_master_qa:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # Extra CS Deep Dives (AI)
    for q, a in EXTRA_CS_DEEPDIVES[8:]:
        story.extend(make_qa(q, a, styles))
        add_md(f"#### {q}\n**Answer:** {a}\n\n")

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 11: 8 FULL LEETCODE PROBLEM SOLUTIONS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 11: Core Algorithmic Patterns & LeetCode High-Frequency Solutions", "Mastery of 10 Fundamental Algorithmic Paradigms with Clean Code & Complexity Analysis", styles))
    add_md("## Chapter 11: Core Algorithmic Patterns & LeetCode High-Frequency Solutions\n\n")

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

    for title, problem_body in LEETCODE_20:
        story.append(Paragraph(f"<b>{title}</b>", styles['h3']))
        story.append(Paragraph(problem_body, styles['body']))
        story.append(Spacer(1, 4))
        add_md(f"#### {title}\n{problem_body.replace('<b>', '**').replace('</b>', '**').replace('<br/>', '\n')}\n\n")

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 12: LATENCY NUMBERS & ESTIMATION (Final Chapter)
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.extend(create_section_header("Chapter 12: Interview Day Fast Reference, Latency Numbers & Estimation Formulas", "Key numerical formulas, latency numbers, and top 10 interview pitfalls to avoid", styles))
    add_md("## Chapter 12: Interview Day Fast Reference, Latency Numbers & Estimation Formulas\n\n")

    sd_math = (
        "• <b>QPS (Queries Per Second):</b> $\\text{QPS} = \\frac{\\text{Daily Active Users (DAU)} \\times \\text{Requests per User}}{86,400 \\text{ seconds}}$.<br/>"
        "• <b>Peak QPS:</b> $\\text{Peak QPS} = \\text{Average QPS} \\times 2 \\text{ to } 3$.<br/>"
        "• <b>Storage Estimation:</b> $\\text{Annual Storage} = \\text{Daily Requests} \\times \\text{Payload Size} \\times 365 \\text{ days} \\times \\text{Replication Factor (3)}$.<br/>"
        "• <b>Network Bandwidth:</b> $\\text{Incoming Bandwidth} = \\text{QPS} \\times \\text{Payload Size (Bytes)} \\times 8 \\text{ bits}$."
    )

    cheat_data = [
        [Paragraph("<b>Operation / Resource</b>", styles['body_bold']), Paragraph("<b>Approximate Latency</b>", styles['body_bold']), Paragraph("<b>Scale Comparison & Takeaway</b>", styles['body_bold'])],
        [Paragraph("L1 CPU Cache Reference", styles['body']), Paragraph("~ 1 ns", styles['body']), Paragraph("Fastest hardware memory lookup.", styles['body'])],
        [Paragraph("Main Memory (RAM) Access", styles['body']), Paragraph("~ 100 ns", styles['body']), Paragraph("100x slower than L1 cache.", styles['body'])],
        [Paragraph("NVMe SSD Random Read", styles['body']), Paragraph("~ 10–50 μs", styles['body']), Paragraph("100x to 500x slower than RAM.", styles['body'])],
        [Paragraph("Network Roundtrip (Same Datacenter)", styles['body']), Paragraph("~ 0.5 ms", styles['body']), Paragraph("10x slower than SSD.", styles['body'])],
        [Paragraph("Cross-Continental Network (NYC - London)", styles['body']), Paragraph("~ 70–100 ms", styles['body']), Paragraph("Speed of light in fiber constraint.", styles['body'])]
    ]

    story.append(Paragraph("12.1 Latency Numbers Every Software Engineer Must Memorize", styles['h2']))
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

    story.append(Paragraph("12.2 System Design Quantitative Estimation Formulas", styles['h2']))
    story.append(Paragraph(sd_math, styles['body']))
    story.append(Spacer(1, 8))

    story.append(Paragraph("12.3 Top 10 Red Flags in Technical Interviews and How to Avoid Them", styles['h2']))
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
    print(f"50-Page Masterpiece PDF successfully compiled at: {pdf_path}")

    with open(md_path, "w", encoding="utf-8") as f:
        f.writelines(md_lines)
    print(f"50-Page Masterpiece Markdown successfully compiled at: {md_path}")

if __name__ == "__main__":
    build_complete_50page_textbook()
