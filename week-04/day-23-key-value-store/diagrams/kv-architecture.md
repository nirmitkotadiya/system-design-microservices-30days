# Key-Value Store Architecture Diagrams

## 1. LSM Tree Write Path

```mermaid
flowchart TD
    Client([Client Write]) --> WAL[WAL\nWrite-Ahead Log\nSequential disk write]
    WAL --> MT[MemTable\nIn-memory sorted structure\nRed-black tree / Skip list]
    MT -->|MemTable full ~64MB| Flush[Flush to SSTable\nLevel 0]
    Flush --> L0[Level 0 SSTables\nMay overlap\nNewest first]
    L0 -->|Compaction trigger| L1[Level 1 SSTables\nNo overlap\n~10x larger than L0]
    L1 -->|Compaction| L2[Level 2 SSTables\n~10x larger than L1]
    L2 -->|Compaction| L3[Level 3 SSTables\n~10x larger than L2]

    style WAL fill:#ff9999
    style MT fill:#99ccff
    style L0 fill:#99ff99
    style L1 fill:#99ff99
    style L2 fill:#99ff99
    style L3 fill:#99ff99
```

## 2. LSM Tree Read Path

```mermaid
flowchart TD
    Client([Client Read]) --> Cache{LRU Cache\nHit?}
    Cache -->|Hit| Return1([Return cached value])
    Cache -->|Miss| MT{MemTable\nHas key?}
    MT -->|Found| Return2([Return value])
    MT -->|Not found| BF{Bloom Filter\nCheck L0 SSTable 1}
    BF -->|Definitely not here| BF2{Bloom Filter\nCheck L0 SSTable 2}
    BF -->|Might be here| Disk1[Read SSTable 1\nfrom disk]
    Disk1 -->|Found| Return3([Return value])
    Disk1 -->|Not found| BF2
    BF2 -->|Check more levels...| L1[Check Level 1\nSSTables...]
    L1 --> NotFound([Return null])

    style Cache fill:#ffcc99
    style BF fill:#cc99ff
    style BF2 fill:#cc99ff
```

## 3. Distributed KV Store Architecture

```mermaid
graph TB
    subgraph Clients
        C1[Client 1]
        C2[Client 2]
        C3[Client 3]
    end

    subgraph Load Balancer
        LB[Load Balancer\nRoutes to coordinator]
    end

    subgraph Coordinator Nodes
        CO1[Coordinator 1]
        CO2[Coordinator 2]
    end

    subgraph Storage Nodes - Consistent Hash Ring
        N1[Node 1\nRange: 0-20%]
        N2[Node 2\nRange: 20-40%]
        N3[Node 3\nRange: 40-60%]
        N4[Node 4\nRange: 60-80%]
        N5[Node 5\nRange: 80-100%]
    end

    C1 & C2 & C3 --> LB
    LB --> CO1 & CO2
    CO1 -->|Hash key → route| N1 & N2 & N3
    CO2 -->|Hash key → route| N3 & N4 & N5

    N1 -.->|Replicate| N2
    N2 -.->|Replicate| N3
    N3 -.->|Replicate| N4
    N4 -.->|Replicate| N5
    N5 -.->|Replicate| N1
```

## 4. Consistent Hash Ring

```
                    0°
                  Node A
                 /       \
           315°             45°
          Node E           Node B
           |                 |
           |   Hash Ring     |
          270°             90°
          Node D           Node C
                 \       /
                  225°
                  (empty)

Key "user:1001" → hash → 127° → Node C (next clockwise)
Key "user:1002" → hash → 280° → Node D (next clockwise)
Key "user:1003" → hash → 350° → Node A (next clockwise)

Replication (N=3): each key stored on 3 consecutive nodes
"user:1001" → primary: Node C, replica1: Node D, replica2: Node E
```

## 5. SSTable File Format

```
┌─────────────────────────────────────────────────────┐
│                    SSTable File                      │
├─────────────────────────────────────────────────────┤
│  Data Block 1 (4KB)                                 │
│  ┌─────────────────────────────────────────────┐   │
│  │ "alice" → "data..."  (offset: 0)            │   │
│  │ "bob"   → "data..."  (offset: 45)           │   │
│  │ "carol" → TOMBSTONE  (offset: 89)           │   │
│  └─────────────────────────────────────────────┘   │
│  Data Block 2 (4KB)                                 │
│  ┌─────────────────────────────────────────────┐   │
│  │ "dave"  → "data..."  (offset: 4096)         │   │
│  │ "eve"   → "data..."  (offset: 4140)         │   │
│  └─────────────────────────────────────────────┘   │
│  ...more data blocks...                             │
├─────────────────────────────────────────────────────┤
│  Index Block                                        │
│  ┌─────────────────────────────────────────────┐   │
│  │ "alice" → offset 0                          │   │
│  │ "bob"   → offset 45                         │   │
│  │ "carol" → offset 89                         │   │
│  │ "dave"  → offset 4096                       │   │
│  │ "eve"   → offset 4140                       │   │
│  └─────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────┤
│  Bloom Filter (10 bits/key, ~1% false positive)     │
├─────────────────────────────────────────────────────┤
│  Footer (offsets to index and bloom filter)         │
└─────────────────────────────────────────────────────┘
```

## 6. Compaction: Before and After

```
BEFORE COMPACTION (4 SSTables, Level 0):

SSTable 1 (oldest): alice=1, bob=2, carol=3
SSTable 2:          bob=99, dave=4          ← bob updated
SSTable 3:          alice=TOMBSTONE          ← alice deleted
SSTable 4 (newest): carol=TOMBSTONE, eve=5  ← carol deleted

Read "bob": check SSTable 4 (not found) → SSTable 3 (not found) 
           → SSTable 2 (found! bob=99) ✓
           = 3 SSTable reads!

AFTER COMPACTION (1 SSTable, Level 1):

SSTable merged: bob=99, dave=4, eve=5
(alice and carol removed — tombstones purged)

Read "bob": check SSTable 1 (found! bob=99) ✓
           = 1 SSTable read!
```

## 7. Quorum Reads and Writes

```
N=3 replicas, W=2, R=2 (strong consistency: W+R > N)

WRITE "user:1" = "Alice":
  Coordinator → Node A: ACK ✓
  Coordinator → Node B: ACK ✓  ← W=2 achieved, return success
  Coordinator → Node C: (still in flight, will eventually sync)

READ "user:1":
  Coordinator → Node A: "Alice" ✓
  Coordinator → Node B: "Alice" ✓  ← R=2 achieved, return "Alice"
  (Node C not needed)

NETWORK PARTITION (Node C isolated):
  W=2: Can still write to A and B ✓
  R=2: Can still read from A and B ✓
  → System remains available during partition!

EVENTUAL CONSISTENCY (W=1, R=1):
  Write to any 1 node → return success
  Read from any 1 node → might get stale data
  → Higher availability, lower consistency
```
