# Day 8: Exercises — CAP Theorem

---

## Exercise 1: Basic Comprehension (15 minutes)

1. State the CAP theorem in one sentence. Then explain why "CA" is not a real option for distributed systems.

2. A network partition occurs between two data centers. Your database chooses availability. What does this mean for users? What does it mean for data consistency?

3. Cassandra uses "tunable consistency." What does this mean? Give an example of when you'd use `QUORUM` vs. `ONE`.

4. What is the difference between CAP's "consistency" and ACID's "consistency"? (They use the same word but mean different things.)

5. PACELC adds the "EL" dimension. What does this capture that CAP misses?

---

## Exercise 2: Database Classification (20 minutes)

Classify each database/system by its CAP properties. For each, explain what happens during a network partition:

| System | CP or AP | What happens during partition? |
|--------|----------|-------------------------------|
| PostgreSQL (single node) | ? | ? |
| PostgreSQL (with streaming replication) | ? | ? |
| Cassandra (default) | ? | ? |
| HBase | ? | ? |
| Redis (single node) | ? | ? |
| Redis Cluster | ? | ? |
| DynamoDB (eventually consistent reads) | ? | ? |
| DynamoDB (strongly consistent reads) | ? | ? |
| etcd | ? | ? |
| MongoDB (replica set, majority write concern) | ? | ? |

---

## Exercise 3: Design Decision (25 minutes)

For each scenario, choose CP or AP and justify:

**Scenario 1: Online Banking**
- Users transfer money between accounts
- Regulatory requirement: no money can be created or destroyed
- Acceptable downtime: 4 hours/year (99.95%)

**Scenario 2: Social Media Likes**
- Users like posts
- Like count is displayed on posts
- 1 billion likes per day

**Scenario 3: E-Commerce Inventory**
- Products have inventory counts
- Users can purchase items
- Overselling is very bad (customer service nightmare)
- But the site going down during Black Friday is also very bad

**Scenario 4: Collaborative Document Editing (like Google Docs)**
- Multiple users edit the same document simultaneously
- Changes must eventually be visible to all users
- Brief inconsistency (one user sees old version for 1 second) is acceptable

For Scenario 3, this is the hardest one. There's no perfect answer — discuss the tradeoffs.

---

## Exercise 4: Partition Scenario Analysis (20 minutes)

### Scenario

You have a distributed database with 3 nodes: A, B, C.

A network partition splits the cluster: {A, B} can communicate with each other, but neither can communicate with C.

```
[A] ←──→ [B]
 ↑         ↑
 │         │
 ✗         ✗  (partition)
 │         │
 ↓         ↓
[C] ←──→ [C]  (C is isolated)
```

**Questions**:

1. **CP behavior**: What should nodes A, B, and C do? Can they serve reads? Writes?

2. **AP behavior**: What should nodes A, B, and C do? What are the risks?

3. A user writes `x=1` to Node A during the partition. The partition heals. Node C had `x=0`. What happens? How does the system resolve the conflict?

4. What is a "split-brain" scenario? How do you prevent it?

---

## Exercise 5: Challenge — Design a Consistent Distributed Counter (35 minutes)

### Problem

You need to build a distributed page view counter for a high-traffic website:
- 1 million page views per second
- Counter must be accurate (no double-counting, no lost counts)
- Counter must be readable with < 10ms latency
- System must be available 99.99%

**The tension**: Strong consistency (CP) means every increment requires coordination between nodes, which adds latency. High availability (AP) means you might lose some counts during partitions.

**Design options**:

**Option A: Strongly consistent counter**
- Use a single Redis instance with INCR
- Problem: single point of failure, limited throughput

**Option B: Distributed counter with coordination**
- Use a consensus protocol (Raft/Paxos) to coordinate increments
- Problem: coordination overhead, latency

**Option C: Approximate counter (AP)**
- Each node maintains its own counter
- Periodically merge counters
- Problem: count is approximate during merge window

**Option D: CRDT (Conflict-free Replicated Data Type)**
- Special data structure that can be merged without conflicts
- G-Counter: each node has its own slot, total = sum of all slots

**Your task**:
1. Implement Option D (G-Counter) conceptually — how does it work?
2. What are the consistency guarantees of a G-Counter?
3. For a page view counter, is eventual consistency acceptable? Why?
4. What would you choose for a financial transaction counter? Why?

---

## Hints

**Exercise 3, Scenario 3**: Think about what's worse — overselling 10 items, or the site being down for 1 hour on Black Friday. The answer depends on the business.

**Exercise 4, Q3**: This is the "conflict resolution" problem. Common strategies: last-write-wins, vector clocks, CRDTs.

**Exercise 5**: A G-Counter works like this: each node has a slot `[node_id]`. To increment, add 1 to your slot. To read the total, sum all slots. Merging two G-Counters takes the max of each slot.

---

## Self-Assessment Checklist

- [ ] I can state the CAP theorem precisely
- [ ] I understand why CA is not a real option
- [ ] I can classify real databases by their CAP properties
- [ ] I understand PACELC and why it's more nuanced than CAP
- [ ] I can make a CAP-informed design decision for a given scenario
- [ ] I understand the difference between CAP consistency and ACID consistency
