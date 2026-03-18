# Twitter Component: Timeline Service

## Overview

The timeline service is the heart of Twitter. It answers one question: "What tweets should I show this user right now?"

This is deceptively hard. Twitter has ~350 million users, each following hundreds of accounts, with ~500 million tweets posted per day.

---

## The Two Approaches

### Fan-out on Write (Push Model)

When a user tweets, immediately write that tweet to every follower's timeline cache.

```
User A (100 followers) tweets:
  → Write tweet to follower 1's timeline cache
  → Write tweet to follower 2's timeline cache
  → ...
  → Write tweet to follower 100's timeline cache

Read timeline:
  → Just read from cache (O(1), very fast)
```

**Pros**: Reads are instant (pre-computed)
**Cons**: Writes are expensive. A celebrity with 10M followers creates 10M cache writes per tweet.

### Fan-out on Read (Pull Model)

When a user requests their timeline, fetch tweets from everyone they follow.

```
User reads timeline:
  → Get list of 500 accounts they follow
  → Fetch recent tweets from each account
  → Merge and sort by timestamp
  → Return top 20

Write tweet:
  → Just store the tweet (O(1))
```

**Pros**: Writes are cheap
**Cons**: Reads are expensive. Following 500 accounts = 500 database queries per timeline load.

---

## Twitter's Hybrid Approach

Twitter uses a hybrid model based on follower count:

```python
CELEBRITY_THRESHOLD = 1_000_000  # followers

def on_tweet(tweet, author):
    if author.follower_count < CELEBRITY_THRESHOLD:
        # Fan-out on write: push to all followers' caches
        for follower_id in get_followers(author.id):
            timeline_cache.prepend(follower_id, tweet)
    else:
        # Don't fan-out for celebrities
        # Store tweet normally, fetch at read time
        tweet_store.save(tweet)

def get_timeline(user_id):
    # Start with pre-computed timeline (from fan-out on write)
    timeline = timeline_cache.get(user_id, limit=800)
    
    # Inject celebrity tweets at read time
    celebrity_follows = get_celebrity_follows(user_id)
    for celebrity_id in celebrity_follows:
        celebrity_tweets = tweet_store.get_recent(celebrity_id, limit=20)
        timeline.extend(celebrity_tweets)
    
    # Sort and return top N
    return sorted(timeline, key=lambda t: t.timestamp, reverse=True)[:20]
```

---

## Timeline Cache Design

```
Redis data model:
  Key: "timeline:{user_id}"
  Type: Sorted Set
  Score: tweet timestamp (Unix epoch)
  Member: tweet_id

Operations:
  ZADD timeline:1001 1704067200 tweet:9999  # Add tweet
  ZREVRANGE timeline:1001 0 19              # Get latest 20
  ZREMRANGEBYRANK timeline:1001 0 -801      # Keep only 800 most recent

Memory per user:
  800 tweets × (8 bytes tweet_id + 8 bytes score) = ~12.8 KB
  350M users × 12.8 KB = ~4.5 TB total
  (Only cache active users — ~50M DAU × 12.8 KB = ~640 GB)
```

---

## Handling Edge Cases

**New user with no tweets in cache**: Fall back to pull model, populate cache.

**User comes back after 30 days**: Cache is stale/empty. Rebuild from tweet store.

**Tweet deletion**: Must remove from all timeline caches. For non-celebrities, this means finding all followers and removing from their caches. Expensive but rare.

**Retweets**: Treated like original tweets for fan-out purposes.

---

## Interview Talking Points

- Start with the naive approach (pull model), explain why it doesn't scale
- Introduce fan-out on write, explain the celebrity problem
- Propose the hybrid model
- Discuss cache eviction (keep only 800 tweets per user)
- Mention that Twitter actually uses this hybrid approach in production
