# Week 2 Review: Distributed Systems Fundamentals

## What We Covered This Week

Week 2 took you from the basics of scalability into the deep end of distributed systems. These are the concepts that separate junior engineers from senior ones in system design interviews.

---

## CAP Theorem — The Fundamental Constraint

Every distributed system must choose two of three guarantees when a network partition occurs:

```
         Consistency
              △
             / \
            /   \
           /     \
          /  CA   \
         /  (not   \
        /  possible \
       /  in dist.  \
      ▽_______________▽
  Availability    Partition
                 Tolerance

Real choices:
  CP: Consistent + Partition Tolerant (HBase, ZooKeeper, etcd)
  AP: Available + Partition Tolerant (Cassandra, DynamoDB, CouchDB)
  CA: Consistent + Available (single-node RDBMS — not distributed)
```

**The key insight**: Network partitions WILL happen. You can't avoid them. So the real choice is between consistency and availability during a partition.

**Interview framing**: "Given that partitions are inevitable, do you need your system to return potentially stale data (AP) or refuse to serve requests until consistency is restored (CP)?"

---

## Replication — Keeping Copies in Sync

Three models, each with different tradeoffs:

### Leader-Follower (Master-Replica)
```
Writes → Leader → replicate → Follower 1
                            → Follower 2
Reads  → Any follower (eventual) or leader (strong)
```
- Simple, well-understood
- Leader is a bottleneck and single point of failure
- Used by: PostgreSQL, MySQL, MongoDB

### Multi-Leader
```
Leader A ←→ Leader B
   ↓              ↓
Followers A   Followers B
```
- Better write throughput, multi-datacenter support
- Conflict resolution is hard (who wins when both leaders write the same key?)
- Used by: CouchDB, some MySQL configurations

### Leaderless (Dynamo-style)
```
Client → writes to W of N nodes
Client → reads from R of N nodes
Strong consistency when W + R > N
```
- No single point of failure
- Complex conflict resolution (vector clocks, LWW)
- Used by: Cassandra, DynamoDB, Riak

---

## Sharding — Splitting Data Across Nodes

When one machine can't hold all your data, you shard it.

### Range-Based Sharding
```
Shard 1: keys A-F
Shard 2: keys G-M
Shard 3: keys N-Z
```
- Good for range queries
- Risk: hotspots if data isn't uniformly distributed

### Hash-Based Sharding
```
shard = hash(key) % num_shards
```
- Even distribution
- Range queries require scatter-gather across all shards
- Problem: adding/removing shards requires rehashing everything

### Consistent Hashing
```
Hash ring: nodes placed at positions on a circle
Key → hash → find next node clockwise
```
- Adding/removing nodes only affects neighboring keys
- Virtual nodes ensure even distribution
- Used by: Cassandra, DynamoDB, Redis Cluster

---

## Consistent Hashing — The Elegant Solution

The problem with `hash(key) % N`: when N changes, almost every key moves.

Consistent hashing solution: keys and nodes are both placed on a ring. A key belongs to the first node clockwise from its position.

```
When you add a node:
  Only keys between the new node and its predecessor move.
  ~1/N of keys move (instead of almost all of them).

When you remove a node:
  Only that node's keys move to the next node.
  ~1/N of keys move.
```

**Virtual nodes**: Each physical node gets 150+ positions on the ring. This ensures even distribution even with heterogeneous hardware.

---

## Message Queues — Decoupling Services

Message queues let producers and consumers operate independently.

```
Without queue:
  Service A → HTTP → Service B
  If B is down: A fails
  If B is slow: A blocks

With queue:
  Service A → Queue → Service B
  If B is down: messages accumulate, B processes when back
  If B is slow: A continues, queue buffers
```

**Key concepts**:
- **At-most-once**: Message delivered 0 or 1 times (can lose messages)
- **At-least-once**: Message delivered 1+ times (can duplicate)
- **Exactly-once**: Message delivered exactly once (expensive, requires coordination)

**When to use queues**:
- Async processing (email sending, image resizing)
- Load leveling (absorb traffic spikes)
- Decoupling services
- Fan-out (one event → many consumers)

---

## Rate Limiting — Protecting Your Services

Four main algorithms:

| Algorithm | Memory | Accuracy | Burst Handling |
|-----------|--------|----------|----------------|
| Fixed Window | O(1) | Low (boundary bursts) | Poor |
| Sliding Window Log | O(requests) | High | Good |
| Sliding Window Counter | O(1) | Good | Good |
| Token Bucket | O(1) | Good | Excellent |
| Leaky Bucket | O(1) | Good | None (smooths) |

**Token bucket** is the most common in practice (used by AWS, Stripe):
- Tokens added at rate R per second
- Each request consumes 1 token
- Bucket capacity = max burst size
- If no tokens: reject or queue

---

## The Big Picture: How It All Connects

```
User Request
     ↓
Rate Limiter (protect from abuse)
     ↓
Load Balancer (distribute traffic)
     ↓
Application Servers
     ↓
Cache (Redis) ← check here first
     ↓ (cache miss)
Database (sharded, replicated)
     ↓
Message Queue (async work)
     ↓
Background Workers
```

Each layer in this stack uses concepts from this week:
- Rate limiter: token bucket algorithm
- Load balancer: consistent hashing for session affinity
- Cache: replication for HA
- Database: sharding + replication
- Message queue: at-least-once delivery

---

## DDIA Connections

- Chapter 5: Replication — all three models in depth
- Chapter 6: Partitioning — sharding strategies, consistent hashing
- Chapter 7: Transactions — how to maintain consistency across shards
- Chapter 9: Consistency and Consensus — CAP theorem, linearizability

---

## Interview Cheat Sheet

**"How do you scale a database?"**
→ Read replicas first, then sharding, then consider NoSQL

**"What happens during a network partition?"**
→ CAP theorem: choose CP (reject requests) or AP (serve stale data)

**"How does Cassandra achieve high availability?"**
→ Leaderless replication, tunable consistency (W+R>N for strong)

**"Why is consistent hashing better than modulo hashing?"**
→ Only ~1/N keys move when adding/removing nodes vs. almost all keys

**"When would you use a message queue?"**
→ Async processing, decoupling, load leveling, fan-out patterns
