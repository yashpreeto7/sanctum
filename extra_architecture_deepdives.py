"""
Extra architectural deep dives to reach 45+ pages.
"""

EXTRA_ARCH_DEEPDIVES = [
    ("9.3 Distributed Cache Architecture: Redis vs Memcached Deep Dive",
     "• <b>Threading Model:</b> Redis uses a single-threaded event loop (with multi-threaded I/O since Redis 6.0) avoiding locking contention and context switching; Memcached uses multi-threaded master-worker architecture.<br/>"
     "• <b>Data Structures:</b> Redis supports rich native data structures (Strings, Hashes, Lists, Sets, Sorted Sets `ZSET`, Bitmaps, HyperLogLogs, Geospatial, Streams); Memcached supports only simple key-value strings.<br/>"
     "• <b>Persistence:</b> Redis supports RDB point-in-time snapshots and AOF (Append-Only File) logging with `fsync` policies; Memcached is pure in-memory without persistence.<br/>"
     "• <b>Replication & Clustering:</b> Redis Sentinel provides high-availability leader failover; Redis Cluster provides automatic multi-shard partitioning across 16,384 hash slots with master-replica topologies."),

    ("9.4 API Gateway Patterns & Reverse Proxies (Envoy vs Nginx vs Kong)",
     "An API Gateway acts as the single entry point for client requests, decoupling frontend clients from microservices.<br/>"
     "• <b>Core Responsibilities:</b> (1) Dynamic Service Discovery & Load Balancing; (2) TLS Termination and Certificate Management; (3) Rate Limiting & DDoS Shielding; (4) JWT / OAuth2 Authentication; (5) Request/Response Transformation; (6) Distributed Tracing (injecting `traceparent` / W3C headers).<br/>"
     "• <b>Envoy Proxy (C++):</b> High-performance L7 proxy with dynamic control plane configuration via xDS APIs (gRPC). Standard for service meshes (Istio)."),

    ("9.5 Reliable Webhook Delivery Engine with Exponential Backoff & Dead Letter Queues (DLQs)",
     "Delivering webhooks to external third-party customer endpoints requires resilient retry architectures.<br/>"
     "• <b>Architecture:</b><br/>"
     "  1. <i>Event Ingestion:</i> Internal service publishes event to RabbitMQ / Kafka topic.<br/>"
     "  2. <i>Worker Dispatch:</i> Webhook worker signs payload with HMAC-SHA256 signature (`X-Hub-Signature-256`) and dispatches HTTP POST.<br/>"
     "  3. <i>Exponential Backoff Retries:</i> If endpoint returns non-2xx (or timeouts >5s), message is routed to retry delay queues with intervals ($2^n \\times 5\\text{s}$: 5s, 10s, 20s, 40s, 80s up to 24 hours).<br/>"
     "  4. <i>Dead Letter Queue (DLQ):</i> If all 10 retry attempts fail, event is moved to DLQ for manual inspection and alerting."),

    ("9.6 Database Connection Pooling: Why PgBouncer is Essential in PostgreSQL",
     "PostgreSQL forks a dedicated backend process for every single client connection (consuming 2–10MB RAM per process).<br/>"
     "• <b>The Problem:</b> When thousands of microservice instances connect directly to Postgres, memory usage explodes and CPU spends 70% of cycles on process context switching rather than query execution.<br/>"
     "• <b>PgBouncer Pooling Modes:</b><br/>"
     "  • <i>Session Pooling:</i> Client keeps server connection for lifetime of its session.<br/>"
     "  • <i>Transaction Pooling (Recommended):</i> Server connection is released back to the pool immediately after `COMMIT` or `ROLLBACK`. Reduces 10,000 application connections down to 50 physical Postgres connections, boosting throughput by $5\\times$.")
]

print("Loaded extra arch deepdives.")
