# Day 23 Exercises: Key-Value Store

## Exercise 1: Conceptual Understanding

Answer these questions in your own words (no peeking at concepts.md):

1. What is the fundamental difference between an LSM tree and a B-tree storage engine? When would you choose each?

2. Explain what a tombstone is in an LSM tree. Why can't you just delete the data immediately?

3. A bloom filter says a key "might be present" in an SSTable. What does this mean, and what are the implications for read performance?

4. You have N=3 replicas. A client writes with W=1 and reads with R=1. Is this strongly consistent? What's the risk?

5. What is a vector clock, and why is it more accurate than timestamps for conflict resolution?

**Self-check**: Can you explain each answer to a rubber duck without hesitation?

---

## Exercise 2: Implement a Basic LSM Tree

Build a simplified LSM tree that demonstrates the core concepts:

```python
# Starter code — complete the implementation
import os
import json
import time
from sortedcontainers import SortedDict  # pip install sortedcontainers

class WAL:
    """Write-Ahead Log for crash recovery"""
    def __init__(self, path):
        self.path = path
    
    def append(self, operation, key, value=None):
        # TODO: Write operation to WAL file
        # Format: {"op": "set/delete", "key": key, "value": value, "ts": timestamp}
        pass
    
    def recover(self):
        # TODO: Read WAL and return list of operations
        pass

class MemTable:
    """In-memory sorted structure"""
    def __init__(self, max_size=1000):
        self.data = SortedDict()
        self.max_size = max_size
        self.size = 0
    
    def set(self, key, value):
        # TODO: Insert key-value pair
        pass
    
    def get(self, key):
        # TODO: Return value or None
        pass
    
    def delete(self, key):
        # TODO: Insert tombstone marker
        pass
    
    def is_full(self):
        return self.size >= self.max_size
    
    def flush_to_sstable(self, path):
        # TODO: Write sorted data to SSTable file
        # Return SSTable object
        pass

class SSTable:
    """Immutable sorted file on disk"""
    def __init__(self, path):
        self.path = path
        self.index = {}  # key → file offset
        self._build_index()
    
    def _build_index(self):
        # TODO: Read file and build in-memory index
        pass
    
    def get(self, key):
        # TODO: Use index to find key in file
        pass

class SimpleLSMTree:
    def __init__(self, data_dir="./lsm_data"):
        os.makedirs(data_dir, exist_ok=True)
        self.data_dir = data_dir
        self.memtable = MemTable()
        self.sstables = []  # List of SSTable objects, newest first
        self.wal = WAL(os.path.join(data_dir, "wal.log"))
    
    def set(self, key, value):
        self.wal.append("set", key, value)
        self.memtable.set(key, value)
        if self.memtable.is_full():
            self._flush_memtable()
    
    def get(self, key):
        # Check memtable first, then SSTables newest to oldest
        # TODO: Implement read path
        pass
    
    def delete(self, key):
        self.wal.append("delete", key)
        self.memtable.delete(key)
    
    def _flush_memtable(self):
        # TODO: Flush memtable to SSTable, reset memtable
        pass

# Test your implementation
if __name__ == "__main__":
    db = SimpleLSMTree()
    db.set("name", "Alice")
    db.set("age", "30")
    db.set("city", "NYC")
    print(db.get("name"))   # Alice
    db.delete("city")
    print(db.get("city"))   # None
    db.set("name", "Bob")   # Update
    print(db.get("name"))   # Bob
```

**Hints**:
- Use `json.dumps()` for serialization
- Tombstones can be represented as `None` or a special sentinel value
- The WAL file should be append-only

---

## Exercise 3: Design a Distributed KV Store

Design a distributed KV store for the following requirements:

**Requirements**:
- 10 billion keys, average value size 1KB
- 1 million reads/second, 100K writes/second
- 99.9% availability (< 8.7 hours downtime/year)
- Read latency p99 < 10ms
- Eventual consistency is acceptable for most reads
- Strong consistency needed for financial transactions

**Your design should address**:

1. **Capacity planning**:
   - How many nodes do you need?
   - What's the replication factor?
   - How much storage per node?

2. **Partitioning strategy**:
   - How do you distribute 10B keys?
   - How do you handle hot keys?
   - What happens when you add/remove nodes?

3. **Consistency model**:
   - What are your W, R, N values for normal operations?
   - How do you handle the financial transaction use case?
   - What happens during a network partition?

4. **Architecture diagram** (use Mermaid or ASCII):
   ```
   Draw your architecture here
   ```

5. **Technology choice**: Would you use DynamoDB, Cassandra, or build custom? Why?

---

## Exercise 4: Redis Design Patterns

You're building a social media platform. Design the Redis data model for:

**Feature 1: User Sessions**
- Store session data for 100M active users
- Sessions expire after 30 minutes of inactivity
- Session data: user_id, permissions, last_active, device_info

**Feature 2: News Feed Cache**
- Cache the last 100 posts for each user's feed
- New posts should appear at the top
- Support pagination (get posts 20-40)

**Feature 3: Rate Limiting**
- Limit API calls to 100 requests per minute per user
- Must be accurate (not approximate)
- Must work across multiple API servers

**Feature 4: Leaderboard**
- Real-time leaderboard for a game
- Support: get top 100 players, get a player's rank, update score
- 10M players total

For each feature, specify:
- Redis data type to use
- Key naming convention
- TTL strategy
- Estimated memory usage

**Hints**:
- Sessions → Hash with TTL
- Feed → Sorted Set (score = timestamp)
- Rate limiting → Sliding window with Sorted Set or fixed window with String
- Leaderboard → Sorted Set (score = game score)

---

## Exercise 5: The Hot Key Problem

**Scenario**: You're running a KV store for a major e-commerce platform. During a flash sale, a single product (key: `product:iphone15:stock`) receives 500,000 reads/second and 10,000 writes/second. Your Redis instance can handle ~100,000 ops/second.

**Part A**: Identify all the problems this creates:
- What happens to the Redis node hosting this key?
- What happens to other keys on the same node?
- What happens to the application?

**Part B**: Design a solution that handles this load. Consider:
- Local in-process caching
- Key sharding (splitting one key into many)
- Read replicas
- Probabilistic early expiration

**Part C**: Implement key sharding in Python:

```python
import redis
import random

class ShardedCounter:
    """
    Distributes a single logical counter across N shards
    to handle high write throughput.
    """
    def __init__(self, redis_client, key_prefix, num_shards=10):
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.num_shards = num_shards
    
    def increment(self, amount=1):
        # TODO: Pick a random shard and increment it
        pass
    
    def get_total(self):
        # TODO: Sum all shards to get total count
        pass
    
    def decrement(self, amount=1):
        # TODO: Pick a random shard and decrement
        # Challenge: What if a shard goes negative?
        pass

# Test
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
counter = ShardedCounter(r, "product:iphone15:stock", num_shards=10)
counter.increment(1000)  # Initial stock
print(counter.get_total())  # 1000
```

**Part D**: What are the tradeoffs of key sharding? When does it break down?

---

## Hints

**Exercise 2**:
- Start with just the MemTable and get reads/writes working in memory
- Add SSTable persistence next
- WAL is the last piece — add it for crash recovery

**Exercise 3**:
- 10B keys × 1KB = ~10TB of data
- With 3x replication = 30TB total
- At 2TB per node = 15 nodes minimum (add headroom → 20 nodes)
- 1M reads/second ÷ 20 nodes = 50K reads/node (very manageable)

**Exercise 4**:
- For rate limiting, the sliding window approach: use a Sorted Set where score = timestamp, members = request IDs. Count members in the last 60 seconds.
- For leaderboard: `ZADD leaderboard <score> <player_id>`, `ZREVRANK leaderboard <player_id>` for rank

**Exercise 5**:
- Key sharding for reads: replicate the key to N copies (`product:iphone15:stock:0` through `:9`), read from random shard
- Key sharding for writes is harder — you need to aggregate. Use a background job to consolidate.

---

## Self-Assessment Checklist

- [ ] I can explain LSM trees without looking at notes
- [ ] I understand why bloom filters are useful
- [ ] I can design a distributed KV store from scratch
- [ ] I know the right Redis data type for common use cases
- [ ] I can identify and solve the hot key problem
- [ ] I understand the CAP tradeoffs in KV stores
- [ ] I could answer "Design a KV store" in a 45-minute interview
