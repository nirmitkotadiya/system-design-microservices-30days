# Twitter Design — Tradeoffs

## The Core Tradeoff: Fan-out on Write vs. Fan-out on Read

This is the most important design decision in Twitter's architecture.

### Fan-out on Write (Push Model)
When a tweet is posted, immediately write it to all followers' timeline caches.

```
User posts tweet:
  For each of user's N followers:
    Write tweet_id to follower's timeline cache

Read timeline:
  Read from cache (fast!)
```

**Pros**: Timeline reads are O(1) — just read from cache  
**Cons**: Write amplification — 1 tweet → N cache writes

**Problem**: Celebrity with 10M followers posts a tweet → 10M cache writes!

### Fan-out on Read (Pull Model)
Don't pre-compute timelines. When a user opens the app, fetch tweets from all followed users.

```
User opens app:
  For each of user's M followed accounts:
    Fetch recent tweets

Merge and sort all tweets
```

**Pros**: No write amplification  
**Cons**: Read is expensive — must query M accounts and merge

**Problem**: User follows 1,000 accounts → 1,000 DB queries per timeline load!

### Twitter's Hybrid Approach

```
Regular users (< 1M followers): Fan-out on write
  → Timeline is pre-computed in Redis
  → Fast reads

Celebrity users (> 1M followers): Fan-out on read
  → Don't pre-compute (too expensive)
  → Fetch celebrity tweets at read time and merge with pre-computed timeline
```

```python
def get_timeline(user_id: str) -> list[Tweet]:
    # 1. Get pre-computed timeline from Redis
    timeline_tweet_ids = redis.lrange(f"timeline:{user_id}", 0, 99)

    # 2. Get followed celebrities
    celebrities = get_followed_celebrities(user_id)

    # 3. Fetch celebrity tweets (fan-out on read)
    celebrity_tweets = []
    for celebrity_id in celebrities:
        tweets = cassandra.query(
            "SELECT * FROM tweets WHERE user_id = ? ORDER BY created_at DESC LIMIT 20",
            celebrity_id
        )
        celebrity_tweets.extend(tweets)

    # 4. Merge and sort
    all_tweets = get_tweets_by_ids(timeline_tweet_ids) + celebrity_tweets
    return sorted(all_tweets, key=lambda t: t.created_at, reverse=True)[:20]
```

---

## Database Choices

### Tweets: Cassandra
**Why**: High write throughput (6,000 tweets/second), time-series access pattern (get tweets by user, ordered by time), horizontal scalability

**Alternative considered**: PostgreSQL  
**Why rejected**: Write throughput limit, sharding complexity

### Users: PostgreSQL
**Why**: Complex queries (search by username, email), ACID for account operations, relatively low write volume

**Alternative considered**: MongoDB  
**Why rejected**: User data is relational (followers, following), complex queries benefit from SQL

### Timeline Cache: Redis
**Why**: Sub-millisecond reads, sorted sets for ordered timelines, pub/sub for real-time updates

**Alternative considered**: Memcached  
**Why rejected**: Redis sorted sets are perfect for ordered timelines; Memcached only supports strings

### Search: Elasticsearch
**Why**: Full-text search, real-time indexing, faceted search (by date, user, etc.)

**Alternative considered**: PostgreSQL full-text search  
**Why rejected**: Doesn't scale to 500M tweets; no real-time trending topics

---

## Consistency Tradeoffs

### Timeline Consistency
**Choice**: Eventual consistency  
**Tradeoff**: User might not see a tweet immediately after it's posted  
**Acceptable because**: Twitter is not a financial system; slight delay is acceptable

### Like/Retweet Counts
**Choice**: Approximate counts (Redis counters, periodically synced to DB)  
**Tradeoff**: Count might be slightly off  
**Acceptable because**: Exact counts don't matter; "1,234 likes" vs "1,235 likes" is irrelevant

### Direct Messages
**Choice**: Strong consistency  
**Tradeoff**: Higher latency for DMs  
**Required because**: Users expect messages to be delivered reliably

---

## What Twitter Actually Does

Twitter's actual architecture has evolved significantly:
- Originally: Ruby on Rails monolith
- 2009-2012: Extracted services (Gizzard for sharding, Finagle for RPC)
- 2012+: Scala services, Manhattan (distributed key-value store)
- 2022+: Significant changes after acquisition

The hybrid fan-out approach described here is based on Twitter's 2012-era architecture, which is well-documented and commonly used in interviews.
