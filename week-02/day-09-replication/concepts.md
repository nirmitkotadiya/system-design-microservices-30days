# Day 9: Replication Strategies — Concepts Deep Dive

## 1. Why Replicate?

Two reasons:
1. **High Availability**: If one node fails, others can take over
2. **Read Scaling**: Spread read load across multiple nodes

```
Without replication:
  Single DB → fails → entire system down

With replication:
  Primary DB → fails → replica promoted → system continues
  Primary DB → 100k reads/sec → too slow
  3 replicas → 33k reads/sec each → manageable
```

---

## 2. Leader-Follower Replication (Master-Slave)

The most common replication model.

```
                    ┌─────────────┐
Writes ────────────▶│   Leader    │
                    │  (Primary)  │
                    └──────┬──────┘
                           │ Replication log
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
Reads ─▶│Follower 1│ │Follower 2│ │Follower 3│
        └──────────┘ └──────────┘ └──────────┘
```

**How it works**:
1. All writes go to the leader
2. Leader writes to its local storage and a replication log
3. Followers read the replication log and apply changes
4. Reads can go to any follower (or the leader)

**Used by**: PostgreSQL, MySQL, MongoDB, Redis

### Synchronous vs. Asynchronous Replication

**Synchronous**:
```
Client → Write to Leader
Leader → Write to Follower 1 (wait for ACK)
Leader → ACK to Client

Guarantee: Follower 1 always has up-to-date data
Cost: Write latency = Leader latency + Follower latency
Risk: If Follower 1 is slow, all writes are slow
```

**Asynchronous**:
```
Client → Write to Leader
Leader → ACK to Client (immediately)
Leader → Write to Follower 1 (in background)

Guarantee: None — follower may be behind
Cost: Write latency = Leader latency only
Risk: If leader fails before replication, data is lost
```

**Semi-synchronous** (PostgreSQL default):
```
Wait for at least one follower to acknowledge.
Other followers replicate asynchronously.
Balance between durability and performance.
```

### Replication Lag

The delay between a write on the leader and its appearance on followers.

```
t=0: User updates profile picture (write to leader)
t=0: Leader ACKs to user
t=2s: Follower receives and applies the update

If user reads from follower at t=1s: sees old picture
If user reads from follower at t=3s: sees new picture
```

**Replication lag problems**:

1. **Read-your-writes violation**: User writes something, immediately reads it, gets old data
2. **Monotonic reads violation**: User reads new data, then reads old data (from different replicas)
3. **Consistent prefix reads violation**: User sees effects before causes

**Solutions**:
- Route reads to leader for a short window after writes
- Track replication position and route to replicas that are caught up
- Use sticky sessions (always read from same replica)

> **DDIA Reference**: Chapter 5 covers replication lag and its consequences in detail. This is one of the most practically important sections.

---

## 3. Multi-Leader Replication

Multiple nodes can accept writes. Each leader replicates to all other leaders.

```
Data Center A          Data Center B
┌──────────┐           ┌──────────┐
│ Leader A │◄─────────▶│ Leader B │
└────┬─────┘           └────┬─────┘
     │                      │
┌────▼─────┐           ┌────▼─────┐
│Follower A│           │Follower B│
└──────────┘           └──────────┘
```

**Use cases**:
- Multi-datacenter deployments (each DC has its own leader)
- Offline-capable clients (mobile apps that sync when online)
- Collaborative editing (Google Docs)

**The Big Problem: Write Conflicts**

```
User A (connected to Leader A): title = "Hello"
User B (connected to Leader B): title = "World"

Both writes succeed locally.
When leaders sync: conflict!
Which value wins?
```

### Conflict Resolution Strategies

**Last Write Wins (LWW)**:
```
Each write has a timestamp.
The write with the latest timestamp wins.

Problem: Clocks are not perfectly synchronized.
         A write with a slightly later timestamp might actually be older.
         Data loss is possible.
```

**Merge**:
```
For some data types, you can merge:
- Sets: union of both sets
- Counters: sum of both counters
- Text: use operational transformation (Google Docs approach)
```

**Custom conflict resolution**:
```python
def resolve_conflict(local_value, remote_value, local_timestamp, remote_timestamp):
    # Application-specific logic
    if local_timestamp > remote_timestamp:
        return local_value
    return remote_value
```

**CRDTs (Conflict-free Replicated Data Types)**:
Data structures designed to merge without conflicts. We'll see these in Day 11.

---

## 4. Leaderless Replication

No single leader. Any node can accept writes. Reads and writes go to multiple nodes simultaneously.

**Used by**: Cassandra, DynamoDB, Riak

```
Client writes to N nodes simultaneously:
  Write to Node 1 ✓
  Write to Node 2 ✓
  Write to Node 3 ✗ (failed)

With W=2 (write quorum): success (2 out of 3 succeeded)

Client reads from N nodes simultaneously:
  Read from Node 1: value=1, version=5
  Read from Node 2: value=1, version=5
  Read from Node 3: value=0, version=3 (stale)

With R=2 (read quorum): return version=5 (most recent)
```

### Quorum Reads and Writes

The key formula: **W + R > N**

Where:
- N = total replicas
- W = write quorum (nodes that must acknowledge a write)
- R = read quorum (nodes that must respond to a read)

```
N=3, W=2, R=2: W+R=4 > 3 ✓ (strong consistency)
N=3, W=1, R=1: W+R=2 < 3 ✗ (eventual consistency)
N=3, W=3, R=1: W+R=4 > 3 ✓ (strong consistency, slow writes)
N=3, W=1, R=3: W+R=4 > 3 ✓ (strong consistency, slow reads)
```

**Cassandra's tunable consistency**:
```python
# Fast writes, eventual consistency
session.execute(query, consistency_level=ConsistencyLevel.ONE)

# Balanced (majority must agree)
session.execute(query, consistency_level=ConsistencyLevel.QUORUM)

# Strongest consistency (all nodes must agree)
session.execute(query, consistency_level=ConsistencyLevel.ALL)
```

### Read Repair

When a read detects stale data on a node, it updates that node:

```
Read from Node 1: version=5 (latest)
Read from Node 3: version=3 (stale)

Read repair: send version=5 to Node 3
Node 3 is now up to date
```

---

## 5. Failover

When the leader fails, a follower must be promoted.

### Automatic Failover Steps
1. Detect leader failure (health check timeout)
2. Elect a new leader (the follower with the most up-to-date data)
3. Reconfigure clients to send writes to new leader
4. Old leader (if it recovers) must become a follower

### Failover Problems

**Split brain**: Two nodes both think they're the leader.
```
Network partition:
  Old leader: "I'm still the leader!"
  New leader: "I'm the new leader!"
  Both accept writes → data diverges
```

**Solution**: Fencing tokens. Only the leader with the highest token can write.

**Data loss**: If asynchronous replication, the new leader may not have all writes from the old leader.

**Solution**: Semi-synchronous replication (at least one follower is always synchronous).

---

## 6. Replication in Practice

### PostgreSQL Streaming Replication
```sql
-- On primary: postgresql.conf
wal_level = replica
max_wal_senders = 3
synchronous_standby_names = 'standby1'  -- Semi-sync

-- On replica: recovery.conf
primary_conninfo = 'host=primary port=5432'
hot_standby = on  -- Allow reads on replica
```

### Monitoring Replication Lag
```sql
-- On primary: check replication lag
SELECT
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    (sent_lsn - replay_lsn) AS replication_lag_bytes
FROM pg_stat_replication;
```

---

## References
- DDIA Chapter 5: Replication (the definitive reference)
- [PostgreSQL Replication Documentation](https://www.postgresql.org/docs/current/warm-standby.html)
- [Cassandra Replication](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html)
