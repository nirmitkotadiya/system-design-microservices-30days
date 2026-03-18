# Day 11: Exercises — Consistent Hashing

---

## Exercise 1: Basic Comprehension (15 minutes)

1. You have 10 nodes using regular hash sharding (`hash(key) % 10`). You add an 11th node. Approximately what percentage of keys need to move?

2. With consistent hashing and 10 nodes, you add an 11th node. Approximately what percentage of keys need to move?

3. What problem do virtual nodes solve? Why does Cassandra use 256 virtual nodes per physical node?

4. With a replication factor of 3 and consistent hashing, how many nodes store each key? What happens when one of those nodes fails?

5. A CDN uses consistent hashing to distribute cached content across edge nodes. A new edge node is added in Tokyo. Which cached content moves to the Tokyo node?

---

## Exercise 2: Manual Ring Traversal (20 minutes)

Given this hash ring with 3 nodes:
```
Ring (0 to 100):
  Node A: position 20
  Node B: position 50
  Node C: position 80
```

For each key, determine which node it maps to:
1. key="user:1" → hash = 10
2. key="user:2" → hash = 35
3. key="user:3" → hash = 65
4. key="user:4" → hash = 90
5. key="user:5" → hash = 15

Now add Node D at position 40. Which keys move? From which node to which node?

---

## Exercise 3: Implement Consistent Hashing (35 minutes)

Using the implementation in `concepts.md` as a reference, implement a consistent hash ring from scratch:

```python
# Your implementation here
class ConsistentHashRing:
    def __init__(self, virtual_nodes: int = 150):
        pass

    def add_node(self, node: str):
        pass

    def remove_node(self, node: str):
        pass

    def get_node(self, key: str) -> str:
        pass
```

Test your implementation:
```python
ring = ConsistentHashRing(virtual_nodes=150)
ring.add_node("server-1")
ring.add_node("server-2")
ring.add_node("server-3")

# Test distribution
from collections import Counter
distribution = Counter()
for i in range(10000):
    node = ring.get_node(f"key:{i}")
    distribution[node] += 1

print(distribution)
# Should be roughly even: ~3333 keys per node

# Test that adding a node moves minimal keys
assignments_before = {f"key:{i}": ring.get_node(f"key:{i}") for i in range(10000)}
ring.add_node("server-4")
assignments_after = {f"key:{i}": ring.get_node(f"key:{i}") for i in range(10000)}

moved = sum(1 for k in assignments_before if assignments_before[k] != assignments_after[k])
print(f"Keys moved: {moved} / 10000 ({moved/100:.1f}%)")
# Should be ~25% (1/4 of keys move to the new node)
```

---

## Exercise 4: Virtual Node Distribution Analysis (20 minutes)

Run this analysis to understand how virtual nodes affect distribution:

```python
import hashlib
import bisect
from collections import defaultdict

def analyze_distribution(num_nodes: int, virtual_nodes_per_node: int, num_keys: int = 100000):
    """Analyze how evenly keys are distributed across nodes."""
    ring = {}
    sorted_keys = []

    for node_id in range(num_nodes):
        for vnode in range(virtual_nodes_per_node):
            key = f"node-{node_id}:vnode:{vnode}"
            pos = int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**32)
            ring[pos] = f"node-{node_id}"
            bisect.insort(sorted_keys, pos)

    # Assign keys to nodes
    distribution = defaultdict(int)
    for i in range(num_keys):
        key_hash = int(hashlib.md5(f"key:{i}".encode()).hexdigest(), 16) % (2**32)
        idx = bisect.bisect_right(sorted_keys, key_hash) % len(sorted_keys)
        node = ring[sorted_keys[idx]]
        distribution[node] += 1

    counts = list(distribution.values())
    avg = sum(counts) / len(counts)
    max_deviation = max(abs(c - avg) / avg * 100 for c in counts)
    return max_deviation

# Compare different virtual node counts
for vnodes in [1, 10, 50, 150, 500]:
    deviation = analyze_distribution(num_nodes=5, virtual_nodes_per_node=vnodes)
    print(f"Virtual nodes: {vnodes:4d} → Max deviation from average: {deviation:.1f}%")
```

What do you observe? How does the number of virtual nodes affect distribution evenness?

---

## Exercise 5: Challenge — Design a Distributed Cache with Consistent Hashing (30 minutes)

### Scenario

You're building a distributed cache (like Memcached) with:
- 10 cache nodes
- 1TB total cache capacity
- 500,000 cache operations/second
- Nodes can be added/removed without downtime

**Design**:

1. **Key routing**: How does a client know which cache node to contact for a given key?

2. **Node failure**: A cache node goes down. What happens to the keys it was responsible for? How do you handle cache misses for those keys?

3. **Adding a node**: You add an 11th cache node. What happens to the cache hit rate during the transition? How do you minimize the impact?

4. **Replication**: Should you replicate cache data? What are the tradeoffs?

5. **Client-side vs. proxy**: Should the consistent hashing logic live in the client library or in a proxy server? What are the tradeoffs?

---

## Hints

**Exercise 2**: Remember, keys go to the next node clockwise. If a key's hash is 90 and the nodes are at 20, 50, 80, the next clockwise from 90 wraps around to Node A at 20.

**Exercise 3**: Use `bisect.bisect_right` to find the insertion point, then take modulo to wrap around.

**Exercise 5, Q3**: When a new node is added, some keys that were on other nodes now map to the new node. Those keys will be cache misses until they're fetched from the source and cached on the new node.

---

## Self-Assessment Checklist

- [ ] I understand why regular hashing fails when nodes change
- [ ] I can manually trace key assignments on a hash ring
- [ ] I can implement consistent hashing from scratch
- [ ] I understand how virtual nodes improve distribution
- [ ] I can describe how consistent hashing is used in Cassandra
- [ ] I can design a distributed cache using consistent hashing
