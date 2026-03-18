# Day 1: Scalability — Concepts Deep Dive

## 1. What Is Scalability?

Scalability is not just "handling more users." It's the ability of a system to handle increased **load** while maintaining acceptable **performance**.

The key word is "acceptable." You need to define what acceptable means before you can design for it:
- Response time under 200ms for 99% of requests?
- 99.9% uptime (8.7 hours downtime/year)?
- Support 1 million concurrent users?

These are called **Service Level Objectives (SLOs)**, and they drive every architectural decision.

---

## 2. Describing Load: Load Parameters

Before you can scale, you need to measure. Load is described by **load parameters**:

| Parameter | Example |
|-----------|---------|
| Requests per second (RPS) | 10,000 RPS on the API |
| Read/write ratio | 100:1 reads to writes (Twitter-like) |
| Active users | 1M concurrent users |
| Cache hit rate | 95% of reads served from cache |
| Data volume | 10TB of stored data |

> **DDIA Reference**: Chapter 1 discusses load parameters as the foundation for describing scalability. Kleppmann uses Twitter's fan-out problem as the canonical example.

---

## 3. Describing Performance: Latency vs. Throughput

These two are often confused. They're different things.

### Latency
**Definition**: The time it takes for a single request to complete.  
**Units**: milliseconds (ms)  
**Analogy**: How long it takes one car to drive from city A to city B.

```
Latency = Time from request sent → response received
```

### Throughput
**Definition**: The number of requests a system can handle per unit of time.  
**Units**: requests per second (RPS), transactions per second (TPS)  
**Analogy**: How many cars can pass through a highway per hour.

```
Throughput = Requests completed / Time period
```

### Why Both Matter
A system can have:
- **Low latency, low throughput**: Fast for one user, falls apart under load
- **High latency, high throughput**: Slow per request but handles many (batch processing)
- **Low latency, high throughput**: The goal (hard to achieve)

### Percentiles: The Right Way to Measure Latency

Never use average latency. Use percentiles:

```
p50  = 50th percentile = median (half of requests are faster than this)
p95  = 95th percentile (95% of requests are faster than this)
p99  = 99th percentile (the "tail latency")
p999 = 99.9th percentile (the "long tail")
```

Why does p99 matter? Because your slowest users are often your most valuable (they're doing the most). Amazon found that 100ms of extra latency cost them 1% in sales.

```
Example latency distribution:
p50:  45ms   ← Most users experience this
p95:  120ms  ← Some users experience this
p99:  350ms  ← A few users experience this
p999: 2000ms ← Rare but real
```

> **DDIA Reference**: Chapter 1, "Describing Performance" — Kleppmann explains why percentiles are superior to averages for latency measurement.

---

## 4. Vertical Scaling (Scale Up)

**Definition**: Making a single machine more powerful.

```
Before:          After:
┌──────────┐     ┌──────────────────┐
│ 4 CPU    │ →   │ 32 CPU           │
│ 16GB RAM │     │ 256GB RAM        │
│ 1TB SSD  │     │ 10TB NVMe        │
└──────────┘     └──────────────────┘
```

### Pros
- Simple — no code changes required
- No distributed systems complexity
- Strong consistency (single machine)
- Easy to reason about

### Cons
- Hard limit — you can't scale infinitely
- Expensive — high-end hardware costs disproportionately more
- Single point of failure — if it goes down, everything goes down
- Downtime required for upgrades

### When to Use Vertical Scaling
- Early stage startups (simplicity wins)
- Databases (distributed DBs are complex)
- When your bottleneck is CPU/RAM on a single process

---

## 5. Horizontal Scaling (Scale Out)

**Definition**: Adding more machines to distribute the load.

```
Before:          After:
┌──────────┐     ┌──────────┐  ┌──────────┐  ┌──────────┐
│ Server 1 │ →   │ Server 1 │  │ Server 2 │  │ Server 3 │
└──────────┘     └──────────┘  └──────────┘  └──────────┘
                      ↑              ↑              ↑
                 Load Balancer distributes traffic
```

### Pros
- Theoretically unlimited scale
- No single point of failure (with proper design)
- Can use commodity hardware
- Can scale incrementally

### Cons
- Requires stateless services (or shared state management)
- Distributed systems complexity
- Network latency between nodes
- Harder to reason about consistency

### The Stateless Requirement
For horizontal scaling to work, your servers must be **stateless** — they can't store user session data locally. Why? Because the next request might go to a different server.

```
BAD (stateful):
User → Server 1 (stores session) → User logs in
User → Server 2 (no session!) → User is logged out

GOOD (stateless):
User → Server 1 → Reads session from Redis → OK
User → Server 2 → Reads session from Redis → OK
```

---

## 6. The 3-Tier Architecture

The foundation of almost every web application:

```
┌─────────────────────────────────────────────────────┐
│                   PRESENTATION TIER                  │
│              (Browser, Mobile App)                   │
└─────────────────────┬───────────────────────────────┘
                      │ HTTP/HTTPS
┌─────────────────────▼───────────────────────────────┐
│                  APPLICATION TIER                    │
│         (Web Servers, API Servers, Business Logic)   │
│              [Horizontally Scalable]                 │
└─────────────────────┬───────────────────────────────┘
                      │ SQL/NoSQL queries
┌─────────────────────▼───────────────────────────────┐
│                    DATA TIER                         │
│              (Databases, File Storage)               │
│           [Harder to scale horizontally]             │
└─────────────────────────────────────────────────────┘
```

Each tier can be scaled independently. The application tier is easiest to scale horizontally (stateless). The data tier is hardest (state must be consistent).

---

## 7. Common Bottlenecks and How to Find Them

A bottleneck is the slowest part of your system. The system can only go as fast as its slowest component.

### The Bottleneck Hierarchy (most common first)
1. **Database** — Almost always the first bottleneck
2. **Network I/O** — Especially for chatty microservices
3. **CPU** — For compute-intensive operations
4. **Memory** — For large in-memory datasets
5. **Disk I/O** — For write-heavy workloads

### How to Find Bottlenecks
```
1. Measure everything (you can't optimize what you can't measure)
2. Profile under realistic load
3. Look for the resource at 100% utilization
4. Fix it, then find the next bottleneck
```

> **Real World**: When Instagram scaled from 0 to 1M users in 3 months, their bottleneck was PostgreSQL. They added read replicas, then sharding, then eventually moved some data to Cassandra.

---

## 8. Key Scalability Patterns

### Pattern 1: Caching
Store frequently accessed data in fast memory to avoid expensive recomputation or database queries.

### Pattern 2: Load Balancing
Distribute incoming requests across multiple servers.

### Pattern 3: Database Replication
Copy data to multiple servers for read scaling and fault tolerance.

### Pattern 4: Database Sharding
Split data across multiple databases to distribute write load.

### Pattern 5: Asynchronous Processing
Move slow operations (email sending, image processing) out of the request path.

We'll cover each of these in depth in the coming days.

---

## 9. Common Pitfalls

### Premature Optimization
> "Premature optimization is the root of all evil." — Donald Knuth

Don't design for 1 billion users on day one. Start simple, measure, then optimize. Most startups die from complexity, not from lack of scale.

### Ignoring the Network
Network calls are 1000x slower than memory access. Every time you add a network hop, you add latency.

```
Memory access:    ~100 nanoseconds
SSD read:         ~100 microseconds  (1,000x slower)
Network (LAN):    ~1 millisecond     (10,000x slower)
Network (WAN):    ~100 milliseconds  (1,000,000x slower)
```

### Not Measuring
You cannot optimize what you don't measure. Always instrument your system before optimizing.

---

## 10. Best Practices

1. **Design for failure** — Assume any component can fail at any time
2. **Measure before optimizing** — Use data, not intuition
3. **Start simple** — Add complexity only when needed
4. **Make services stateless** — Enables horizontal scaling
5. **Use async where possible** — Don't block on slow operations
6. **Cache aggressively** — But invalidate carefully
7. **Design for observability** — Logs, metrics, traces from day one

---

## References
- DDIA Chapter 1: Reliable, Scalable, and Maintainable Applications
- [The Twelve-Factor App](https://12factor.net/) — Principles for scalable, maintainable apps
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
