# Day 13: Exercises — Rate Limiting

---

## Exercise 1: Basic Comprehension (15 minutes)

1. A token bucket has capacity=10, refill_rate=2/second. At t=0, the bucket is full. 15 requests arrive at t=0. How many are allowed? How many are rejected?

2. What is the "window boundary attack" on fixed window rate limiting? Give a concrete example.

3. Why is Redis a good choice for distributed rate limiting? What property of Redis makes it safe for concurrent rate limit checks?

4. What HTTP status code should you return when a client is rate limited? What headers should you include?

5. You're rate limiting login attempts to prevent brute force attacks. Should you rate limit by user_id, by IP address, or both? What are the tradeoffs?

---

## Exercise 2: Algorithm Implementation (30 minutes)

Implement a sliding window counter rate limiter in Python (without Redis — use in-memory):

```python
import time
from collections import deque
from threading import Lock

class SlidingWindowRateLimiter:
    """
    Sliding window log rate limiter.
    Allows `limit` requests per `window_seconds`.
    """

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        # Store per-user request timestamps
        self._windows: dict[str, deque] = {}
        self._lock = Lock()

    def is_allowed(self, user_id: str) -> bool:
        """
        Returns True if the request is allowed, False if rate limited.
        """
        # Your implementation here
        pass

    def get_remaining(self, user_id: str) -> int:
        """Returns how many requests the user has remaining in the current window."""
        # Your implementation here
        pass
```

Test your implementation:
```python
limiter = SlidingWindowRateLimiter(limit=5, window_seconds=10)

# Should allow 5 requests
for i in range(5):
    assert limiter.is_allowed("user:1") == True, f"Request {i+1} should be allowed"

# 6th request should be rejected
assert limiter.is_allowed("user:1") == False, "6th request should be rejected"

# Different user should be unaffected
assert limiter.is_allowed("user:2") == True, "Different user should be allowed"

print("All tests passed!")
```

---

## Exercise 3: Design Rate Limiting Rules (25 minutes)

### Scenario: Public REST API

You're designing rate limiting for a public API (like Twitter's API):

**API Endpoints**:
- `GET /tweets/{id}` — Read a tweet
- `POST /tweets` — Create a tweet
- `GET /users/{id}/timeline` — Get user's timeline
- `POST /auth/login` — Login
- `GET /search` — Search tweets

**User Tiers**:
- Free: Basic access
- Developer: Higher limits
- Enterprise: Very high limits

**Design the rate limiting rules**:

| Endpoint | Free | Developer | Enterprise | Rationale |
|----------|------|-----------|------------|-----------|
| GET /tweets/{id} | ? | ? | ? | ? |
| POST /tweets | ? | ? | ? | ? |
| GET /timeline | ? | ? | ? | ? |
| POST /auth/login | ? | ? | ? | ? |
| GET /search | ? | ? | ? | ? |

Also answer:
1. Should you rate limit by user_id, API key, or IP? (Different for each endpoint?)
2. How do you handle unauthenticated requests?
3. What's your strategy for the login endpoint specifically?

---

## Exercise 4: Distributed Rate Limiter Design (20 minutes)

### Scenario

You have 20 API servers behind a load balancer. You need to rate limit users to 100 requests/minute.

**Problem**: Each server only sees 1/20 of the traffic. If you rate limit locally, each server allows 100 req/min, but the user can actually make 2,000 req/min (100 × 20 servers).

**Design a distributed rate limiter**:
1. Where does the rate limit state live?
2. How do you handle the case where Redis is down?
3. How do you minimize latency added by rate limiting?
4. How do you handle rate limiting across multiple data centers?

---

## Exercise 5: Challenge — Design a Rate Limiter for a Payment API (35 minutes)

### Scenario

You're designing rate limiting for a payment processing API:
- Endpoint: `POST /payments`
- Normal usage: 10 payments/minute per merchant
- Fraud pattern: 1000 payments/minute from a compromised merchant account
- Legitimate burst: A merchant runs a flash sale and needs 500 payments/minute for 5 minutes

**The tension**: Too strict = legitimate merchants can't process payments. Too loose = fraud goes undetected.

**Design**:

1. **Normal rate limit**: What's the base rate limit? How do you set it?

2. **Burst allowance**: How do you allow legitimate bursts without enabling fraud? (Hint: token bucket with large capacity)

3. **Anomaly detection**: How do you detect when a merchant's rate suddenly spikes 100x? What do you do?

4. **Graduated response**: Instead of hard blocking, design a graduated response:
   - 0-10 req/min: Normal
   - 10-50 req/min: Add CAPTCHA
   - 50-200 req/min: Require additional verification
   - 200+ req/min: Block and alert fraud team

5. **Merchant-specific limits**: Some merchants legitimately process more payments. How do you handle custom limits?

---

## Hints

**Exercise 2**: Use `deque` to store timestamps. Remove timestamps older than `window_seconds` before counting.

**Exercise 4**: Redis with Lua scripts for atomic operations. For Redis downtime, consider "fail open" (allow requests) vs. "fail closed" (reject requests). Which is safer for a payment API?

**Exercise 5**: Think about the token bucket algorithm. A large capacity allows bursts, but the refill rate controls the sustained rate.

---

## Self-Assessment Checklist

- [ ] I can explain 4 rate limiting algorithms and their tradeoffs
- [ ] I can implement a sliding window rate limiter
- [ ] I understand why distributed rate limiting requires centralized state
- [ ] I can design rate limiting rules for a public API
- [ ] I know the correct HTTP status code and headers for rate limiting
- [ ] I understand the tradeoff between strict and lenient rate limiting
