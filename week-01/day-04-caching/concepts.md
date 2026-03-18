# Day 4: Caching Strategies — Concepts Deep Dive

## 1. Why Caching Matters

The speed difference between storage layers is enormous:

```
L1 CPU Cache:     ~1 nanosecond
L2 CPU Cache:     ~4 nanoseconds
RAM (Redis):      ~100 microseconds   (100,000x slower than L1)
SSD (local):      ~100 microseconds
Network (LAN):    ~1 millisecond      (1,000,000x slower than L1)
HDD:              ~10 milliseconds
Database query:   ~10-100 milliseconds
```

A cache hit (serving from Redis) is 100-1000x faster than a database query. If 90% of your requests are cache hits, you've effectively made your system 10-100x faster.

> **Real World**: Facebook's Memcached deployment handles over 1 billion requests per second. Without caching, their MySQL databases would be completely overwhelmed.

---

## 2. Cache Terminology

**Cache Hit**: The requested data is in the cache. Fast path.  
**Cache Miss**: The data isn't in the cache. Must fetch from the source.  
**Cache Hit Rate**: Percentage of requests served from cache. Target: 80-95%+  
**Cache Eviction**: Removing data from cache to make room for new data.  
**Cache Invalidation**: Explicitly removing or updating stale data.  
**TTL (Time To Live)**: How long a cache entry is valid before expiring.

---

## 3. Cache-Aside (Lazy Loading)

The most common pattern. The application manages the cache explicitly.

```
READ:
1. App checks cache for key
2. Cache HIT → return cached value
3. Cache MISS → fetch from DB, store in cache, return value

WRITE:
1. App writes to DB
2. App invalidates (deletes) the cache entry
   (Next read will repopulate from DB)
```

```python
def get_user(user_id: int) -> dict:
    # 1. Check cache
    cached = redis.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)  # Cache HIT

    # 2. Cache MISS — fetch from DB
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)

    # 3. Store in cache with TTL
    redis.setex(f"user:{user_id}", 3600, json.dumps(user))

    return user

def update_user(user_id: int, data: dict):
    db.execute("UPDATE users SET ... WHERE id = ?", user_id)
    redis.delete(f"user:{user_id}")  # Invalidate cache
```

**Pros**:
- Only caches what's actually requested (no wasted memory)
- Cache failures don't break the app (falls back to DB)
- Works well for read-heavy workloads

**Cons**:
- Cache miss penalty (3 operations instead of 1)
- Potential for stale data between write and invalidation
- Cache stampede risk (see section 7)

---

## 4. Write-Through

Every write goes to both the cache and the database simultaneously.

```
WRITE:
1. App writes to cache
2. Cache synchronously writes to DB
3. Both are updated atomically

READ:
1. App checks cache
2. Cache HIT → return (always fresh)
3. Cache MISS → fetch from DB (rare, only on cold start)
```

```python
def update_user(user_id: int, data: dict):
    # Write to both simultaneously
    db.execute("UPDATE users SET ... WHERE id = ?", user_id)
    redis.setex(f"user:{user_id}", 3600, json.dumps(data))
```

**Pros**:
- Cache is always consistent with DB
- No stale reads
- Low read latency (always in cache)

**Cons**:
- Write latency is higher (must write to both)
- Cache fills up with data that may never be read
- If DB write fails, cache and DB are inconsistent

**Best for**: Read-heavy workloads where data freshness is critical

---

## 5. Write-Back (Write-Behind)

Writes go to cache first, then asynchronously to the database.

```
WRITE:
1. App writes to cache
2. Return success immediately
3. Background process writes to DB asynchronously

READ:
1. App checks cache
2. Cache HIT → return (always fresh)
```

```
Timeline:
t=0: Write to cache → return success
t=5s: Background job writes to DB
```

**Pros**:
- Lowest write latency (only writes to cache)
- Can batch multiple writes to DB
- Great for write-heavy workloads

**Cons**:
- Risk of data loss if cache fails before DB write
- More complex implementation
- Harder to reason about consistency

**Best for**: Write-heavy workloads where some data loss is acceptable (analytics, counters)

---

## 6. Write-Around

Writes go directly to the database, bypassing the cache. Cache is only populated on reads.

```
WRITE: App → DB (cache not updated)
READ:  App → Cache MISS → DB → populate cache
```

**Best for**: Data that is written once and rarely read (logs, audit trails)

---

## 7. Cache Eviction Policies

When the cache is full, something must be removed. The policy determines what.

### LRU (Least Recently Used)
Remove the item that hasn't been accessed for the longest time.

```
Cache state: [A(t=1), B(t=5), C(t=3), D(t=8)]
Cache full, need to add E
LRU evicts: A (accessed at t=1, oldest)
```

**Best for**: General-purpose caching. Works well when recent access predicts future access.

### LFU (Least Frequently Used)
Remove the item that has been accessed the fewest times.

```
Cache state: [A(count=10), B(count=2), C(count=7), D(count=1)]
Cache full, need to add E
LFU evicts: D (accessed only 1 time)
```

**Best for**: When some items are consistently more popular than others.

### TTL (Time To Live)
Items expire after a fixed time, regardless of access patterns.

```python
redis.setex("user:123", 3600, json.dumps(user))  # Expires in 1 hour
```

**Best for**: Data with a known freshness requirement (session tokens, rate limit counters)

### FIFO (First In, First Out)
Remove the oldest item regardless of access patterns.

**Best for**: Simple use cases, not recommended for general caching.

---

## 8. Cache Stampede (Thundering Herd)

**The Problem**: A popular cache entry expires. Suddenly, 1000 concurrent requests all get a cache miss and all try to fetch from the database simultaneously.

```
t=0: Cache entry for "trending_posts" expires
t=0.001: 1000 requests arrive, all get cache miss
t=0.001: 1000 requests all query the database
t=0.5: Database is overwhelmed, latency spikes
```

### Solution 1: Mutex/Lock
Only one request fetches from DB. Others wait.

```python
def get_trending_posts():
    cached = redis.get("trending_posts")
    if cached:
        return json.loads(cached)

    # Try to acquire lock
    lock = redis.set("trending_posts:lock", 1, nx=True, ex=10)
    if lock:
        # We got the lock — fetch from DB
        posts = db.query("SELECT * FROM posts ORDER BY likes DESC LIMIT 20")
        redis.setex("trending_posts", 300, json.dumps(posts))
        redis.delete("trending_posts:lock")
        return posts
    else:
        # Another request is fetching — wait and retry
        time.sleep(0.1)
        return get_trending_posts()
```

### Solution 2: Probabilistic Early Expiration
Randomly refresh the cache before it expires.

```python
def get_with_early_refresh(key: str, ttl: int, fetch_fn):
    value, remaining_ttl = redis.get_with_ttl(key)
    if value is None:
        # Cache miss — fetch and store
        value = fetch_fn()
        redis.setex(key, ttl, value)
    elif remaining_ttl < ttl * 0.1:
        # Within 10% of expiry — probabilistically refresh
        if random.random() < 0.1:  # 10% chance
            value = fetch_fn()
            redis.setex(key, ttl, value)
    return value
```

### Solution 3: Background Refresh
A background job refreshes the cache before it expires.

---

## 9. Cache Levels

### Client-Side Cache (Browser)
```http
Cache-Control: public, max-age=86400
ETag: "abc123"
```
Fastest possible — no network call at all.

### CDN Cache
Geographically distributed. Reduces latency for static assets.

### Application Cache (Redis/Memcached)
Shared across all app servers. Most flexible.

### Database Query Cache
Built into some databases. Caches query results.

---

## 10. What NOT to Cache

- **User-specific sensitive data** (unless encrypted and properly keyed)
- **Frequently changing data** (cache invalidation becomes a nightmare)
- **Data that must be strongly consistent** (financial transactions)
- **Very large objects** (wastes cache memory)
- **Data that's cheap to compute** (caching overhead isn't worth it)

---

## 11. Redis vs. Memcached

| Feature | Redis | Memcached |
|---------|-------|-----------|
| Data structures | Strings, lists, sets, hashes, sorted sets | Strings only |
| Persistence | Optional (RDB, AOF) | None |
| Replication | Yes | No |
| Clustering | Yes | Yes |
| Pub/Sub | Yes | No |
| Lua scripting | Yes | No |
| Use case | General purpose | Simple key-value cache |

**Choose Redis** for almost everything. Memcached is only faster for simple string caching at extreme scale.

---

## References
- DDIA Chapter 3: Storage and Retrieval (discusses caching in storage engines)
- [Redis Documentation](https://redis.io/docs/)
- [Facebook's Memcached Paper](https://research.facebook.com/publications/scaling-memcache-at-facebook/)
- [Cache Stampede Prevention](https://redis.io/docs/manual/patterns/distributed-locks/)
