# Final Interview Questions by Company

These are representative system design questions asked at top tech companies. Each question is followed by key areas the interviewer expects you to cover.

**Instructions**: Pick one question, set a 45-minute timer, and design it on paper or a whiteboard. Then compare your design to the hints.

---

## Google

Google interviews emphasize scale, reliability, and elegant solutions. They love questions about distributed systems and data pipelines.

### Question 1: Design Google Search
**Difficulty**: Hard | **Time**: 45 min

Key areas to cover:
- Web crawling (distributed crawler, politeness, robots.txt)
- Indexing pipeline (MapReduce/Dataflow, inverted index)
- Ranking (PageRank, ML ranking signals)
- Serving (query parsing, index lookup, result ranking, < 200ms)
- Scale: 8.5 billion searches/day

Hints:
- Start with the crawling pipeline — how do you discover and fetch billions of pages?
- The inverted index is the core data structure: word → [doc_id, position, ...]
- Ranking is a separate concern from indexing — discuss both
- Discuss how you handle freshness (new pages indexed quickly)

### Question 2: Design Google Maps
**Difficulty**: Hard | **Time**: 45 min

Key areas to cover:
- Map tile serving (pre-rendered tiles at zoom levels)
- Routing algorithm (Dijkstra/A* on road graph)
- Real-time traffic (aggregating GPS data from millions of phones)
- ETA calculation
- Scale: 1 billion users, 25 million map updates/day

Hints:
- Map tiles are pre-rendered images — CDN is critical
- Road graph: nodes = intersections, edges = road segments with weights
- Traffic data: aggregate anonymized GPS from Android phones
- ETA: historical + real-time traffic data

### Question 3: Design YouTube
**Difficulty**: Medium-Hard | **Time**: 45 min

Key areas to cover:
- Video upload pipeline (encoding, transcoding, storage)
- Video serving (adaptive bitrate, CDN)
- Recommendation system
- Comment system (high write volume)
- Scale: 500 hours of video uploaded per minute

---

## Amazon

Amazon interviews focus on operational excellence, cost efficiency, and AWS services. They love questions about e-commerce and distributed systems.

### Question 4: Design Amazon's Product Catalog
**Difficulty**: Medium | **Time**: 45 min

Key areas to cover:
- Product data model (highly variable attributes per category)
- Search and filtering (Elasticsearch)
- Inventory management (consistency requirements)
- Price updates (high write volume)
- Scale: 350 million products

Hints:
- Product attributes vary wildly (a book has ISBN, a TV has resolution) → document store
- Search needs full-text + faceted filtering → Elasticsearch
- Inventory is write-heavy and needs strong consistency → SQL with careful sharding
- Price changes: ~1M price changes/day → async processing

### Question 5: Design Amazon's Order System
**Difficulty**: Hard | **Time**: 45 min

Key areas to cover:
- Order state machine (placed → confirmed → shipped → delivered)
- Distributed transaction (deduct inventory + charge payment + create order)
- Idempotency (retry safety)
- Order history (read-heavy, append-only)
- Scale: 1.6 million orders/day

Hints:
- Saga pattern for the distributed transaction
- Outbox pattern for reliable event publishing
- Order history: append-only → good fit for Cassandra or DynamoDB
- Idempotency key on payment API to prevent double charges

### Question 6: Design a Distributed Job Scheduler
**Difficulty**: Hard | **Time**: 45 min

Key areas to cover:
- Job definition (cron syntax, one-time, recurring)
- Distributed execution (multiple workers, no duplicate execution)
- Failure handling (retry, dead letter)
- Priority queues
- Scale: 1 million jobs/day

---

## Meta (Facebook)

Meta interviews emphasize social graph problems, news feed, and real-time systems.

### Question 7: Design Facebook News Feed
**Difficulty**: Hard | **Time**: 45 min

Key areas to cover:
- Feed generation (fan-out on write vs read)
- Ranking (ML model, engagement signals)
- Real-time updates (new posts appear quickly)
- Privacy (only show posts you're allowed to see)
- Scale: 3 billion users, billions of posts/day

Hints:
- Very similar to Twitter timeline — discuss the same fan-out tradeoffs
- Ranking is more complex than Twitter (ML model, not just chronological)
- Privacy check must happen at read time (permissions can change)
- Facebook uses a hybrid: fan-out for most users, pull for celebrities

### Question 8: Design Facebook Messenger
**Difficulty**: Hard | **Time**: 45 min

Key areas to cover:
- Real-time message delivery (WebSockets)
- Message storage (append-only, sharded by conversation_id)
- Online presence (who's online right now)
- Group chats
- Scale: 100 billion messages/day

Hints:
- Very similar to WhatsApp — discuss the same delivery guarantee patterns
- Online presence: heartbeat every 5 seconds, Redis with TTL
- Message storage: Cassandra sharded by conversation_id + timestamp
- Group chats: fan-out at server side (unlike WhatsApp's client-side E2E)

### Question 9: Design Instagram
**Difficulty**: Medium | **Time**: 45 min

Key areas to cover:
- Photo upload and storage (S3 + CDN)
- Feed generation (similar to Twitter)
- Stories (24-hour expiry)
- Explore page (content discovery)
- Scale: 100 million photos/day

---

## Microsoft

Microsoft interviews often focus on enterprise systems, Azure services, and reliability.

### Question 10: Design a Distributed Cache
**Difficulty**: Medium | **Time**: 45 min

Key areas to cover:
- Cache topology (client-side, proxy, server-side)
- Eviction policies
- Consistency (cache invalidation strategies)
- Replication and failover
- Scale: 1 million requests/second

### Question 11: Design Azure Blob Storage
**Difficulty**: Hard | **Time**: 45 min

Key areas to cover:
- Object storage model (buckets, objects, metadata)
- Replication (LRS, ZRS, GRS)
- Consistency model
- Large file uploads (multipart)
- Scale: exabytes of data

---

## Stripe / Fintech

Fintech interviews emphasize correctness, idempotency, and auditability over raw scale.

### Question 12: Design a Payment Processing System
**Difficulty**: Hard | **Time**: 45 min

Key areas to cover:
- Idempotency (never charge twice)
- Distributed transaction (debit sender, credit receiver)
- Fraud detection (real-time ML scoring)
- Audit log (immutable, append-only)
- Reconciliation (end-of-day balance checks)

Hints:
- Idempotency key: client generates UUID, server deduplicates
- Two-phase commit or Saga for the transfer
- Fraud detection: synchronous (< 100ms) ML model call
- Audit log: append-only Kafka topic → data warehouse
- This is a CP system — consistency over availability

### Question 13: Design a Rate Limiter as a Service
**Difficulty**: Medium | **Time**: 45 min

Key areas to cover:
- Algorithm choice (token bucket, sliding window)
- Distributed state (Redis Cluster)
- Low latency (< 1ms overhead)
- Failure mode (what if Redis is down?)
- Multi-tenancy (different limits per customer)

---

## Startup / General

### Question 14: Design a Notification System
**Difficulty**: Medium | **Time**: 45 min

Key areas to cover:
- Multiple channels (push, email, SMS, in-app)
- User preferences (opt-out, frequency caps)
- Delivery guarantees (at-least-once)
- Template rendering
- Scale: 1 billion notifications/day

### Question 15: Design a Real-Time Leaderboard
**Difficulty**: Medium | **Time**: 45 min

Key areas to cover:
- Score updates (high write volume)
- Top-N queries (get top 100 players)
- User rank queries (where am I in the ranking?)
- Historical snapshots (daily/weekly leaderboards)
- Scale: 10 million players, 1 million score updates/minute

Hints:
- Redis Sorted Set: ZADD, ZREVRANK, ZREVRANGE
- For global leaderboard: Redis Cluster with scatter-gather
- Historical: snapshot to database at end of period

---

## Interview Tips by Company

| Company | What They Value | Watch Out For |
|---------|----------------|---------------|
| Google | Elegance, scale, distributed systems | Don't skip the hard algorithmic parts |
| Amazon | Operational excellence, cost, AWS | They'll ask about failure modes |
| Meta | Social graph, real-time, scale | Privacy and permissions are important |
| Microsoft | Enterprise reliability, Azure | Don't forget about SLAs |
| Stripe | Correctness, idempotency, auditability | Scale is secondary to correctness |
| Startups | Pragmatism, speed, simplicity | Don't over-engineer |

---

## The 45-Minute Framework

Use this structure for every interview:

```
0:00 - 5:00   Requirements clarification
5:00 - 10:00  Capacity estimation
10:00 - 20:00 High-level design
20:00 - 35:00 Deep dive (2 components)
35:00 - 40:00 Bottlenecks and scaling
40:00 - 45:00 Tradeoffs and wrap-up
```

If the interviewer redirects you, follow their lead. They're telling you what they care about.
