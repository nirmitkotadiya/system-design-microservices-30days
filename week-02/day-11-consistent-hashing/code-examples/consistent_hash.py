"""
Consistent Hashing Implementation — Day 11

Full implementation with virtual nodes, replication support,
and distribution analysis.

Run: python consistent_hash.py
"""

import hashlib
import bisect
from collections import defaultdict, Counter
from typing import Optional


class ConsistentHashRing:
    """
    Consistent hash ring with virtual nodes and replication support.

    Uses MD5 hashing to place nodes and keys on a circular ring (0 to 2^32).
    Virtual nodes ensure even distribution even with few physical nodes.
    """

    def __init__(self, virtual_nodes: int = 150):
        """
        Args:
            virtual_nodes: Number of virtual nodes per physical node.
                           Higher = more even distribution, more memory.
                           Cassandra default: 256
        """
        self.virtual_nodes = virtual_nodes
        self.ring: dict[int, str] = {}       # position → physical node name
        self.sorted_keys: list[int] = []     # sorted ring positions
        self.nodes: set[str] = set()         # set of physical nodes

    def _hash(self, key: str) -> int:
        """Hash a string to a position on the ring (0 to 2^32 - 1)."""
        return int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**32)

    def add_node(self, node: str):
        """
        Add a physical node to the ring.
        Creates `virtual_nodes` virtual nodes for even distribution.
        """
        if node in self.nodes:
            return

        self.nodes.add(node)
        for i in range(self.virtual_nodes):
            # Each virtual node gets a unique position
            virtual_key = f"{node}:vnode:{i}"
            position = self._hash(virtual_key)
            self.ring[position] = node
            bisect.insort(self.sorted_keys, position)

    def remove_node(self, node: str):
        """
        Remove a physical node and all its virtual nodes from the ring.
        Keys previously assigned to this node will move to the next node.
        """
        if node not in self.nodes:
            return

        self.nodes.discard(node)
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:vnode:{i}"
            position = self._hash(virtual_key)
            if position in self.ring:
                del self.ring[position]
                idx = bisect.bisect_left(self.sorted_keys, position)
                if idx < len(self.sorted_keys) and self.sorted_keys[idx] == position:
                    self.sorted_keys.pop(idx)

    def get_node(self, key: str) -> Optional[str]:
        """
        Get the primary node responsible for a given key.
        Returns None if the ring is empty.
        """
        if not self.ring:
            return None

        position = self._hash(key)
        idx = bisect.bisect_right(self.sorted_keys, position)

        # Wrap around to the first node if past the end
        if idx == len(self.sorted_keys):
            idx = 0

        return self.ring[self.sorted_keys[idx]]

    def get_nodes(self, key: str, count: int) -> list[str]:
        """
        Get the N distinct physical nodes responsible for a key.
        Used for replication: primary + N-1 replicas.

        Args:
            key: The key to look up
            count: Number of distinct nodes to return (replication factor)
        """
        if not self.ring:
            return []

        position = self._hash(key)
        idx = bisect.bisect_right(self.sorted_keys, position)

        nodes = []
        seen_nodes = set()

        for i in range(len(self.sorted_keys)):
            ring_idx = (idx + i) % len(self.sorted_keys)
            node = self.ring[self.sorted_keys[ring_idx]]

            if node not in seen_nodes:
                nodes.append(node)
                seen_nodes.add(node)

            if len(nodes) == count:
                break

        return nodes

    def get_distribution(self, num_keys: int = 10000) -> dict[str, int]:
        """Analyze how evenly keys are distributed across nodes."""
        distribution = defaultdict(int)
        for i in range(num_keys):
            node = self.get_node(f"test_key:{i}")
            if node:
                distribution[node] += 1
        return dict(distribution)


def demonstrate_basic_hashing_problem():
    """Show why regular hashing fails when nodes change."""
    print("\n❌ PROBLEM: Regular Hash-Based Sharding")
    print("─" * 50)

    num_keys = 1000
    keys = [f"user:{i}" for i in range(num_keys)]

    def assign_regular(key, num_shards):
        return f"shard-{int(hashlib.md5(key.encode()).hexdigest(), 16) % num_shards}"

    # Assignments with 4 shards
    assignments_4 = {k: assign_regular(k, 4) for k in keys}

    # Assignments with 5 shards (added one)
    assignments_5 = {k: assign_regular(k, 5) for k in keys}

    moved = sum(1 for k in keys if assignments_4[k] != assignments_5[k])
    print(f"  Keys with 4 shards: {num_keys}")
    print(f"  Keys moved when adding 5th shard: {moved} ({moved/num_keys*100:.0f}%)")
    print(f"  → Nearly ALL keys move! This is catastrophic in production.")


def demonstrate_consistent_hashing():
    """Show how consistent hashing minimizes data movement."""
    print("\n✅ SOLUTION: Consistent Hashing")
    print("─" * 50)

    num_keys = 10000
    keys = [f"user:{i}" for i in range(num_keys)]

    ring = ConsistentHashRing(virtual_nodes=150)
    ring.add_node("server-1")
    ring.add_node("server-2")
    ring.add_node("server-3")
    ring.add_node("server-4")

    # Record assignments before adding a node
    before = {k: ring.get_node(k) for k in keys}

    # Add a 5th node
    ring.add_node("server-5")

    # Record assignments after
    after = {k: ring.get_node(k) for k in keys}

    moved = sum(1 for k in keys if before[k] != after[k])
    print(f"  Keys total: {num_keys}")
    print(f"  Keys moved when adding 5th node: {moved} ({moved/num_keys*100:.1f}%)")
    print(f"  Expected: ~{num_keys//5} ({100//5}%) — only keys that move to new node")


def demonstrate_virtual_nodes():
    """Show how virtual nodes improve distribution."""
    print("\n📊 VIRTUAL NODES: Distribution Analysis")
    print("─" * 50)
    print(f"  {'VNodes/Node':<15} {'Max Deviation':<20} {'Assessment'}")
    print(f"  {'─'*13:<15} {'─'*18:<20} {'─'*15}")

    for vnodes in [1, 5, 20, 50, 150, 500]:
        ring = ConsistentHashRing(virtual_nodes=vnodes)
        for i in range(1, 6):
            ring.add_node(f"node-{i}")

        dist = ring.get_distribution(num_keys=50000)
        counts = list(dist.values())
        avg = sum(counts) / len(counts)
        max_dev = max(abs(c - avg) / avg * 100 for c in counts)

        assessment = "Poor" if max_dev > 30 else "OK" if max_dev > 10 else "Good" if max_dev > 5 else "Excellent"
        print(f"  {vnodes:<15} {max_dev:<19.1f}% {assessment}")


def demonstrate_replication():
    """Show consistent hashing with replication."""
    print("\n🔄 REPLICATION: Key → Multiple Nodes")
    print("─" * 50)

    ring = ConsistentHashRing(virtual_nodes=150)
    for i in range(1, 6):
        ring.add_node(f"node-{i}")

    test_keys = ["user:alice", "user:bob", "product:123", "session:xyz"]
    replication_factor = 3

    for key in test_keys:
        nodes = ring.get_nodes(key, replication_factor)
        print(f"  {key:<20} → {', '.join(nodes)}")

    print(f"\n  With RF={replication_factor}: each key is on {replication_factor} nodes")
    print(f"  If any 1 node fails, data is still available on {replication_factor-1} nodes")


def main():
    print("\n🔵 CONSISTENT HASHING DEMO — Day 11")
    print("=" * 60)

    demonstrate_basic_hashing_problem()
    demonstrate_consistent_hashing()
    demonstrate_virtual_nodes()
    demonstrate_replication()

    print("\n💡 KEY TAKEAWAYS:")
    print("  1. Regular hashing moves ~80% of keys when adding a node")
    print("  2. Consistent hashing moves only ~1/N keys (N = new node count)")
    print("  3. Virtual nodes ensure even distribution with few physical nodes")
    print("  4. Replication: store each key on N consecutive nodes for fault tolerance")
    print("  5. Used by: Cassandra, DynamoDB, CDNs, distributed caches")
    print()


if __name__ == "__main__":
    main()
