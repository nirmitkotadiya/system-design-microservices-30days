# Day 10: Partitioning & Sharding — Concepts Deep Dive

## 1. Why Shard?

Read replicas solve read scaling. But what about write scaling?

```
Problem:
  Single primary DB: 10,000 writes/second (at capacity)
  Adding read replicas doesn't help — writes still go to one node

Solution: Sharding
  Shard 1: handles users A-M (5,000 writes/second)
  Shard 2: handles users N-Z (5,000 writes/second)
  Total: 10,000 writes/second across 2 shards
```

Sharding also solves the dataset size problem:
```
Single DB: 10TB limit (hardware constraint)
4 shards: 2.5TB each → effectively 10TB total
```

**When to shard**:
- Write throughput exceeds what a single primary can handle
- Dataset is too large for one machine
- You've exhausted vertical scaling options
- You've added read replicas and writes are still the bottleneck

**When NOT to shard** (yet):
- You haven't tried read replicas
- You haven't tried caching
- You haven't tried query optimization
- You haven't tried vertical scaling

> **DDIA Reference**: Chapter 6 covers partitioning in depth. Kleppmann distinguishes between partitioning for query load and partitioning for data size.

---

## 2. Sharding Strategy 1: Range-Based Sharding

Divide data by ranges of the shard key.

```
Shard 1: user_id 1 – 1,000,000
Shard 2: user_id 1,000,001 – 2,000,000
Shard 3: user_id 2,000,001 – 3,000,000
```

**Pros**:
- Range queries are efficient (all data in a range is on one shard)
- Easy to understand and implement
- Easy to add new shards at the end

**Cons**:
- Hot shards: if new users are always in the highest range, Shard 3 gets all the writes
- Uneven distribution: some ranges may have more data than others

**Best for**: Time-series data (shard by date range), where you query recent data most

```sql
-- Range sharding by date
Shard 1: events WHERE created_at < '2024-01-01'
Shard 2: events WHERE created_at BETWEEN '2024-01-01' AND '2024-06-30'
Shard 3: events WHERE created_at > '2024-06-30'
```

---

## 3. Sharding Strategy 2: Hash-Based Sharding

Apply a hash function to the shard key to determine which shard.

```python
def get_shard(user_id: int, num_shards: int) -> int:
    return hash(user_id) % num_shards

# user_id=123 → hash(123) % 4 = 3 → Shard 3
# user_id=456 → hash(456) % 4 = 0 → Shard 0
# user_id=789 → hash(789) % 4 = 1 → Shard 1
```

**Pros**:
- Even distribution of data (hash functions distribute uniformly)
- No hot shards (assuming uniform key distribution)

**Cons**:
- Range queries require hitting all shards
- Resharding is painful (changing num_shards changes all assignments)

**The Resharding Problem**:
```
Before: 4 shards
  user_id=123 → hash(123) % 4 = 3 → Shard 3

After adding a 5th shard:
  user_id=123 → hash(123) % 5 = 3 → Shard 3 (same, lucky)
  user_id=456 → hash(456) % 5 = 1 → Shard 1 (was Shard 0!)

Most data needs to move when you add a shard!
```

**Solution**: Consistent hashing (Day 11)

---

## 4. Sharding Strategy 3: Directory-Based Sharding

A lookup table maps each key to a shard.

```
Lookup Table:
  user_id 1-1000 → Shard 1
  user_id 1001-5000 → Shard 2
  user_id 5001-10000 → Shard 1  (rebalanced)
  user_id 10001+ → Shard 3
```

**Pros**:
- Maximum flexibility (can move data between shards without changing the algorithm)
- Easy to rebalance

**Cons**:
- Lookup table is a single point of failure
- Lookup table must be cached (adds latency)
- Complexity of maintaining the lookup table

**Best for**: Systems that need fine-grained control over data placement

---

## 5. Choosing a Shard Key

The shard key is the most important decision in sharding. A bad shard key causes hot shards.

### What Makes a Good Shard Key?

1. **High cardinality**: Many distinct values (user_id: good, country: bad)
2. **Even distribution**: Values are uniformly distributed
3. **Matches access patterns**: Data you access together is on the same shard
4. **Immutable**: The shard key shouldn't change (moving data between shards is expensive)

### Common Shard Key Choices

| System | Shard Key | Why |
|--------|-----------|-----|
| User data | user_id | High cardinality, even distribution |
| Messages | conversation_id | Messages in a conversation are accessed together |
| Orders | user_id | User's orders are accessed together |
| Events | (user_id, date) | Composite key for time-series per user |
| Posts | post_id | Even distribution, posts accessed individually |

### The Celebrity Problem

If you shard by user_id, and a celebrity has 100M followers, their data might be accessed 1000x more than average users.

```
Shard 3: user_id=celebrity → 1M reads/second
Shard 1: user_id=regular_user → 100 reads/second

Shard 3 is a hot shard!
```

**Solutions**:
- Split the celebrity's data across multiple shards
- Cache celebrity data aggressively
- Use a separate "celebrity" tier

---

## 6. Hot Shards

A hot shard receives disproportionately more traffic than other shards.

### Causes
1. **Uneven key distribution**: Some keys are accessed much more than others
2. **Sequential keys**: New data always goes to the same shard (range sharding)
3. **Celebrity/viral content**: One piece of content gets massive traffic

### Detection
```sql
-- Monitor shard load
SELECT shard_id, COUNT(*) as request_count
FROM shard_metrics
WHERE timestamp > NOW() - INTERVAL '1 minute'
GROUP BY shard_id
ORDER BY request_count DESC;
```

### Solutions
1. **Re-shard**: Split the hot shard into multiple shards
2. **Cache**: Add a caching layer in front of the hot shard
3. **Read replicas**: Add read replicas to the hot shard
4. **Better shard key**: Choose a key with more even distribution

---

## 7. Cross-Shard Queries

The biggest operational challenge with sharding.

### The Problem
```sql
-- This query is easy on a single database:
SELECT u.name, COUNT(o.id) as order_count
FROM users u
JOIN orders o ON o.user_id = u.id
GROUP BY u.id
ORDER BY order_count DESC
LIMIT 10;

-- With sharding, users and orders might be on different shards!
-- You'd need to:
-- 1. Query all user shards
-- 2. Query all order shards
-- 3. Join the results in application code
-- 4. Sort and paginate in application code
```

### Strategies

**Avoid cross-shard queries by design**:
- Shard related data together (users and their orders on the same shard)
- Denormalize data to avoid joins

**Scatter-gather**:
```python
def get_top_users_by_orders():
    # Query all shards in parallel
    results = []
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(query_shard, shard_id, "SELECT user_id, COUNT(*) FROM orders GROUP BY user_id")
            for shard_id in range(NUM_SHARDS)
        ]
        for future in futures:
            results.extend(future.result())

    # Merge and sort in application
    return sorted(results, key=lambda x: x['count'], reverse=True)[:10]
```

**Dedicated analytics database**:
- Keep sharded DB for transactional queries
- Replicate all data to a single analytics DB (or data warehouse)
- Run complex queries on the analytics DB

---

## 8. Resharding

Adding new shards when you need more capacity.

### The Challenge
```
Before: 4 shards, 1TB each
After: 8 shards, 500GB each

Problem: Must move 50% of data from each old shard to new shards
         During migration, data is in two places
         Must handle reads/writes during migration
```

### Online Resharding Strategy
1. Create new shards
2. Start dual-writing to old and new shards
3. Backfill old data to new shards
4. Verify data consistency
5. Switch reads to new shards
6. Stop writing to old shards
7. Delete old shards

This is complex and risky. Consistent hashing (Day 11) minimizes data movement.

---

## References
- DDIA Chapter 6: Partitioning
- [Vitess: MySQL Sharding at YouTube](https://vitess.io/)
- [Citus: PostgreSQL Sharding](https://www.citusdata.com/)
