# 30-Day Knowledge Checklist

Rate yourself on each item: ✅ Solid | 🟡 Shaky | ❌ Need to review

Be honest. The gaps you identify today are the ones to focus on next.

---

## Week 1: Foundations

### Scalability (Day 1)
- [ ] Explain vertical vs horizontal scaling and when to use each
- [ ] Define throughput, latency, and the difference between them
- [ ] Explain what a p99 latency means and why it matters
- [ ] Describe the three-tier architecture (presentation, application, data)
- [ ] Explain why stateless servers are easier to scale
- [ ] Define SLA, SLO, and SLI
- [ ] Explain what "9s of availability" means (99.9% = 8.7 hrs downtime/year)

### Networking (Day 2)
- [ ] Explain what happens when you type a URL in a browser (DNS → TCP → HTTP)
- [ ] Describe the difference between TCP and UDP and when to use each
- [ ] Explain HTTP/1.1 vs HTTP/2 vs HTTP/3 key differences
- [ ] Define what a CDN is and how it works
- [ ] Explain TLS handshake at a high level
- [ ] Describe what a reverse proxy does vs a forward proxy
- [ ] Explain long polling vs WebSockets vs Server-Sent Events

### Load Balancing (Day 3)
- [ ] Name and explain 4 load balancing algorithms
- [ ] Explain the difference between L4 and L7 load balancing
- [ ] Describe how sticky sessions work and their tradeoffs
- [ ] Explain what health checks do in a load balancer
- [ ] Describe active-active vs active-passive failover

### Caching (Day 4)
- [ ] Explain cache-aside, write-through, write-behind, and read-through patterns
- [ ] Define cache eviction policies (LRU, LFU, FIFO) and when to use each
- [ ] Explain cache stampede / thundering herd and how to prevent it
- [ ] Describe what a CDN cache is and how it differs from an application cache
- [ ] Explain TTL and why you add jitter to TTLs
- [ ] Define cache hit rate and what a "good" hit rate looks like

### SQL Databases (Day 5)
- [ ] Explain ACID properties (Atomicity, Consistency, Isolation, Durability)
- [ ] Describe the difference between a clustered and non-clustered index
- [ ] Explain what a B-tree index is and why it's used
- [ ] Describe N+1 query problem and how to fix it
- [ ] Explain database normalization (1NF, 2NF, 3NF) and when to denormalize
- [ ] Describe read replicas and their limitations
- [ ] Explain what a database transaction isolation level is

### NoSQL Databases (Day 6)
- [ ] Name the 4 types of NoSQL databases and give an example of each
- [ ] Explain when you'd choose NoSQL over SQL
- [ ] Describe the document model (MongoDB) and its tradeoffs
- [ ] Explain the wide-column model (Cassandra) and its use cases
- [ ] Describe eventual consistency and give a real-world example
- [ ] Explain what BASE means (Basically Available, Soft state, Eventually consistent)

---

## Week 2: Distributed Systems

### CAP Theorem (Day 8)
- [ ] State the CAP theorem correctly
- [ ] Explain why CA systems don't exist in distributed systems
- [ ] Give examples of CP systems and AP systems
- [ ] Explain what happens to a CP system during a network partition
- [ ] Explain what happens to an AP system during a network partition
- [ ] Describe PACELC theorem (extends CAP with latency tradeoffs)

### Replication (Day 9)
- [ ] Explain leader-follower replication and its failure modes
- [ ] Describe multi-leader replication and the conflict problem
- [ ] Explain leaderless replication (Dynamo-style)
- [ ] Define synchronous vs asynchronous replication tradeoffs
- [ ] Explain what replication lag is and its consequences
- [ ] Describe how read-your-own-writes consistency works

### Sharding (Day 10)
- [ ] Explain range-based vs hash-based sharding
- [ ] Describe the hotspot problem and how to fix it
- [ ] Explain what a scatter-gather query is
- [ ] Describe how you handle cross-shard transactions
- [ ] Explain resharding and why it's painful
- [ ] Describe the difference between sharding and partitioning

### Consistent Hashing (Day 11)
- [ ] Explain why `hash(key) % N` is problematic when N changes
- [ ] Describe how consistent hashing solves this
- [ ] Explain what virtual nodes are and why they're needed
- [ ] Describe how consistent hashing handles node addition/removal
- [ ] Name systems that use consistent hashing (Cassandra, DynamoDB, Redis Cluster)

### Message Queues (Day 12)
- [ ] Explain at-most-once, at-least-once, and exactly-once delivery
- [ ] Describe the difference between a queue and a topic (pub/sub)
- [ ] Explain when to use Kafka vs RabbitMQ vs SQS
- [ ] Describe the consumer group pattern in Kafka
- [ ] Explain what message ordering guarantees Kafka provides
- [ ] Describe the dead letter queue pattern

### Rate Limiting (Day 13)
- [ ] Explain the token bucket algorithm
- [ ] Describe the leaky bucket algorithm and how it differs
- [ ] Explain the sliding window log algorithm
- [ ] Describe the fixed window counter and its boundary problem
- [ ] Explain how to implement distributed rate limiting (across multiple servers)
- [ ] Describe where to implement rate limiting (client, API gateway, service)

---

## Week 3: Microservices

### Microservices (Day 15)
- [ ] Explain Conway's Law and its implications for architecture
- [ ] Describe the strangler fig pattern for migrating from monolith
- [ ] Explain the circuit breaker pattern and when it triggers
- [ ] Describe the bulkhead pattern
- [ ] Explain what a service mesh is (Istio, Linkerd)
- [ ] Describe the sidecar pattern

### API Design (Day 16)
- [ ] Explain REST constraints (stateless, uniform interface, etc.)
- [ ] Describe GraphQL advantages over REST
- [ ] Explain gRPC and when to use it over REST
- [ ] Describe API versioning strategies and their tradeoffs
- [ ] Explain idempotency and why it matters for APIs
- [ ] Describe pagination patterns (cursor vs offset)

### Service Discovery (Day 17)
- [ ] Explain client-side vs server-side service discovery
- [ ] Describe how Consul or Eureka works
- [ ] Explain DNS-based service discovery
- [ ] Describe health checks and their role in service discovery
- [ ] Explain what happens when a service instance fails

### Distributed Transactions (Day 18)
- [ ] Explain why ACID transactions don't work across services
- [ ] Describe the Two-Phase Commit (2PC) protocol and its problems
- [ ] Explain the Saga pattern (choreography vs orchestration)
- [ ] Describe compensating transactions
- [ ] Explain eventual consistency in the context of sagas

### Observability (Day 19)
- [ ] Explain the three pillars of observability (metrics, logs, traces)
- [ ] Describe the Four Golden Signals (latency, traffic, errors, saturation)
- [ ] Explain distributed tracing and how trace IDs work
- [ ] Describe structured logging and why it's better than plain text
- [ ] Explain what an SLO is and how to set one
- [ ] Describe the difference between monitoring and observability

### CDN and Edge (Day 20)
- [ ] Explain how a CDN works (PoPs, origin, edge caching)
- [ ] Describe cache invalidation strategies (TTL, purge, versioned URLs)
- [ ] Explain edge computing and give an example use case
- [ ] Describe when to use a CDN vs when it doesn't help
- [ ] Explain what Anycast routing is

---

## Week 4: Case Studies

### URL Shortener (Day 22)
- [ ] Design a URL shortener end-to-end in 10 minutes
- [ ] Explain base62 encoding and why it's used
- [ ] Describe how to handle custom aliases
- [ ] Explain how to track click analytics
- [ ] Describe how to handle redirects at scale (301 vs 302)

### Key-Value Store (Day 23)
- [ ] Explain LSM trees vs B-trees and when to use each
- [ ] Describe what an SSTable is
- [ ] Explain what a bloom filter does and why it's useful
- [ ] Describe the compaction process
- [ ] Explain Redis persistence options (RDB vs AOF)
- [ ] Describe Redis eviction policies

### Twitter (Day 24)
- [ ] Explain the fan-out on write vs fan-out on read tradeoff
- [ ] Describe Twitter's hybrid approach for celebrities
- [ ] Explain what a Snowflake ID is
- [ ] Describe how to shard the tweets table
- [ ] Explain how search works at Twitter scale

### Uber (Day 25)
- [ ] Explain how to handle 500K location updates/second
- [ ] Describe geospatial indexing (geohash or S2)
- [ ] Explain the driver matching algorithm
- [ ] Describe the trip state machine
- [ ] Explain how surge pricing is computed

### Netflix (Day 26)
- [ ] Explain why Netflix built its own CDN (Open Connect)
- [ ] Describe the video encoding pipeline
- [ ] Explain adaptive bitrate streaming
- [ ] Describe how the recommendation system works at scale
- [ ] Explain the thundering herd problem and Netflix's solution

### WhatsApp (Day 27)
- [ ] Explain why WhatsApp chose Erlang
- [ ] Describe the message delivery flow with receipts
- [ ] Explain how group messaging works at scale
- [ ] Describe how E2E encryption affects the architecture
- [ ] Explain how offline message delivery works

### Security (Day 28)
- [ ] Explain OAuth 2.0 flow
- [ ] Describe JWT structure and validation
- [ ] Explain mTLS and when to use it
- [ ] Describe common attack vectors (SQL injection, XSS, CSRF)
- [ ] Explain the principle of least privilege
- [ ] Describe secrets management (Vault, AWS Secrets Manager)

---

## Meta-Skills

### Interview Process
- [ ] Can clarify requirements in < 5 minutes
- [ ] Can do back-of-envelope estimation confidently
- [ ] Can draw a high-level architecture in < 10 minutes
- [ ] Can identify the hardest problem in any design
- [ ] Can discuss tradeoffs without being prompted
- [ ] Can handle "what if the scale is 10x?" questions
- [ ] Can communicate while thinking (no long silences)

### Technology Selection
- [ ] Know when to use SQL vs NoSQL
- [ ] Know when to use Redis vs Memcached
- [ ] Know when to use Kafka vs RabbitMQ vs SQS
- [ ] Know when to use REST vs GraphQL vs gRPC
- [ ] Know when to use microservices vs monolith

---

## Your Score

Count your checkmarks:

| Range | Assessment |
|-------|-----------|
| 90-100% | Ready for senior/staff interviews |
| 75-89% | Ready for most senior interviews, review gaps |
| 60-74% | Good foundation, 2-4 more weeks of practice |
| < 60% | Review weak weeks before interviewing |

**Your score**: ___ / 100+ items

**Top 3 gaps to address**:
1. _______________
2. _______________
3. _______________
