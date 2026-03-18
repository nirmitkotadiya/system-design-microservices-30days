# Twitter — Scale Considerations

## Current Scale
- 500M tweets/day = 6,000 tweets/second
- 300B timeline reads/day = 3.5M reads/second
- 200M DAU

## Handling 100x Growth (50B tweets/day)

### Write Path (600,000 tweets/second)

**Current bottleneck**: Cassandra write throughput  
**Solution**: Increase Cassandra cluster size (linear scaling)

```
Current: 100 Cassandra nodes, 6,000 writes/second
100x: 10,000 Cassandra nodes, 600,000 writes/second
```

Cassandra scales linearly — this is achievable.

### Fan-out Service (600,000 × avg_followers writes/second)

**Current**: 6,000 tweets/second × 200 avg followers = 1.2M fan-out writes/second  
**100x**: 120M fan-out writes/second

**Solution**: 
1. More fan-out workers (Kafka consumer group, add more consumers)
2. Batch fan-out writes
3. Lower the celebrity threshold (skip fan-out for users with > 100k followers instead of 1M)

### Timeline Cache (350M reads/second)

**Current**: 3.5M reads/second → ~100 Redis nodes  
**100x**: 350M reads/second → ~10,000 Redis nodes

**Alternative**: Tiered caching
- L1: Local cache in app server (most popular timelines)
- L2: Redis cluster
- L3: Cassandra (cold storage)

### Search (Elasticsearch)

**Current**: Elasticsearch cluster handles tweet indexing  
**100x**: Need to shard Elasticsearch more aggressively

**Solution**: Partition by time (recent tweets in hot shards, old tweets in cold shards)

## The Real Scaling Challenge: The Celebrity Problem

At 100x scale, a celebrity with 100M followers posting a tweet generates:
- 100M fan-out writes
- At 6,000 tweets/second from celebrities: 600B writes/second

**This is impossible with fan-out on write.**

**Solution**: Dynamic threshold
- Monitor follower count in real-time
- Automatically switch users above threshold to fan-out on read
- Threshold adjusts based on system load

## Geographic Distribution

At 100x scale, you need multiple data centers:

```
US East (primary):
  - All writes go here
  - Replication to other regions

EU (replica):
  - Serves EU users
  - Replication lag: ~100ms

APAC (replica):
  - Serves Asia-Pacific users
  - Replication lag: ~200ms
```

**Challenge**: EU data residency regulations require EU user data to stay in EU.  
**Solution**: Shard by user geography. EU users' data stored in EU data center.
