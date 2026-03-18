# Day 8: CAP Theorem — Concepts Deep Dive

## 1. The CAP Theorem

Proposed by Eric Brewer in 2000, proved by Gilbert and Lynch in 2002:

> **A distributed system cannot simultaneously guarantee all three of:**
> - **C**onsistency
> - **A**vailability  
> - **P**artition Tolerance

### Defining the Terms Precisely

**Consistency (C)**  
Every read receives the most recent write or an error. All nodes see the same data at the same time.

```
Node A: balance = $100
Node B: balance = $100

User writes: balance = $50 to Node A
Node A: balance = $50
Node B: balance = $100  ← INCONSISTENT (before replication)

With strong consistency: Node B returns error or waits until it has $50
```

**Availability (A)**  
Every request receives a (non-error) response — but it might not be the most recent data.

```
Node A is down.
With availability: Node B responds with possibly stale data
Without availability: Node B returns an error
```

**Partition Tolerance (P)**  
The system continues operating even when network messages are lost or delayed between nodes.

```
Network partition: Node A and Node B can't communicate

With partition tolerance: Both nodes continue serving requests
Without partition tolerance: System shuts down
```

---

## 2. Why "CA" Doesn't Exist

This is the most common misunderstanding of CAP.

**Network partitions always happen.** Networks are unreliable. Cables get cut. Switches fail. Packets get dropped. In any distributed system, you must assume partitions will occur.

Therefore, **partition tolerance is not optional**. You must design for it.

The real choice is: **when a partition occurs, do you sacrifice consistency or availability?**

```
CP (Consistency + Partition Tolerance):
  When partition occurs → refuse to serve stale data → return error
  Example: ZooKeeper, HBase, etcd

AP (Availability + Partition Tolerance):
  When partition occurs → serve possibly stale data → return something
  Example: Cassandra, CouchDB, DynamoDB (default)
```

"CA" systems (like a single-node PostgreSQL) only work because they're not distributed. The moment you add a second node, you have a distributed system and must handle partitions.

> **DDIA Reference**: Chapter 8 "The Trouble with Distributed Systems" — Kleppmann explains why network partitions are inevitable and how to design for them.

---

## 3. Visualizing CAP

```
              Consistency
                  /\
                 /  \
                /    \
               /  CP  \
              /        \
             /──────────\
            /     CA     \
           /  (not real   \
          /  in distributed \
         /     systems)      \
        /────────────────────\
       /          AP          \
      /______________________ \
  Availability          Partition
                        Tolerance
```

Real distributed systems live on the CP-AP spectrum, not at the vertices.

---

## 4. Real Database Classifications

### CP Databases (Consistency over Availability)

**HBase**
- Chooses consistency: if a region server is unavailable, reads/writes to that region fail
- Used by: Facebook (messages), Twitter (analytics)

**ZooKeeper / etcd**
- Distributed coordination services
- Will refuse requests rather than return stale data
- Used for: leader election, distributed locks, service discovery

**MongoDB (with majority write concern)**
- Can be configured for strong consistency
- Default: eventual consistency

### AP Databases (Availability over Consistency)

**Cassandra**
- Always available (no single point of failure)
- Tunable consistency: you choose per-query (ONE, QUORUM, ALL)
- Default: eventual consistency

**CouchDB**
- Designed for offline-first applications
- Sync when connected, work offline when not

**DynamoDB (default)**
- Eventually consistent reads by default
- Can request strongly consistent reads (higher cost)

### The Nuance: Tunable Consistency

Many modern databases let you choose per-operation:

```python
# Cassandra: choose consistency level per query
session.execute(
    "SELECT * FROM users WHERE id = ?",
    [user_id],
    consistency_level=ConsistencyLevel.QUORUM  # Wait for majority
)

session.execute(
    "INSERT INTO events ...",
    consistency_level=ConsistencyLevel.ONE  # Write to one node, fast
)
```

This means the CP vs. AP classification is not binary — it's a dial.

---

## 5. PACELC — A Better Model

CAP only describes behavior during partitions. But what about normal operation?

**PACELC** (proposed by Daniel Abadi, 2012):

> If there is a **P**artition, choose between **A**vailability and **C**onsistency.  
> **E**lse (no partition), choose between **L**atency and **C**onsistency.

```
PACELC Classification:

Database        | Partition | Else
----------------|-----------|------
DynamoDB        | AP        | EL (low latency, eventual consistency)
Cassandra       | AP        | EL
HBase           | CP        | EC (consistent, higher latency)
MySQL (cluster) | CP        | EC
Spanner (Google)| CP        | EC (but very low latency via atomic clocks)
```

PACELC is more useful because it captures the everyday tradeoff (latency vs. consistency), not just the rare partition scenario.

---

## 6. Consistency Models (Beyond CAP)

CAP's "consistency" is actually "linearizability" — the strongest consistency model. There are weaker models that are often sufficient:

### Linearizability (Strongest)
Every operation appears to take effect instantaneously at some point between its start and end. All clients see the same order of operations.

```
Client A: Write x=1 (completes at t=5)
Client B: Read x (starts at t=6) → Must see x=1
```

### Sequential Consistency
All operations appear to execute in some sequential order, consistent with the order seen by each individual client.

### Causal Consistency
Operations that are causally related are seen in the same order by all nodes. Concurrent operations may be seen in different orders.

```
Alice posts: "I'm going to the store"
Bob replies: "Pick up milk!"
Carol must see Alice's post before Bob's reply (causal order)
```

### Eventual Consistency (Weakest)
If no new updates are made, all replicas will eventually converge to the same value.

```
Write x=1 to Node A
Node B still has x=0 (old value)
After some time, Node B receives the update: x=1
```

---

## 7. Practical CAP Decision Guide

```
Is data loss acceptable?
  NO → CP (consistency over availability)
  YES → AP (availability over consistency)

Examples:
  Financial transactions → CP (never lose a transaction)
  User profile picture → AP (stale picture for 2 seconds is fine)
  Shopping cart → AP (losing a cart item is annoying but not catastrophic)
  Inventory count → CP (can't oversell)
  Social media likes → AP (approximate count is fine)
  Medical records → CP (must be accurate)
```

---

## 8. The Consistency Spectrum in Practice

```
Strongest ←────────────────────────────────────────→ Weakest

Linearizable  Sequential  Causal  Read-your-writes  Eventual
     │              │         │           │              │
  ZooKeeper    Spanner    DynamoDB    PostgreSQL    Cassandra
  etcd         (global)   (strong)    (default)    (default)
```

Most applications don't need linearizability. Causal consistency or read-your-writes is often sufficient.

---

## References
- DDIA Chapter 9: Consistency and Consensus (the most important chapter for this topic)
- [CAP Twelve Years Later: How the "Rules" Have Changed](https://www.infoq.com/articles/cap-twelve-years-later-how-the-rules-have-changed/) — Eric Brewer
- [PACELC Paper](https://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf) — Daniel Abadi
