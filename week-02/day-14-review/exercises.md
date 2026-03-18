# Day 14: Mini-Design Challenge — Distributed Cache

Set a 45-minute timer. Design a distributed cache like Memcached or Redis Cluster.

---

## The Problem

Design a distributed in-memory cache with the following requirements:

**Functional Requirements**:
- `set(key, value, ttl)` — Store a key-value pair with expiration
- `get(key)` — Retrieve a value by key
- `delete(key)` — Remove a key
- `get_many(keys)` — Batch get multiple keys

**Non-Functional Requirements**:
- 1 million operations per second
- p99 latency < 1ms
- 10TB total cache capacity
- Availability: 99.99%
- Horizontal scalability (add nodes without downtime)

---

## Step 1: Estimate Scale (5 minutes)

1. If each cache entry is ~1KB on average, how many entries fit in 10TB?
2. At 1M ops/second, how many ops per node if you have 100 nodes?
3. What's the network bandwidth requirement? (1M ops × 1KB = ?)

---

## Step 2: High-Level Architecture (10 minutes)

Draw the architecture showing:
- Client libraries
- Cache nodes
- How clients find the right node for a key
- Replication topology

---

## Step 3: Key Distribution (10 minutes)

How do you distribute keys across 100 cache nodes?

1. Why is consistent hashing better than `hash(key) % 100`?
2. How many virtual nodes per physical node?
3. What happens when you add a 101st node?
4. What happens when a node fails?

---

## Step 4: Replication (10 minutes)

Should you replicate cache data?

1. What's the tradeoff between replication factor 1 (no replication) and 3?
2. If a node fails with no replication, what happens to cache hit rate?
3. If you replicate, do you use synchronous or asynchronous replication?
4. How do you handle write conflicts in a replicated cache?

---

## Step 5: Eviction Policy (5 minutes)

Your cache is full. What do you evict?

1. LRU vs. LFU — which is better for a general-purpose cache?
2. How do you implement LRU efficiently? (Hint: doubly linked list + hash map)
3. Should TTL expiration be eager (check on every access) or lazy (background job)?

---

## Step 6: Consistency Model (5 minutes)

What consistency guarantees does your cache provide?

1. If two clients write the same key simultaneously, what happens?
2. After a write, is the new value immediately visible to all clients?
3. What's your CAP classification? (CP or AP?)

---

## Reference Solution Outline

**Architecture**:
- Client library with consistent hashing (no proxy needed)
- 100 cache nodes, each with 100GB RAM
- Replication factor: 2 (primary + 1 replica)
- Asynchronous replication (low latency writes)

**Key distribution**: Consistent hashing with 150 virtual nodes/physical node

**Eviction**: LRU with lazy TTL expiration

**Consistency**: AP — available during partitions, eventual consistency

**CAP reasoning**: Cache data is not source of truth. Stale data is acceptable. Availability is more important than consistency.

---

## Week 2 Final Checklist

- [ ] CAP theorem: can classify any database and explain the tradeoff
- [ ] Replication: can design HA setup with appropriate sync/async choice
- [ ] Sharding: can choose shard key and explain hot shard prevention
- [ ] Consistent hashing: can explain and implement from scratch
- [ ] Message queues: can design event-driven architecture
- [ ] Rate limiting: can implement sliding window counter
- [ ] Distributed cache: can design end-to-end
