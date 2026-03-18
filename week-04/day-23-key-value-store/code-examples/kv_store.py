"""
Distributed Key-Value Store Implementation
==========================================
A working implementation demonstrating core KV store concepts:
- LSM Tree storage engine with MemTable + SSTables
- Write-Ahead Log (WAL) for crash recovery
- Bloom filters for read optimization
- LRU cache layer
- Consistent hashing for distribution simulation

Run: python kv_store.py
Requirements: pip install sortedcontainers mmh3
"""

import os
import json
import time
import math
import hashlib
import struct
import bisect
from collections import OrderedDict
from typing import Optional, List, Tuple, Dict, Any


# ─────────────────────────────────────────────
# Bloom Filter
# ─────────────────────────────────────────────

class BloomFilter:
    """
    Probabilistic data structure for membership testing.
    No false negatives. Small false positive rate (~1% with good sizing).
    
    Used to avoid unnecessary disk reads for SSTables.
    """
    
    def __init__(self, expected_items: int = 1000, false_positive_rate: float = 0.01):
        # Calculate optimal bit array size and hash count
        self.size = self._optimal_size(expected_items, false_positive_rate)
        self.hash_count = self._optimal_hash_count(self.size, expected_items)
        self.bit_array = bytearray(math.ceil(self.size / 8))
        self.item_count = 0
    
    def _optimal_size(self, n: int, p: float) -> int:
        """m = -(n * ln(p)) / (ln(2)^2)"""
        return int(-(n * math.log(p)) / (math.log(2) ** 2))
    
    def _optimal_hash_count(self, m: int, n: int) -> int:
        """k = (m/n) * ln(2)"""
        return max(1, int((m / n) * math.log(2)))
    
    def _get_bit_positions(self, key: str) -> List[int]:
        """Generate k hash positions for a key."""
        positions = []
        for i in range(self.hash_count):
            # Use different seeds for each hash function
            h = int(hashlib.md5(f"{i}:{key}".encode()).hexdigest(), 16)
            positions.append(h % self.size)
        return positions
    
    def add(self, key: str):
        """Add a key to the bloom filter."""
        for pos in self._get_bit_positions(key):
            byte_idx = pos // 8
            bit_idx = pos % 8
            self.bit_array[byte_idx] |= (1 << bit_idx)
        self.item_count += 1
    
    def might_contain(self, key: str) -> bool:
        """
        Returns False if key is definitely NOT present.
        Returns True if key MIGHT be present (could be false positive).
        """
        for pos in self._get_bit_positions(key):
            byte_idx = pos // 8
            bit_idx = pos % 8
            if not (self.bit_array[byte_idx] & (1 << bit_idx)):
                return False  # Definitely not present
        return True  # Probably present


# ─────────────────────────────────────────────
# Write-Ahead Log (WAL)
# ─────────────────────────────────────────────

class WAL:
    """
    Write-Ahead Log for crash recovery.
    Every write is logged here BEFORE being applied to the MemTable.
    On restart, replay the WAL to reconstruct in-memory state.
    """
    
    TOMBSTONE = "__DELETED__"
    
    def __init__(self, path: str):
        self.path = path
        self._file = open(path, 'a', encoding='utf-8')
    
    def append(self, key: str, value: Optional[str]):
        """Append a write operation to the WAL."""
        entry = json.dumps({
            "key": key,
            "value": value if value is not None else self.TOMBSTONE,
            "ts": time.time()
        })
        self._file.write(entry + "\n")
        self._file.flush()  # Ensure it's on disk before acknowledging write
    
    def recover(self) -> List[Tuple[str, Optional[str]]]:
        """Read WAL and return list of (key, value) operations."""
        operations = []
        if not os.path.exists(self.path):
            return operations
        
        with open(self.path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    value = None if entry["value"] == self.TOMBSTONE else entry["value"]
                    operations.append((entry["key"], value))
                except json.JSONDecodeError:
                    # Corrupted entry — skip (last write may be incomplete)
                    pass
        return operations
    
    def clear(self):
        """Clear WAL after MemTable has been flushed to SSTable."""
        self._file.close()
        open(self.path, 'w').close()  # Truncate
        self._file = open(self.path, 'a', encoding='utf-8')
    
    def close(self):
        self._file.close()


# ─────────────────────────────────────────────
# MemTable
# ─────────────────────────────────────────────

class MemTable:
    """
    In-memory sorted data structure.
    New writes go here first. When full, flushed to SSTable on disk.
    
    Uses a simple sorted dict (in production: red-black tree or skip list).
    """
    
    TOMBSTONE = "__DELETED__"
    
    def __init__(self, max_size: int = 100):
        # In production, use a balanced BST for O(log n) operations
        self._data: Dict[str, str] = {}
        self.max_size = max_size
    
    def set(self, key: str, value: str):
        self._data[key] = value
    
    def delete(self, key: str):
        """Write a tombstone — actual deletion happens during compaction."""
        self._data[key] = self.TOMBSTONE
    
    def get(self, key: str) -> Optional[str]:
        """Returns value, None (tombstone = deleted), or raises KeyError (not found)."""
        if key not in self._data:
            raise KeyError(key)
        value = self._data[key]
        return None if value == self.TOMBSTONE else value
    
    def is_full(self) -> bool:
        return len(self._data) >= self.max_size
    
    def sorted_items(self) -> List[Tuple[str, str]]:
        """Return all items sorted by key (for SSTable flush)."""
        return sorted(self._data.items())
    
    def clear(self):
        self._data.clear()
    
    def __len__(self):
        return len(self._data)


# ─────────────────────────────────────────────
# SSTable (Sorted String Table)
# ─────────────────────────────────────────────

class SSTable:
    """
    Immutable sorted file on disk.
    
    File format (simplified):
    - Each line: JSON {"key": k, "value": v}
    - Index file: JSON {"key": byte_offset}
    - Bloom filter file: serialized bloom filter
    """
    
    TOMBSTONE = "__DELETED__"
    
    def __init__(self, path: str):
        self.path = path
        self.index_path = path + ".index"
        self.bloom_path = path + ".bloom"
        self._index: Dict[str, int] = {}
        self._bloom: Optional[BloomFilter] = None
        
        if os.path.exists(self.index_path):
            self._load_index()
        if os.path.exists(self.bloom_path):
            self._load_bloom()
    
    @classmethod
    def create(cls, path: str, sorted_items: List[Tuple[str, str]]) -> 'SSTable':
        """Create a new SSTable from sorted key-value pairs."""
        bloom = BloomFilter(expected_items=max(len(sorted_items), 1))
        index = {}
        
        with open(path, 'w', encoding='utf-8') as f:
            for key, value in sorted_items:
                offset = f.tell()
                index[key] = offset
                bloom.add(key)
                entry = json.dumps({"key": key, "value": value})
                f.write(entry + "\n")
        
        # Write index
        with open(path + ".index", 'w', encoding='utf-8') as f:
            json.dump(index, f)
        
        # Write bloom filter (simplified — just store the bit array)
        with open(path + ".bloom", 'w', encoding='utf-8') as f:
            json.dump({
                "size": bloom.size,
                "hash_count": bloom.hash_count,
                "bits": list(bloom.bit_array)
            }, f)
        
        return cls(path)
    
    def _load_index(self):
        with open(self.index_path, 'r', encoding='utf-8') as f:
            self._index = json.load(f)
    
    def _load_bloom(self):
        with open(self.bloom_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self._bloom = BloomFilter.__new__(BloomFilter)
        self._bloom.size = data["size"]
        self._bloom.hash_count = data["hash_count"]
        self._bloom.bit_array = bytearray(data["bits"])
        self._bloom.item_count = 0
    
    def get(self, key: str) -> Optional[str]:
        """
        Look up a key. Returns:
        - str: the value
        - None: key was deleted (tombstone)
        - raises KeyError: key not in this SSTable
        """
        # Bloom filter check — skip if definitely not present
        if self._bloom and not self._bloom.might_contain(key):
            raise KeyError(key)
        
        # Use index for O(1) lookup
        if key not in self._index:
            raise KeyError(key)
        
        offset = self._index[key]
        with open(self.path, 'r', encoding='utf-8') as f:
            f.seek(offset)
            line = f.readline()
            entry = json.loads(line)
            if entry["value"] == self.TOMBSTONE:
                return None  # Deleted
            return entry["value"]
    
    def get_all_keys(self) -> List[str]:
        return list(self._index.keys())
    
    def size(self) -> int:
        return len(self._index)


# ─────────────────────────────────────────────
# LRU Cache
# ─────────────────────────────────────────────

class LRUCache:
    """
    Least Recently Used cache using OrderedDict.
    Sits in front of the storage engine to serve hot keys from memory.
    """
    
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self._cache: OrderedDict = OrderedDict()
    
    def get(self, key: str) -> Optional[str]:
        if key not in self._cache:
            return None
        # Move to end (most recently used)
        self._cache.move_to_end(key)
        return self._cache[key]
    
    def put(self, key: str, value: Optional[str]):
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        if len(self._cache) > self.capacity:
            self._cache.popitem(last=False)  # Remove LRU item
    
    def invalidate(self, key: str):
        self._cache.pop(key, None)
    
    def hit_rate(self) -> float:
        return getattr(self, '_hits', 0) / max(getattr(self, '_total', 1), 1)


# ─────────────────────────────────────────────
# LSM Tree Storage Engine
# ─────────────────────────────────────────────

class LSMTree:
    """
    Log-Structured Merge Tree storage engine.
    
    Write path: WAL → MemTable → (flush) → SSTable
    Read path: LRU Cache → MemTable → SSTables (newest first)
    Background: Compaction merges SSTables
    """
    
    def __init__(self, data_dir: str = "./lsm_data", memtable_size: int = 50):
        os.makedirs(data_dir, exist_ok=True)
        self.data_dir = data_dir
        self.wal = WAL(os.path.join(data_dir, "wal.log"))
        self.memtable = MemTable(max_size=memtable_size)
        self.sstables: List[SSTable] = []  # Newest first
        self.cache = LRUCache(capacity=500)
        self._sstable_counter = 0
        self._stats = {"reads": 0, "writes": 0, "cache_hits": 0, "flushes": 0}
        
        # Load existing SSTables
        self._load_existing_sstables()
        
        # Recover from WAL if needed
        self._recover_from_wal()
    
    def _load_existing_sstables(self):
        """Load SSTables from disk on startup."""
        sst_files = sorted([
            f for f in os.listdir(self.data_dir)
            if f.endswith('.sst') and not f.endswith('.index') and not f.endswith('.bloom')
        ], reverse=True)  # Newest first (by name)
        
        for filename in sst_files:
            path = os.path.join(self.data_dir, filename)
            self.sstables.append(SSTable(path))
        
        if sst_files:
            # Extract counter from last SSTable name
            last = sst_files[0]
            self._sstable_counter = int(last.split('_')[1].split('.')[0]) + 1
    
    def _recover_from_wal(self):
        """Replay WAL to reconstruct MemTable after crash."""
        operations = self.wal.recover()
        if operations:
            print(f"[Recovery] Replaying {len(operations)} operations from WAL")
            for key, value in operations:
                if value is None:
                    self.memtable.delete(key)
                else:
                    self.memtable.set(key, value)
    
    def set(self, key: str, value: str):
        """Write a key-value pair."""
        self._stats["writes"] += 1
        
        # 1. Write to WAL first (crash safety)
        self.wal.append(key, value)
        
        # 2. Write to MemTable
        self.memtable.set(key, value)
        
        # 3. Invalidate cache
        self.cache.invalidate(key)
        
        # 4. Flush MemTable to SSTable if full
        if self.memtable.is_full():
            self._flush_memtable()
    
    def get(self, key: str) -> Optional[str]:
        """Read a value by key. Returns None if deleted or not found."""
        self._stats["reads"] += 1
        
        # 1. Check LRU cache
        cached = self.cache.get(key)
        if cached is not None:
            self._stats["cache_hits"] += 1
            return cached
        
        # 2. Check MemTable (most recent writes)
        try:
            value = self.memtable.get(key)
            self.cache.put(key, value)
            return value
        except KeyError:
            pass
        
        # 3. Check SSTables (newest first)
        for sst in self.sstables:
            try:
                value = sst.get(key)
                self.cache.put(key, value)
                return value
            except KeyError:
                continue
        
        return None  # Not found
    
    def delete(self, key: str):
        """Delete a key by writing a tombstone."""
        self.wal.append(key, None)
        self.memtable.delete(key)
        self.cache.invalidate(key)
    
    def _flush_memtable(self):
        """Flush MemTable to a new SSTable on disk."""
        self._stats["flushes"] += 1
        
        # Create SSTable from sorted MemTable contents
        sst_path = os.path.join(
            self.data_dir,
            f"sst_{self._sstable_counter:06d}.sst"
        )
        sorted_items = self.memtable.sorted_items()
        sst = SSTable.create(sst_path, sorted_items)
        
        # Prepend to list (newest first)
        self.sstables.insert(0, sst)
        self._sstable_counter += 1
        
        # Clear MemTable and WAL
        self.memtable.clear()
        self.wal.clear()
        
        print(f"[Flush] Flushed {len(sorted_items)} entries to {sst_path}")
        
        # Trigger compaction if too many SSTables
        if len(self.sstables) >= 5:
            self._compact()
    
    def _compact(self):
        """
        Merge all SSTables into one, removing tombstones and duplicates.
        In production: leveled or size-tiered compaction strategies.
        """
        print(f"[Compaction] Merging {len(self.sstables)} SSTables...")
        
        # Collect all keys (newest SSTable wins for duplicates)
        merged: Dict[str, str] = {}
        for sst in reversed(self.sstables):  # Oldest first
            for key in sst.get_all_keys():
                try:
                    value = sst.get(key)
                    if value is None:
                        # Tombstone — mark for deletion
                        merged[key] = MemTable.TOMBSTONE
                    else:
                        merged[key] = value
                except KeyError:
                    pass
        
        # Remove tombstones (safe to do during compaction)
        merged = {k: v for k, v in merged.items() if v != MemTable.TOMBSTONE}
        
        # Write new compacted SSTable
        sst_path = os.path.join(
            self.data_dir,
            f"sst_{self._sstable_counter:06d}.sst"
        )
        sorted_items = sorted(merged.items())
        new_sst = SSTable.create(sst_path, sorted_items)
        self._sstable_counter += 1
        
        # Delete old SSTables
        for sst in self.sstables:
            for path in [sst.path, sst.index_path, sst.bloom_path]:
                if os.path.exists(path):
                    os.remove(path)
        
        self.sstables = [new_sst]
        print(f"[Compaction] Done. {len(sorted_items)} keys in compacted SSTable.")
    
    def stats(self) -> Dict[str, Any]:
        return {
            **self._stats,
            "memtable_size": len(self.memtable),
            "sstable_count": len(self.sstables),
            "cache_hit_rate": f"{self._stats['cache_hits'] / max(self._stats['reads'], 1) * 100:.1f}%"
        }
    
    def close(self):
        self.wal.close()


# ─────────────────────────────────────────────
# Consistent Hashing (for distribution)
# ─────────────────────────────────────────────

class ConsistentHashRing:
    """
    Distributes keys across nodes using consistent hashing.
    Virtual nodes (vnodes) ensure even distribution.
    """
    
    def __init__(self, vnodes_per_node: int = 150):
        self.vnodes_per_node = vnodes_per_node
        self.ring: Dict[int, str] = {}
        self.sorted_keys: List[int] = []
        self.nodes: List[str] = []
    
    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def add_node(self, node: str):
        """Add a node with virtual nodes for even distribution."""
        self.nodes.append(node)
        for i in range(self.vnodes_per_node):
            vnode_key = self._hash(f"{node}:vnode:{i}")
            self.ring[vnode_key] = node
            bisect.insort(self.sorted_keys, vnode_key)
    
    def remove_node(self, node: str):
        """Remove a node and its virtual nodes."""
        self.nodes.remove(node)
        for i in range(self.vnodes_per_node):
            vnode_key = self._hash(f"{node}:vnode:{i}")
            del self.ring[vnode_key]
            self.sorted_keys.remove(vnode_key)
    
    def get_node(self, key: str) -> str:
        """Get the node responsible for a key."""
        if not self.ring:
            raise Exception("No nodes in ring")
        
        key_hash = self._hash(key)
        idx = bisect.bisect_right(self.sorted_keys, key_hash)
        
        # Wrap around
        if idx == len(self.sorted_keys):
            idx = 0
        
        return self.ring[self.sorted_keys[idx]]
    
    def get_nodes_for_key(self, key: str, n: int = 3) -> List[str]:
        """Get N nodes for replication (next N unique nodes clockwise)."""
        if not self.ring:
            return []
        
        key_hash = self._hash(key)
        idx = bisect.bisect_right(self.sorted_keys, key_hash)
        
        nodes = []
        seen = set()
        for i in range(len(self.sorted_keys)):
            node = self.ring[self.sorted_keys[(idx + i) % len(self.sorted_keys)]]
            if node not in seen:
                nodes.append(node)
                seen.add(node)
            if len(nodes) == n:
                break
        
        return nodes
    
    def distribution_stats(self) -> Dict[str, int]:
        """Show how many vnodes each node has (should be roughly equal)."""
        counts: Dict[str, int] = {}
        for node in self.ring.values():
            counts[node] = counts.get(node, 0) + 1
        return counts


# ─────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────

def demo_lsm_tree():
    """Demonstrate LSM tree operations."""
    print("=" * 60)
    print("LSM Tree Demo")
    print("=" * 60)
    
    import shutil
    if os.path.exists("./demo_lsm"):
        shutil.rmtree("./demo_lsm")
    
    db = LSMTree(data_dir="./demo_lsm", memtable_size=5)
    
    # Basic operations
    print("\n--- Basic Operations ---")
    db.set("user:1", "Alice")
    db.set("user:2", "Bob")
    db.set("user:3", "Charlie")
    print(f"get user:1 → {db.get('user:1')}")
    print(f"get user:2 → {db.get('user:2')}")
    
    # Update
    db.set("user:1", "Alice Updated")
    print(f"get user:1 (after update) → {db.get('user:1')}")
    
    # Delete
    db.delete("user:2")
    print(f"get user:2 (after delete) → {db.get('user:2')}")
    
    # Trigger flush by filling MemTable
    print("\n--- Triggering MemTable Flush ---")
    for i in range(10):
        db.set(f"key:{i}", f"value:{i}")
    
    # Reads after flush (from SSTable)
    print(f"get key:0 (from SSTable) → {db.get('key:0')}")
    print(f"get key:5 (from SSTable) → {db.get('key:5')}")
    
    # Stats
    print(f"\n--- Stats ---")
    for k, v in db.stats().items():
        print(f"  {k}: {v}")
    
    db.close()
    shutil.rmtree("./demo_lsm")


def demo_bloom_filter():
    """Demonstrate bloom filter behavior."""
    print("\n" + "=" * 60)
    print("Bloom Filter Demo")
    print("=" * 60)
    
    bf = BloomFilter(expected_items=100, false_positive_rate=0.01)
    
    # Add some keys
    keys = [f"user:{i}" for i in range(50)]
    for key in keys:
        bf.add(key)
    
    # Test membership
    true_positives = sum(1 for k in keys if bf.might_contain(k))
    
    # Test false positives
    non_keys = [f"product:{i}" for i in range(1000)]
    false_positives = sum(1 for k in non_keys if bf.might_contain(k))
    
    print(f"Keys added: {len(keys)}")
    print(f"True positives: {true_positives}/{len(keys)} (should be 100%)")
    print(f"False positives: {false_positives}/{len(non_keys)} ({false_positives/len(non_keys)*100:.2f}%)")
    print(f"Bit array size: {bf.size} bits ({bf.size//8} bytes)")
    print(f"Hash functions: {bf.hash_count}")


def demo_consistent_hashing():
    """Demonstrate consistent hashing distribution."""
    print("\n" + "=" * 60)
    print("Consistent Hashing Demo")
    print("=" * 60)
    
    ring = ConsistentHashRing(vnodes_per_node=150)
    
    # Add nodes
    for i in range(5):
        ring.add_node(f"node-{i}")
    
    # Distribute 1000 keys
    distribution: Dict[str, int] = {}
    for i in range(1000):
        node = ring.get_node(f"key:{i}")
        distribution[node] = distribution.get(node, 0) + 1
    
    print("Key distribution across 5 nodes (1000 keys):")
    for node, count in sorted(distribution.items()):
        bar = "█" * (count // 5)
        print(f"  {node}: {count:4d} keys {bar}")
    
    # Show replication
    print(f"\nReplication for 'user:1001' (N=3):")
    nodes = ring.get_nodes_for_key("user:1001", n=3)
    for i, node in enumerate(nodes):
        role = "primary" if i == 0 else f"replica-{i}"
        print(f"  {role}: {node}")
    
    # Show what happens when a node is removed
    print(f"\nRemoving node-2...")
    ring.remove_node("node-2")
    
    new_distribution: Dict[str, int] = {}
    for i in range(1000):
        node = ring.get_node(f"key:{i}")
        new_distribution[node] = new_distribution.get(node, 0) + 1
    
    print("Distribution after removing node-2:")
    for node, count in sorted(new_distribution.items()):
        bar = "█" * (count // 5)
        print(f"  {node}: {count:4d} keys {bar}")


if __name__ == "__main__":
    demo_lsm_tree()
    demo_bloom_filter()
    demo_consistent_hashing()
    
    print("\n" + "=" * 60)
    print("All demos complete!")
    print("=" * 60)
