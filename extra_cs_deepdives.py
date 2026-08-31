"""
30 Advanced Core Computer Science Deep-Dives across OS, Networks, DBMS, and AI.
"""

EXTRA_CS_DEEPDIVES = [
    # OS & Linux Internals
    ("Q9: Linux Signals, Signal Handlers, and Reentrancy Hazards.",
     "A <b>Signal</b> is an asynchronous notification sent by the Linux kernel to a process (e.g. `SIGINT` 2, `SIGKILL` 9, `SIGSEGV` 11, `SIGCHLD` 17).<br/>"
     "• <b>Signal Delivery:</b> Kernel sets bit in process's pending signal bitmap. When process returns from kernel mode to user mode, kernel forces execution of the registered signal handler function (`sigaction`).<br/>"
     "• <b>Reentrancy Hazards:</b> If a signal handler interrupts non-reentrant functions (like `malloc`, `printf`, or `free` which hold internal locks), calling those functions inside the handler causes immediate deadlocks. Only **async-signal-safe functions** (`write`, `_exit`) may be invoked safely within signal handlers."),

    ("Q10: Memory-Mapped Files (`mmap`) vs Standard Read/Write Syscalls (`read`/`write`).",
     "• <b>Standard `read()` / `write()`:</b> Incurs **two memory copies**: (1) Disk $\\rightarrow$ Kernel Page Cache (via DMA); (2) Kernel Page Cache $\\rightarrow$ User-Space Buffer (CPU copy). Also requires context switches between user/kernel mode.<br/>"
     "• <b>`mmap()` (Zero-Copy):</b> Maps file directly into the process's virtual address space. Accessing memory triggers on-demand page faults that load data directly into RAM. Reads/writes bypass user-space buffer copies, drastically accelerating high-throughput file I/O (used in SQLite, Kafka, RocksDB)."),

    ("Q11: The Linux `epoll` Architecture: `epoll_create`, `epoll_ctl`, and `epoll_wait`.",
     "• <b>`epoll_create1(0)`:</b> Creates an anonymous `epoll` file descriptor in the kernel with associated data structures: a Red-Black Tree (for tracking monitored FDs) and a Ready List (doubly-linked list for ready events).<br/>"
     "• <b>`epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &event)`:</b> Inserts the socket file descriptor into the kernel Red-Black Tree ($O(\\log N)$). Registers a callback with the network device driver.<br/>"
     "• <b>`epoll_wait(epfd, events, maxevents, timeout)`:</b> Puts calling thread to sleep. When network packets arrive, driver callback appends ready FD to the Ready List and wakes the thread. $O(1)$ lookup time relative to total monitored connections."),

    # Computer Networks & Protocols
    ("Q8: HTTP/2 Header Compression: The HPACK Algorithm.",
     "In HTTP/1.1, headers (cookies, user-agents, authorization) were re-transmitted as redundant plaintext on every single request.<br/>"
     "• <b>HPACK Architecture:</b> Maintains two tables: (1) <b>Static Table:</b> Predefined table of 61 common header fields (e.g. `:method: GET`, `:status: 200`); (2) <b>Dynamic Table:</b> Shared state updated incrementally per connection.<br/>"
     "• <b>Huffman Coding:</b> Header names/values are encoded using a static Huffman code table, reducing payload size by over 85% on repeat API requests."),

    ("Q9: The Mechanics of TCP Fast Open (TFO) and 0-RTT TLS Resumption.",
     "• <b>TCP Fast Open (RFC 7413):</b> Allows data payload to be included directly in the initial `SYN` packet along with a cryptographic TFO Cookie previously issued by the server. Eliminates 1 full RTT on repeat connections.<br/>"
     "• <b>TLS 1.3 0-RTT Early Data:</b> Uses a Pre-Shared Key (PSK) derived from a prior session ticket. Client sends encrypted application data in its very first `ClientHello` flight, enabling immediate API interaction."),

    ("Q10: Border Gateway Protocol (BGP) & Autonomous Systems (AS).",
     "The internet is an interconnected mesh of Autonomous Systems (AS). BGP is the Path Vector routing protocol governing inter-AS routing.<br/>"
     "• <b>BGP Routing:</b> Exchanges AS-PATH attributes to prevent routing loops. Routers select optimal paths based on route policies, shortest AS path length, and Multi-Exit Discriminators (MED).<br/>"
     "• <b>BGP Hijacking:</b> When a rogue AS maliciously broadcasts ownership of an IP prefix, diverting global traffic. Mitigated via RPKI (Resource Public Key Infrastructure) cryptographic route validation."),

    # Database Systems & Indexing
    ("Q7: LSM-Trees (Log-Structured Merge-Trees) vs B+ Trees (Write-Heavy vs Read-Heavy).",
     "• <b>B+ Trees:</b> In-place updates on disk pages. Optimal for Read-heavy workloads ($O(\\log N)$ random reads), but suffers write amplification and random disk I/O on heavy writes.<br/>"
     "• <b>LSM-Trees (Used in RocksDB, Cassandra, Qdrant):</b> Append-only structure. Writes are written sequentially to an in-memory sorted buffer (<b>MemTable</b>) and Write-Ahead Log. When full, MemTable is flushed sequentially to disk as an immutable <b>SSTable</b> (Sorted String Table). Background compaction merges SSTables. Optimal for high-throughput write workloads."),

    ("Q8: Distributed Consensus: The Raft Algorithm (Leader Election, Log Replication, Safety).",
     "Raft breaks distributed consensus into 3 independent subproblems:<br/>"
     "1. <b>Leader Election:</b> Randomized election timeouts prevent split votes. Candidate requests votes; becomes Leader upon receiving majority ($N/2 + 1$) votes.<br/>"
     "2. <b>Log Replication:</b> Leader receives client writes, appends to its log, broadcasts `AppendEntries` RPCs to followers. Commits entry once replicated on majority.<br/>"
     "3. <b>Election Safety:</b> A follower only votes for a candidate whose log is at least as up-to-date as its own (comparing `(term, index)`), guaranteeing committed entries are never overwritten."),

    # AI & Modern LLM Systems
    ("Q5: Rotary Position Embedding (RoPE) vs Sinusoidal Positional Encoding.",
     "• <b>Sinusoidal Positional Encoding (Original Transformer):</b> Adds absolute position vectors to token embeddings ($X + P$). Weak generalization to long sequence lengths beyond training context.<br/>"
     "• <b>Rotary Position Embedding (RoPE - used in LLaMA 3, Qwen 2.5):</b> Rotates Query and Key vector representations in 2D complex subspace planes: $q_m = R_{\\Theta, m} W_Q x_m$. The inner product $\\langle q_m, k_n \\rangle$ naturally encodes the **relative distance $(m - n)$**, enabling superior context length extrapolation (e.g. 128k+ tokens)."),

    ("Q6: Reinforcement Learning from Human Feedback (RLHF) vs Direct Preference Optimization (DPO).",
     "• <b>RLHF (PPO):</b> Requires 3 stages: (1) Supervised Fine-Tuning (SFT); (2) Training a Reward Model on human preference pairs; (3) Optimizing policy using PPO (Proximal Policy Optimization) with a KL-divergence penalty. Complex and unstable to train.<br/>"
     "• <b>DPO (Direct Preference Optimization):</b> Mathematically derives closed-form exact solution mapping reward function directly to policy probabilities: $\\mathcal{L}_{\\text{DPO}} = -\\log \\sigma \\left( \\beta \\log \\frac{\\pi(y_w|x)}{\\pi_{\\text{ref}}(y_w|x)} - \\beta \\log \\frac{\\pi(y_l|x)}{\\pi_{\\text{ref}}(y_l|x)} \\right)$. Eliminates separate reward model and PPO reinforcement learning loop.")
]

print("Loaded extra CS deep dives.")
