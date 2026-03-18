"""
Caching Patterns — Day 4: Caching Strategies

Demonstrates cache-aside, write-through, TTL, and stampede prevention.
Requires Redis running locally: docker run -d -p 6379:6379 redis

Run: python caching_patterns.py
"""

import json
import time
import random
import threading
from typing import Optional, Any

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Redis not installed. Run: pip install redis")
    print("Running in simulation mode...\n")


# ─── Simulated Database ───────────────────────────────────────────────────────

class FakeDatabase:
    """Simulates a slow database with realistic query times."""

    def __init__(self, latency_ms: float = 50.0):
        self.latency_ms = latency_ms
        self.query_count = 0
        self._data = {
            i: {"id": i, "name": f"User {i}", "email": f"user{i}@example.com"}
            for i in range(1, 101)
        }

    def get_user(self, user_id: int) -> Optional[dict]:
        """Simulate a slow DB query."""
        time.sleep(self.latency_ms / 1000.0)
        self.query_count += 1
        return self._data.get(user_id)

    def update_user(self, user_id: int, data: dict):
        """Simulate a DB write."""
        time.sleep(self.latency_ms / 1000.0)
        if user_id in self._data:
            self._data[user_id].update(data)


# ─── Simple In-Memory Cache (for when Redis isn't available) ──────────────────

class SimpleCache:
    """Thread-safe in-memory cache with TTL support."""

    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[str]:
        with self._lock:
            if key in self._store:
                value, expires_at = self._store[key]
                if time.time() < expires_at:
                    return value
                del self._store[key]
        return None

    def setex(self, key: str, ttl: int, value: str):
        with self._lock:
            self._store[key] = (value, time.time() + ttl)

    def delete(self, key: str):
        with self._lock:
            self._store.pop(key, None)

    def set(self, key: str, value: str, nx: bool = False, ex: int = None) -> bool:
        with self._lock:
            if nx and key in self._store:
                return False
            expires_at = time.time() + (ex or 3600)
            self._store[key] = (value, expires_at)
            return True

    def ping(self):
        return True


def get_cache():
    """Get Redis or fallback to in-memory cache."""
    if REDIS_AVAILABLE:
        try:
            r = redis.Redis(host="localhost", port=6379, decode_responses=True)
            r.ping()
            return r
        except Exception:
            pass
    return SimpleCache()


# ─── Pattern 1: Cache-Aside ───────────────────────────────────────────────────

class CacheAsideRepository:
    """Implements the cache-aside (lazy loading) pattern."""

    def __init__(self, db: FakeDatabase, cache, ttl: int = 60):
        self.db = db
        self.cache = cache
        self.ttl = ttl
        self.cache_hits = 0
        self.cache_misses = 0

    def get_user(self, user_id: int) -> Optional[dict]:
        key = f"user:{user_id}"

        # 1. Check cache
        cached = self.cache.get(key)
        if cached:
            self.cache_hits += 1
            return json.loads(cached)

        # 2. Cache miss — fetch from DB
        self.cache_misses += 1
        user = self.db.get_user(user_id)
        if user:
            self.cache.setex(key, self.ttl, json.dumps(user))
        return user

    def update_user(self, user_id: int, data: dict):
        # Write to DB
        self.db.update_user(user_id, data)
        # Invalidate cache
        self.cache.delete(f"user:{user_id}")

    @property
    def hit_rate(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0


# ─── Pattern 2: Stampede Prevention ──────────────────────────────────────────

class StampedePreventionCache:
    """Demonstrates cache stampede and prevention with mutex."""

    def __init__(self, db: FakeDatabase, cache):
        self.db = db
        self.cache = cache
        self.db_calls = 0

    def get_trending_posts_unsafe(self) -> list:
        """UNSAFE: No stampede protection."""
        cached = self.cache.get("trending_posts")
        if cached:
            return json.loads(cached)

        # Simulate expensive DB query
        self.db_calls += 1
        time.sleep(0.1)  # 100ms DB query
        posts = [{"id": i, "title": f"Post {i}"} for i in range(1, 21)]
        self.cache.setex("trending_posts", 1, json.dumps(posts))  # 1s TTL
        return posts

    def get_trending_posts_safe(self) -> list:
        """SAFE: Mutex prevents stampede."""
        cached = self.cache.get("trending_posts_safe")
        if cached:
            return json.loads(cached)

        # Try to acquire lock (only one request fetches from DB)
        lock_acquired = self.cache.set(
            "trending_posts_safe:lock", "1", nx=True, ex=5
        )

        if lock_acquired:
            try:
                # We got the lock — fetch from DB
                self.db_calls += 1
                time.sleep(0.1)
                posts = [{"id": i, "title": f"Post {i}"} for i in range(1, 21)]
                self.cache.setex("trending_posts_safe", 1, json.dumps(posts))
                return posts
            finally:
                self.cache.delete("trending_posts_safe:lock")
        else:
            # Another request is fetching — wait briefly and retry
            time.sleep(0.05)
            cached = self.cache.get("trending_posts_safe")
            if cached:
                return json.loads(cached)
            return []  # Fallback


# ─── Experiments ─────────────────────────────────────────────────────────────

def experiment_cache_aside(cache):
    print("\n📊 EXPERIMENT 1: Cache-Aside Pattern")
    print("─" * 50)

    db = FakeDatabase(latency_ms=50)
    repo = CacheAsideRepository(db, cache, ttl=30)

    # First access — all cache misses
    print("  First pass (cold cache):")
    t0 = time.perf_counter()
    for user_id in [1, 2, 3, 4, 5]:
        repo.get_user(user_id)
    cold_time = (time.perf_counter() - t0) * 1000
    print(f"  5 requests: {cold_time:.0f}ms (all cache misses)")

    # Second access — all cache hits
    print("  Second pass (warm cache):")
    t0 = time.perf_counter()
    for user_id in [1, 2, 3, 4, 5]:
        repo.get_user(user_id)
    warm_time = (time.perf_counter() - t0) * 1000
    print(f"  5 requests: {warm_time:.0f}ms (all cache hits)")
    print(f"  Speedup: {cold_time / max(warm_time, 0.1):.1f}x faster")
    print(f"  Hit rate: {repo.hit_rate:.0%}")
    print(f"  DB queries: {db.query_count} (vs 10 without cache)")


def experiment_stampede(cache):
    print("\n📊 EXPERIMENT 2: Cache Stampede")
    print("─" * 50)

    db = FakeDatabase(latency_ms=50)
    stampede_cache = StampedePreventionCache(db, cache)

    # Clear any existing cache
    cache.delete("trending_posts")
    cache.delete("trending_posts_safe")
    cache.delete("trending_posts_safe:lock")

    # Simulate 20 concurrent requests hitting expired cache
    print("  Simulating 20 concurrent requests (UNSAFE):")
    stampede_cache.db_calls = 0
    threads = [
        threading.Thread(target=stampede_cache.get_trending_posts_unsafe)
        for _ in range(20)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"  DB calls made: {stampede_cache.db_calls} (should be ~20 — stampede!)")

    # Wait for cache to expire
    time.sleep(1.1)

    print("  Simulating 20 concurrent requests (SAFE with mutex):")
    stampede_cache.db_calls = 0
    threads = [
        threading.Thread(target=stampede_cache.get_trending_posts_safe)
        for _ in range(20)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"  DB calls made: {stampede_cache.db_calls} (should be 1 — stampede prevented!)")


def main():
    print("\n🗄️  CACHING PATTERNS DEMO — Day 4: Caching Strategies")
    print("=" * 60)

    cache = get_cache()
    cache_type = "Redis" if REDIS_AVAILABLE else "In-Memory (simulation)"
    print(f"  Using: {cache_type}")

    experiment_cache_aside(cache)
    experiment_stampede(cache)

    print("\n💡 KEY TAKEAWAYS:")
    print("  1. Cache-aside gives 10-100x speedup for read-heavy workloads")
    print("  2. Cache stampede can overwhelm your DB when a popular key expires")
    print("  3. A simple mutex reduces DB calls from N to 1 during stampede")
    print("  4. Always measure hit rate — below 80% means your cache isn't helping")
    print()


if __name__ == "__main__":
    main()
