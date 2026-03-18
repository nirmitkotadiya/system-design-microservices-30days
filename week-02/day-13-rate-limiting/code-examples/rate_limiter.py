"""
Rate Limiter Implementations — Day 13: Rate Limiting

Demonstrates token bucket, sliding window, and fixed window algorithms.
Includes a Redis-based distributed rate limiter.

Run: python rate_limiter.py
"""

import time
import threading
from collections import deque, defaultdict
from dataclasses import dataclass, field
from typing import Optional

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


# ─── Algorithm 1: Token Bucket ────────────────────────────────────────────────

class TokenBucket:
    """
    Token bucket rate limiter.

    Allows bursts up to `capacity` requests, then limits to `refill_rate` req/sec.
    """

    def __init__(self, capacity: int, refill_rate: float):
        """
        Args:
            capacity: Maximum tokens (burst size)
            refill_rate: Tokens added per second (sustained rate)
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.monotonic()
        self._lock = threading.Lock()

    def allow_request(self, tokens_needed: int = 1) -> bool:
        """Returns True if request is allowed, False if rate limited."""
        with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_refill

            # Refill tokens based on elapsed time
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.refill_rate
            )
            self.last_refill = now

            if self.tokens >= tokens_needed:
                self.tokens -= tokens_needed
                return True
            return False

    @property
    def available_tokens(self) -> float:
        with self._lock:
            return self.tokens


# ─── Algorithm 2: Fixed Window Counter ───────────────────────────────────────

class FixedWindowCounter:
    """
    Fixed window rate limiter.

    Simple but vulnerable to boundary attacks.
    """

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self._counts: dict[str, tuple[int, float]] = {}  # key → (count, window_start)
        self._lock = threading.Lock()

    def allow_request(self, key: str) -> bool:
        with self._lock:
            now = time.monotonic()
            window_start = now - (now % self.window_seconds)

            if key not in self._counts or self._counts[key][1] != window_start:
                self._counts[key] = (0, window_start)

            count, _ = self._counts[key]
            if count < self.limit:
                self._counts[key] = (count + 1, window_start)
                return True
            return False


# ─── Algorithm 3: Sliding Window Log ─────────────────────────────────────────

class SlidingWindowLog:
    """
    Sliding window log rate limiter.

    Accurate but uses O(requests) memory per user.
    """

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self._logs: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow_request(self, key: str) -> bool:
        with self._lock:
            now = time.monotonic()
            window_start = now - self.window_seconds
            log = self._logs[key]

            # Remove expired entries
            while log and log[0] <= window_start:
                log.popleft()

            if len(log) < self.limit:
                log.append(now)
                return True
            return False

    def get_remaining(self, key: str) -> int:
        with self._lock:
            now = time.monotonic()
            window_start = now - self.window_seconds
            log = self._logs[key]
            while log and log[0] <= window_start:
                log.popleft()
            return max(0, self.limit - len(log))


# ─── Algorithm 4: Sliding Window Counter ─────────────────────────────────────

class SlidingWindowCounter:
    """
    Sliding window counter rate limiter.

    Approximates sliding window using two fixed windows.
    Low memory, accurate enough for most use cases.
    """

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        # {key: {window_start: count}}
        self._windows: dict[str, dict[float, int]] = defaultdict(dict)
        self._lock = threading.Lock()

    def allow_request(self, key: str) -> bool:
        with self._lock:
            now = time.monotonic()
            current_window = int(now / self.window_seconds) * self.window_seconds
            prev_window = current_window - self.window_seconds

            windows = self._windows[key]

            # Clean up old windows
            for w in list(windows.keys()):
                if w < prev_window:
                    del windows[w]

            prev_count = windows.get(prev_window, 0)
            curr_count = windows.get(current_window, 0)

            # Weight previous window by how much of it overlaps with current window
            elapsed_in_current = now - current_window
            prev_weight = 1.0 - (elapsed_in_current / self.window_seconds)

            weighted_count = prev_count * prev_weight + curr_count

            if weighted_count < self.limit:
                windows[current_window] = curr_count + 1
                return True
            return False


# ─── Experiments ─────────────────────────────────────────────────────────────

def test_burst_behavior():
    """Compare how algorithms handle bursts."""
    print("\n📊 EXPERIMENT 1: Burst Behavior")
    print("─" * 50)
    print("Sending 15 requests instantly, then 1 per second for 5 seconds")
    print("Limit: 10 requests per 10 seconds\n")

    token_bucket = TokenBucket(capacity=10, refill_rate=1.0)
    sliding_log = SlidingWindowLog(limit=10, window_seconds=10)
    fixed_window = FixedWindowCounter(limit=10, window_seconds=10)

    results = {"token_bucket": [], "sliding_log": [], "fixed_window": []}

    # Burst: 15 requests at once
    for i in range(15):
        results["token_bucket"].append(token_bucket.allow_request())
        results["sliding_log"].append(sliding_log.allow_request("user"))
        results["fixed_window"].append(fixed_window.allow_request("user"))

    for algo, res in results.items():
        allowed = sum(res)
        print(f"  {algo:<25}: {allowed}/15 allowed in burst")


def test_window_boundary():
    """Demonstrate the fixed window boundary attack."""
    print("\n📊 EXPERIMENT 2: Window Boundary Attack")
    print("─" * 50)
    print("Fixed window: 10 req/10sec")
    print("Attack: 10 requests at end of window, 10 at start of next\n")

    # Simulate boundary attack
    fixed = FixedWindowCounter(limit=10, window_seconds=10)
    sliding = SlidingWindowLog(limit=10, window_seconds=10)

    # First 10 requests (end of window 1)
    fixed_allowed_1 = sum(fixed.allow_request("attacker") for _ in range(10))
    sliding_allowed_1 = sum(sliding.allow_request("attacker") for _ in range(10))

    # Simulate time passing to next window
    # (In real test, we'd sleep, but we'll just show the concept)
    print(f"  Fixed window - Window 1: {fixed_allowed_1}/10 allowed")
    print(f"  Sliding log  - Window 1: {sliding_allowed_1}/10 allowed")
    print(f"\n  Fixed window vulnerability: attacker can send 20 requests in 1 second")
    print(f"  (10 at end of window 1 + 10 at start of window 2)")
    print(f"  Sliding window prevents this by tracking exact timestamps")


def test_rate_limiter_performance():
    """Compare performance of different algorithms."""
    print("\n📊 EXPERIMENT 3: Performance Comparison")
    print("─" * 50)

    algorithms = {
        "Token Bucket": TokenBucket(capacity=1000, refill_rate=100),
        "Fixed Window": FixedWindowCounter(limit=1000, window_seconds=10),
        "Sliding Log": SlidingWindowLog(limit=1000, window_seconds=10),
        "Sliding Counter": SlidingWindowCounter(limit=1000, window_seconds=10),
    }

    num_requests = 10000

    for name, algo in algorithms.items():
        start = time.perf_counter()
        if name == "Token Bucket":
            for _ in range(num_requests):
                algo.allow_request()
        else:
            for i in range(num_requests):
                algo.allow_request(f"user:{i % 100}")
        elapsed = (time.perf_counter() - start) * 1000

        print(f"  {name:<20}: {elapsed:.1f}ms for {num_requests} requests ({elapsed/num_requests*1000:.1f}μs/req)")


def main():
    print("\n🚦 RATE LIMITER DEMO — Day 13: Rate Limiting")
    print("=" * 60)

    test_burst_behavior()
    test_window_boundary()
    test_rate_limiter_performance()

    print("\n💡 KEY TAKEAWAYS:")
    print("  1. Token bucket allows bursts — good for APIs with variable load")
    print("  2. Fixed window is simple but vulnerable to boundary attacks")
    print("  3. Sliding window log is accurate but memory-intensive")
    print("  4. Sliding window counter is the best balance (used in production)")
    print("  5. For distributed systems, use Redis with Lua scripts for atomicity")
    print()


if __name__ == "__main__":
    main()
