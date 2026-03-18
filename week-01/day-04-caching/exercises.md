# Day 4: Exercises — Caching Strategies

---

## Exercise 1: Basic Comprehension (15 minutes)

1. Your cache has a 95% hit rate. Your database query takes 50ms. Your cache lookup takes 1ms. What is the average response time? (Show your math.)

2. You're using cache-aside. A user updates their profile. What must you do to the cache? What could go wrong if you don't?

3. You have a leaderboard that updates every 5 minutes. What TTL would you set? What eviction policy makes sense?

4. Explain the difference between cache invalidation and cache eviction. Give an example of each.

5. A colleague says "let's cache everything with a 24-hour TTL." What are the risks of this approach?

---

## Exercise 2: Hands-On — Redis Caching (30 minutes)

Start Redis:
```bash
docker run -d -p 6379:6379 redis
```

Run the caching demo:
```bash
cd code-examples/
pip install redis
python caching_patterns.py
```

Observe:
1. The difference in response time between cache hit and cache miss
2. How TTL affects cache behavior
3. The cache stampede simulation and how the mutex prevents it

---

## Exercise 3: Design Problem (25 minutes)

### Scenario: Social Media Feed

Design the caching strategy for a Twitter-like feed:
- Each user follows up to 1,000 accounts
- Feed shows the 50 most recent posts from followed accounts
- Posts are created at a rate of 10,000/second globally
- 100 million daily active users
- 80% of users check their feed within 1 hour of a post being created

**Design**:
1. What do you cache? (The feed itself? Individual posts? Both?)
2. What's the cache key structure?
3. What TTL do you use?
4. When a new post is created, how do you update the cache?
5. How do you handle a celebrity with 10M followers posting? (Fan-out problem)

---

## Exercise 4: Critical Thinking — Strategy Selection (20 minutes)

For each scenario, choose the best caching strategy and justify:

| Scenario | Cache-Aside | Write-Through | Write-Back | Write-Around |
|----------|-------------|---------------|------------|--------------|
| User profile (reads 100x more than writes) | | | | |
| Shopping cart (must not lose data) | | | | |
| Page view counter (can lose some counts) | | | | |
| Audit log (write once, rarely read) | | | | |
| Real-time game score (updates every second) | | | | |

---

## Exercise 5: Challenge — Design a Distributed Cache (35 minutes)

You need to build a distributed cache for a system with:
- 10 app servers
- 3 cache nodes (Redis)
- 1TB of cacheable data
- 500,000 cache operations per second

**Design challenges**:

1. **Data distribution**: How do you decide which cache node stores which keys? (Hint: consistent hashing — we'll cover this on Day 11, but think about it now)

2. **Cache node failure**: If one of your 3 cache nodes goes down, what happens? How do you handle it?

3. **Hot keys**: 1% of your keys receive 50% of the traffic. How do you prevent these from overwhelming a single cache node?

4. **Cache warming**: You deploy a new cache node. It starts empty. How do you prevent a flood of cache misses while it warms up?

5. **Monitoring**: What metrics would you track to know if your cache is healthy?

---

## Hints

**Exercise 1**: Average = (hit_rate × cache_latency) + (miss_rate × db_latency)

**Exercise 3**: Think about the fan-out problem. When a celebrity posts, do you update 10M cache entries immediately?

**Exercise 5, Q3**: Think about replicating hot keys across multiple nodes.

---

## Self-Assessment Checklist

- [ ] I can calculate average response time given hit rate and latencies
- [ ] I understand the difference between cache-aside and write-through
- [ ] I know what a cache stampede is and can describe a prevention strategy
- [ ] I can design a caching strategy for a social media feed
- [ ] I understand LRU vs. LFU eviction
- [ ] I know when NOT to cache something
