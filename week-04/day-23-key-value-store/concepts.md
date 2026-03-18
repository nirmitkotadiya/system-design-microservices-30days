# Key-Value Store: Deep Dive

## What Is a Key-Value Store?

A key-value store is the simplest form of a database: you store a value under a key, and retrieve it by that key. Think of it like a giant hash map that lives on disk and can span thousands of machines.

```
set("user:1001:name", "Alice")
get("user:1001:name")  → "Alice"
```

Simple interface. Incredibly complex internals.

Real-world examples:
- **Redis** — in-memory, sub-millisecond latency
- **DynamoDB** — AWS managed, massive scale
- **Cassandra** — wide-column, tunable consistency
- **RocksDB** — embedded, used inside other databases
- **etcd** — strongly consistent, used in Kubernetes

---

## The Core Problem: Storage Engine

The most important decision in a KV store is how data is stored on disk. Two dominant approaches:

### B-Tree (Used by PostgreSQL, MySQL, LMDB)

```
         [50]
        /    \
    [25]      [75]
   /    \    /    \
 [10] [30] [60] [90]
```

- Data stored in sorted tree pages (typically 4KB each)
- Updates happen **in-place** — find the page, modify it
- Great for **reads** (O(log n) lookups)
- Writes require random I/O — slow for write-heavy workloads
- WAL (Write-Ahead Log) for crash recovery

### LSM Tree (Log-Structured Merge Tree) — Used by Cassandra, RocksDB, LevelDB

This is the dominant approach for modern write-heavy KV stores.

**The key insight**: Sequential writes are 10-100x faster than random writes on both HDDs and SSDs. LSM trees turn all writes into sequential writes.

```
Write Path:
  Client Write
      ↓
  WAL (Write-Ahead Log) — sequential, for crash recovery
      ↓
  MemTable (in-memory sorted structure, e.g., red-black tree)
      ↓ (when MemTable is full, ~64MB)
  Flush to SSTable (Sorted String Table) on disk — Level 0
      ↓ (background compaction)
  Merge and compact into Level 1, 2, 3...
```

**SSTable (Sorted String Table)**:
- Immutable file of key-value pairs, sorted by key
- Has an index at the end for binary search
- Compressed for space efficiency

```
SSTable file layout:
┌─────────────────────────────────┐
│ data block 1 (sorted KV pairs)  │
│ data block 2                    │
│ ...                             │
│ index block (key → offset)      │
│ bloom filter                    │
│ footer (offsets to index/bloom) │
└─────────────────────────────────┘
```

**Read Path** (the expensive part):
1. Check MemTable (most recent writes)
2. Check Level 0 SSTables (newest first — may overlap)
3. Check Level 1, 2, 3... (no overlap within a level)
4. Return first match found

This is why LSM trees are **write-optimized but read-pessimized** compared to B-trees.

---

## Bloom Filters: The Read Optimization

A bloom filter answers: "Is this key definitely NOT in this SSTable?"

- Probabilistic data structure — no false negatives, small false positive rate
- Typically 10 bits per key → ~1% false positive rate
- Saves disk I/O by skipping SSTables that definitely don't have the key

```python
# Conceptual bloom filter
class BloomFilter:
    def __init__(self, size=1000, hash_count=3):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = [0] * size
    
    def add(self, key):
        for seed in range(self.hash_count):
            index = hash(f"{seed}:{key}") % self.size
            self.bit_array[index] = 1
    
    def might_contain(self, key):
        for seed in range(self.hash_count):
            index = hash(f"{seed}:{key}") % self.size
            if self.bit_array[index] == 0:
                return False  # Definitely not present
        return True  # Probably present (might be false positive)
```

---

## Compaction: The Background Tax

As SSTables accumulate, reads get slower (more files to check) and disk usage grows (deleted keys still take space). Compaction merges SSTables and removes deleted entries.

**Tombstones**: Deletes are written as special "tombstone" markers. The actual data is removed during compaction.

```
Before compaction (Level 0):
  SSTable 1: {a:1, b:2, c:3}
  SSTable 2: {b:99, d:4}  ← b was updated
  SSTable 3: {a:TOMBSTONE} ← a was deleted

After compaction (Level 1):
  SSTable merged: {b:99, c:3, d:4}  ← a removed, b deduplicated
```

**Compaction strategies**:
- **Size-tiered** (Cassandra default): Merge SSTables of similar size. Write-efficient, but space-amplification during compaction.
- **Leveled** (LevelDB/RocksDB default): Each level has a size limit. Better read performance, more write I/O.
- **FIFO**: Just delete oldest files. Good for time-series data.

---

## Distributed Architecture

A single-node KV store is just a library. The interesting part is distribution.

### Partitioning (Sharding)

Use consistent hashing to distribute keys across nodes:

```
Hash ring with 3 nodes:
     Node A (0-33%)
    /
Ring
    \
     Node B (33-66%) — Node C (66-100%)

key "user:1001" → hash → 45% → Node B
key "user:1002" → hash → 72% → Node C
```

Each node owns a range of the hash ring. Virtual nodes (vnodes) prevent hotspots.

### Replication

Each key is replicated to N nodes (typically N=3):

```
Replication factor = 3:
key "user:1001" → primary: Node B
                → replica 1: Node C  (next clockwise)
                → replica 2: Node A  (next clockwise)
```

**Quorum reads/writes** (DynamoDB/Cassandra model):
- W = write quorum (how many nodes must acknowledge write)
- R = read quorum (how many nodes must respond to read)
- N = replication factor
- For strong consistency: W + R > N (e.g., N=3, W=2, R=2)
- For availability: W=1, R=1 (eventual consistency)

```
Tunable consistency (Cassandra):
  CONSISTENCY ONE   → fastest, weakest
  CONSISTENCY QUORUM → balanced
  CONSISTENCY ALL   → slowest, strongest
```

### Conflict Resolution

When two nodes have different values for the same key (network partition), how do you resolve it?

**Last-Write-Wins (LWW)**: Use timestamps. Simple but can lose data if clocks drift.

**Vector Clocks**: Track causality across nodes.

```
Initial: {}
Node A writes: {A:1} → value="Alice"
Node B writes: {B:1} → value="Bob"  (concurrent with A)
Conflict! Both {A:1} and {B:1} are valid.
Client must resolve (or system uses LWW).

If A then B: {A:1} → {A:1, B:1} → no conflict, B wins
```

**CRDTs (Conflict-free Replicated Data Types)**: Data structures that can always be merged without conflicts. Used in Redis Cluster, Riak.

---

## Caching Layer: Redis Deep Dive

Redis is a KV store that lives entirely in memory (with optional persistence).

### Data Structures
Redis isn't just strings — it supports rich types:

```
String:  SET user:1:name "Alice"
Hash:    HSET user:1 name "Alice" age 30
List:    LPUSH queue "job1" "job2"
Set:     SADD tags "python" "redis"
Sorted Set: ZADD leaderboard 1500 "Alice"
Bitmap:  SETBIT active_users 1001 1
HyperLogLog: PFADD visitors "user1" "user2"
```

### Persistence Options

**RDB (Redis Database)**: Point-in-time snapshots
- `BGSAVE` forks the process, writes snapshot to disk
- Fast restarts, but can lose up to minutes of data

**AOF (Append-Only File)**: Log every write command
- `appendfsync always` — fsync after every write (slow but safe)
- `appendfsync everysec` — fsync every second (good balance)
- Larger files, slower restarts, but minimal data loss

**Hybrid**: Use both — RDB for fast restarts, AOF for durability.

### Eviction Policies

When memory is full, Redis must evict keys:

```
maxmemory-policy options:
  noeviction      → return error (default)
  allkeys-lru     → evict least recently used from all keys
  volatile-lru    → evict LRU from keys with TTL set
  allkeys-lfu     → evict least frequently used
  allkeys-random  → evict random key
  volatile-ttl    → evict key with shortest TTL
```

For a cache, `allkeys-lru` or `allkeys-lfu` is typical.

---

## DynamoDB Architecture

DynamoDB is Amazon's managed KV/document store, designed for massive scale.

### Key Design
- **Partition key** (hash key): Determines which partition stores the item
- **Sort key** (range key): Optional, enables range queries within a partition
- **Primary key** = partition key + optional sort key

```
Table: UserSessions
Partition key: user_id
Sort key: session_timestamp

user_id=1001, session_timestamp=2024-01-01T10:00 → {data...}
user_id=1001, session_timestamp=2024-01-01T11:00 → {data...}
user_id=1002, session_timestamp=2024-01-01T09:00 → {data...}
```

### Capacity Modes
- **Provisioned**: You specify RCU/WCU (read/write capacity units). Cheaper, but requires capacity planning.
- **On-demand**: Pay per request. More expensive but no capacity planning.

### DynamoDB Streams
Every write generates a stream event — useful for event-driven architectures, replication, and cache invalidation.

---

## Comparison Table

| Feature | Redis | DynamoDB | Cassandra | etcd |
|---------|-------|----------|-----------|------|
| Storage | In-memory | Disk (SSD) | Disk | Disk |
| Consistency | Strong (single node) | Eventual/Strong | Tunable | Strong |
| Latency | <1ms | 1-10ms | 1-10ms | 1-10ms |
| Scale | Vertical + Cluster | Unlimited (managed) | Horizontal | Small clusters |
| Use case | Cache, sessions | General purpose | Time-series, IoT | Config, coordination |
| CAP | CP (cluster) | AP (default) | AP (tunable) | CP |

---

## DDIA Reference

From *Designing Data-Intensive Applications* (Kleppmann):
- Chapter 3: "Storage and Retrieval" — LSM trees vs B-trees, SSTables
- Chapter 5: "Replication" — leader-follower, multi-leader, leaderless
- Chapter 6: "Partitioning" — consistent hashing, secondary indexes
- Chapter 7: "Transactions" — ACID in distributed systems

Key quote: *"An application developer needs to understand the internals of storage engines to select the right tool and tune it appropriately."*

---

## Interview Questions

1. "How does Redis handle persistence?" → RDB snapshots + AOF log, hybrid mode
2. "What's the difference between Redis and Memcached?" → Redis has richer data types, persistence, pub/sub, clustering; Memcached is simpler, multi-threaded
3. "How does DynamoDB achieve single-digit millisecond latency?" → SSDs, in-memory caching (DAX), consistent hashing, no joins
4. "When would you choose Cassandra over DynamoDB?" → Multi-region active-active, open source requirement, time-series data
5. "What is a hot partition and how do you fix it?" → One partition key gets disproportionate traffic; fix with key sharding (add random suffix), caching, or redesigning the key schema

---

## Common Pitfalls

**Hot keys**: One key gets 90% of traffic. Solution: cache at application layer, shard the key.

**Large values**: Storing 10MB blobs in Redis wastes memory and causes latency spikes. Store in S3, keep reference in Redis.

**TTL stampede**: Many keys expire at the same time, causing a thundering herd to the database. Solution: add jitter to TTLs.

**Forgetting about memory**: Redis is in-memory. A 100GB dataset needs a 100GB+ instance. Plan accordingly.

**Not setting maxmemory**: Redis will use all available RAM and the OS will start swapping — catastrophic for performance.
