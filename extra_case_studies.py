"""
Comprehensive System Design Case Studies & Advanced Architectural Breakdowns.
"""

CASE_STUDIES = [
    ("Case Study 1: Designing a Real-Time Collaborative Document Editor (e.g. Google Docs / Notion)",
     "<b>Functional Requirements:</b> Real-time multi-user editing with <50ms latency, conflict resolution, offline editing sync, document revision history, and user presence indicators (cursor positions).<br/>"
     "<b>Non-Functional Requirements:</b> High availability (99.99%), causal consistency, low bandwidth overhead, scalability to 10,000 active concurrent viewers per doc.<br/>"
     "<b>Core Architecture & Trade-Offs:</b><br/>"
     "1. <b>Concurrency & Conflict Resolution:</b><br/>"
     "  • <i>Operational Transformation (OT):</i> Centralized server transforms operation indices based on server sequence numbers. Used by Google Docs. Requires central server authority.<br/>"
     "  • <i>Conflict-free Replicated Data Types (CRDTs):</i> State-based (LWW-Element-Set) or Operation-based (Yjs, Automerge) mathematical structures with commutative and associative properties. Enables peer-to-peer offline merges with zero central server coordination.<br/>"
     "2. <b>Transport Layer:</b> WebSockets for full-duplex operation streaming; Redis Pub/Sub cluster for routing edits across document room shards.<br/>"
     "3. <b>Persistence:</b> PostgreSQL for document metadata and user permissions; Amazon S3 for immutable snapshot checkpoints taken every 100 operations + Cassandra for append-only operation logs."),

    ("Case Study 2: Designing a Global Distributed Rate Limiter (e.g. Cloudflare / Stripe)",
     "<b>Functional Requirements:</b> Limit API requests per client IP / API key (e.g. 100 req/min), return standard HTTP 429 Too Many Requests with `Retry-After` header, support tiered rate limits.<br/>"
     "<b>Non-Functional Requirements:</b> Sub-millisecond latency (<1ms), high throughput (1,000,000 QPS), high availability, resilience to edge network partitions.<br/>"
     "<b>Core Architecture:</b><br/>"
     "1. <b>Algorithm Selection:</b> <i>Sliding Window Counter</i> combining previous and current window counts with weights. Eliminates boundary spikes while using $O(1)$ memory per key.<br/>"
     "2. <b>Distributed Storage:</b> Redis Cluster with localized in-memory sliding window counters executing atomic Lua scripts (`EVAL`):<br/>"
     "<code>local current = redis.call('INCR', KEYS[1])<br/>"
     "if current == 1 then redis.call('EXPIRE', KEYS[1], ARGV[1]) end<br/>"
     "if current > tonumber(ARGV[2]) then return 0 else return 1 end</code><br/>"
     "3. <b>Edge Local Caching & Batching:</b> Edge proxies (Envoy / Cloudflare Workers) maintain local token buckets and synchronize batched usage to regional Redis nodes every 500ms, eliminating cross-region network latency."),

    ("Case Study 3: Designing a High-Throughput URL Shortener (e.g. TinyURL / Bitly)",
     "<b>Functional Requirements:</b> Given a long URL, generate a unique 7-character short URL (e.g. `tinyurl.com/aB3x9Z`); redirect short URLs with HTTP 301/302; track click analytics.<br/>"
     "<b>Non-Functional Requirements:</b> Read-heavy system (100:1 read-to-write ratio), 100M new URLs per month, sub-10ms redirect latency, 99.999% availability.<br/>"
     "<b>Capacity Estimations:</b><br/>"
     "• <i>Write QPS:</i> $100\\text{M} / 2.5\\text{M seconds} \\approx 40 \\text{ writes/sec}$.<br/>"
     "• <i>Read QPS:</i> $40 \\times 100 = 4,000 \\text{ reads/sec}$.<br/>"
     "• <i>Storage:</i> 100M URLs/mo $\\times 500$ bytes $\\times 12$ mo $\\times 5$ yrs $\\approx 3 \\text{ TB}$ (fits easily on a distributed DB).<br/>"
     "<b>Architecture & Hash Collision Avoidance:</b><br/>"
     "1. <b>Base62 Encoding:</b> 7 characters from `[a-zA-Z0-9]` yields $62^7 \\approx 3.52 \\times 10^{12}$ unique URLs.<br/>"
     "2. <b>Unique ID Generation:</b> Pre-generated Distributed ID Generator (Snowflake / ZooKeeper Token Ranges) generates 64-bit monotonically increasing integers, converted directly to Base62 without hash collisions.<br/>"
     "3. <b>Caching & Storage:</b> PostgreSQL with B+ Tree index on `short_hash`; Redis cache storing top 20% most accessed URLs (80-20 Pareto rule), achieving sub-2ms redirect latency."),

    ("Case Study 4: Designing a Distributed Vector Database with HNSW Indexing (e.g. Qdrant / Pinecone)",
     "<b>Functional Requirements:</b> High-dimensional vector upserts ($d=384 \\text{ to } 1536$), filtered Approximate Nearest Neighbor (ANN) search, metadata payload indexing, real-time collection updates.<br/>"
     "<b>Non-Functional Requirements:</b> Sub-15ms p99 query latency over 100M vectors, 99.99% availability, linear horizontal scalability.<br/>"
     "<b>Architecture:</b><br/>"
     "1. <b>Vector Index:</b> In-memory HNSW graphs with Scalar Quantization (converting FP32 to INT8, saving 75% RAM).<br/>"
     "2. <b>Storage Engine:</b> RocksDB / Memmap for persistent vector and metadata storage with Write-Ahead Logging.<br/>"
     "3. <b>Sharding & Partitioning:</b> Hash-based sharding across physical nodes; each node executes local HNSW graph traversal on its shard, coordinator node aggregates top-K results using Min-Heap priority queues.<br/>"
     "4. <b>Filtered Search:</b> Pre-filtering via payload bitmap indexes combined with vector graph exploration (Iterative Graph Traversal with filter conditions)."),

    ("Case Study 5: Designing a Real-Time Live Notification & Streaming Engine (e.g. Uber / Twitter Notifications)",
     "<b>Functional Requirements:</b> Push real-time notifications to millions of connected web and mobile devices, user preference filtering, notification deduplication, batching.<br/>"
     "<b>Non-Functional Requirements:</b> Scalability to 10M concurrent WebSocket connections, sub-100ms end-to-end delivery, at-least-once delivery guarantee.<br/>"
     "<b>Architecture:</b><br/>"
     "1. <b>Connection Layer:</b> Distributed WebSocket Gateway clusters behind Layer 4 Network Load Balancers. Each gateway maintains 50,000 active socket connections in memory.<br/>"
     "2. <b>Message Broker:</b> Apache Kafka message pipeline partitioned by `user_id`.<br/>"
     "3. <b>Routing & Presence:</b> Redis Cluster maintains user-to-gateway mapping (`user_123 -> gateway_pod_7`). When an event occurs, worker reads Redis, routes payload to the specific gateway pod via internal gRPC, which pushes the frame over the client's WebSocket.")
]

print("Case studies loaded.")
