# Day 11: Consistent Hashing — Concepts Deep Dive

## 1. The Problem with Regular Hashing

With regular hash-based sharding:
```python
shard = hash(key) % num_shards
```

When you add a shard:
```
Before (4 shards): key → hash(key) % 4
After (5 shards):  key → hash(key) % 5

key="user:123": hash=456789
  Before: 456789 % 4 = 1 → Shard 1
  After:  456789 % 5 = 4 → Shard 4  ← MOVED!

key="user:456": hash=789012
  Before: 789012 % 4 = 0 → Shard 0
  After:  789012 % 5 = 2 → Shard 2  ← MOVED!
```

**Result**: ~80% of all keys need to move when adding one shard. This is catastrophic for a production system.

---

## 2. The Hash Ring

Consistent hashing places both nodes and keys on a circular ring (hash space 0 to 2^32).

```
                    0
                  ┌───┐
              330 │   │ 30
                  │   │
          300 ────┤   ├──── 60
                  │   │
              270 │   │ 90
                  └───┘
                   180

Nodes placed on ring:
  Node A: hash("NodeA") = 45  → position 45
  Node B: hash("NodeB") = 150 → position 150
  Node C: hash("NodeC") = 270 → position 270

Keys assigned to the next node clockwise:
  key="user:1": hash = 30  → next node clockwise = Node A (45)
  key="user:2": hash = 100 → next node clockwise = Node B (150)
  key="user:3": hash = 200 → next node clockwise = Node C (270)
  key="user:4": hash = 300 → next node clockwise = Node A (45, wraps around)
```

### Adding a Node

```
Add Node D at position 200:

Before:
  key="user:3": hash=200 → Node C (270)

After:
  key="user:3": hash=200 → Node D (200)  ← Only keys between 150 and 200 move!

Only keys in the range (150, 200] need to move from Node C to Node D.
All other keys are unaffected.
```

### Removing a Node

```
Remove Node B (position 150):

Before:
  key="user:2": hash=100 → Node B (150)

After:
  key="user:2": hash=100 → Node C (270)  ← Only keys that were on Node B move!

Only keys that were assigned to Node B move to Node C.
All other keys are unaffected.
```

**Key insight**: When adding/removing a node, only K/N keys need to move (where K = total keys, N = number of nodes). With 1M keys and 10 nodes, adding a node moves ~100K keys instead of ~900K.

---

## 3. The Problem with Basic Consistent Hashing

With only a few nodes, the distribution can be uneven:

```
Ring positions:
  Node A: 45
  Node B: 150
  Node C: 270

Ranges:
  Node A handles: 270 → 45 (range of 135 units)
  Node B handles: 45 → 150 (range of 105 units)
  Node C handles: 150 → 270 (range of 120 units)

Node A handles 36% of the ring, Node B handles 28%, Node C handles 32%.
Not perfectly even!
```

With random node placement, some nodes might get much more data than others.

---

## 4. Virtual Nodes (VNodes)

Instead of placing each physical node once on the ring, place it many times (as "virtual nodes").

```
Physical nodes: A, B, C
Virtual nodes per physical node: 3

Ring positions:
  A1: 15,  A2: 120, A3: 280
  B1: 45,  B2: 180, B3: 320
  C1: 75,  C2: 210, C3: 350

Now each physical node handles multiple small ranges instead of one large range.
Distribution is much more even.
```

**Benefits of virtual nodes**:
1. **Even distribution**: More virtual nodes = more uniform distribution
2. **Heterogeneous hardware**: Powerful nodes get more virtual nodes
3. **Smooth rebalancing**: When a node is added, it takes a small portion from many nodes

**Cassandra uses 256 virtual nodes per physical node by default.**

---

## 5. Consistent Hashing with Replication

For fault tolerance, each key is stored on multiple nodes.

```
Replication factor = 3:
  key="user:1": hash=30
  Primary: Node A (45) — next clockwise
  Replica 1: Node B (150) — second next clockwise
  Replica 2: Node C (270) — third next clockwise
```

This is exactly how Cassandra works:
- Data is replicated to the next N nodes clockwise on the ring
- If a node fails, the next node in the ring serves the data

---

## 6. Real-World Applications

### Cassandra
- Uses consistent hashing with virtual nodes
- Each node is responsible for a range of the hash ring
- Replication factor determines how many nodes store each key
- Gossip protocol keeps all nodes aware of the ring topology

### Amazon DynamoDB
- Uses consistent hashing internally
- Automatically rebalances as nodes are added/removed
- Transparent to the user

### CDN Cache Distribution
- CDN edge nodes use consistent hashing to distribute cached content
- When an edge node is added, only a fraction of cached content needs to move

### Load Balancers
- Some load balancers use consistent hashing for session affinity
- Same client always goes to same server (without sticky session cookies)

---

## 7. Implementation

```python
import hashlib
import bisect
from typing import Optional

class ConsistentHashRing:
    """
    Consistent hash ring with virtual nodes.
    """

    def __init__(self, nodes: list[str] = None, virtual_nodes: int = 150):
        self.virtual_nodes = virtual_nodes
        self.ring: dict[int, str] = {}  # position → node name
        self.sorted_keys: list[int] = []  # sorted positions

        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key: str) -> int:
        """Hash a key to a position on the ring (0 to 2^32)."""
        return int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**32)

    def add_node(self, node: str):
        """Add a node to the ring with virtual nodes."""
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:vnode:{i}"
            position = self._hash(virtual_key)
            self.ring[position] = node
            bisect.insort(self.sorted_keys, position)

    def remove_node(self, node: str):
        """Remove a node and all its virtual nodes from the ring."""
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:vnode:{i}"
            position = self._hash(virtual_key)
            if position in self.ring:
                del self.ring[position]
                self.sorted_keys.remove(position)

    def get_node(self, key: str) -> Optional[str]:
        """Get the node responsible for a given key."""
        if not self.ring:
            return None

        position = self._hash(key)

        # Find the first node clockwise from this position
        idx = bisect.bisect_right(self.sorted_keys, position)

        # Wrap around if we're past the last node
        if idx == len(self.sorted_keys):
            idx = 0

        return self.ring[self.sorted_keys[idx]]

    def get_nodes(self, key: str, count: int) -> list[str]:
        """Get the N nodes responsible for a key (for replication)."""
        if not self.ring:
            return []

        position = self._hash(key)
        idx = bisect.bisect_right(self.sorted_keys, position)

        nodes = []
        seen = set()

        for i in range(len(self.sorted_keys)):
            node_idx = (idx + i) % len(self.sorted_keys)
            node = self.ring[self.sorted_keys[node_idx]]
            if node not in seen:
                nodes.append(node)
                seen.add(node)
            if len(nodes) == count:
                break

        return nodes
```

---

## References
- [Consistent Hashing Original Paper](https://www.cs.princeton.edu/courses/archive/fall09/cos518/papers/chash.pdf) — Karger et al., 1997
- DDIA Chapter 6: Partitioning (section on consistent hashing)
- [Cassandra Architecture: Consistent Hashing](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html)
