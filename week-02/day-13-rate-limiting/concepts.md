# Day 13: Rate Limiting — Concepts Deep Dive

## 1. Why Rate Limiting?

### Protection Against Abuse
```
Without rate limiting:
  Attacker sends 1,000,000 requests/second
  Your servers are overwhelmed
  Legitimate users can't access the service

With rate limiting:
  Attacker is limited to 100 requests/second
  Legitimate users are unaffected
```

### Fair Resource Allocation
```
Without rate limiting:
  Power user makes 10,000 API calls/minute
  Free tier users get no resources
  
With rate limiting:
  Free tier: 100 calls/minute
  Pro tier: 10,000 calls/minute
  Enterprise: unlimited
```

### Cost Control
API calls cost money (compute, database queries, third-party APIs). Rate limiting prevents runaway costs.

---

## 2. Algorithm 1: Token Bucket

**Analogy**: A bucket that fills with tokens at a fixed rate. Each request consumes one token. If the bucket is empty, the request is rejected.

```
Bucket capacity: 10 tokens
Refill rate: 2 tokens/second

t=0:  Bucket = 10 tokens
t=0:  5 requests arrive → consume 5 tokens → Bucket = 5 tokens
t=1:  Bucket refills → Bucket = 7 tokens (5 + 2)
t=1:  8 requests arrive → consume 7 tokens → Bucket = 0 → 1 request rejected
t=2:  Bucket refills → Bucket = 2 tokens
```

**Pros**:
- Allows bursts (up to bucket capacity)
- Smooth average rate
- Simple to implement

**Cons**:
- Two parameters to tune (capacity and refill rate)
- Burst can still overwhelm downstream services

**Best for**: APIs where occasional bursts are acceptable

```python
class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.last_refill = time.time()

    def allow_request(self) -> bool:
        now = time.time()
        # Add tokens based on time elapsed
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
```

---

## 3. Algorithm 2: Leaky Bucket

**Analogy**: A bucket with a hole at the bottom. Water (requests) pours in at any rate, but leaks out at a fixed rate. If the bucket overflows, requests are dropped.

```
Bucket capacity: 10 requests
Leak rate: 2 requests/second

t=0:  Bucket = 0
t=0:  10 requests arrive → Bucket = 10 (full)
t=0:  2 more requests arrive → DROPPED (bucket full)
t=1:  2 requests processed (leaked) → Bucket = 8
t=1:  5 requests arrive → Bucket = 13 → 3 DROPPED
```

**Pros**:
- Smooth, constant output rate
- Protects downstream services from bursts

**Cons**:
- Bursts are dropped, not delayed
- Doesn't allow any burst

**Best for**: Protecting downstream services that can't handle bursts

---

## 4. Algorithm 3: Fixed Window Counter

**How it works**: Count requests in fixed time windows (e.g., per minute).

```
Window: 1 minute
Limit: 100 requests/minute

12:00:00 - 12:00:59: 95 requests → OK
12:01:00 - 12:01:59: 100 requests → OK
```

**The Problem: Window Boundary Attack**

```
Limit: 100 requests/minute

12:00:50 - 12:00:59: 100 requests (end of window 1)
12:01:00 - 12:01:10: 100 requests (start of window 2)

In 20 seconds: 200 requests! (2x the limit)
```

**Pros**: Simple, low memory  
**Cons**: Vulnerable to boundary attacks

---

## 5. Algorithm 4: Sliding Window Log

**How it works**: Keep a log of all request timestamps. Count requests in the last N seconds.

```
Limit: 100 requests/minute

At 12:01:30:
  Remove all timestamps older than 12:00:30
  Count remaining timestamps
  If count < 100: allow request, add timestamp
  If count >= 100: reject request
```

**Pros**: Accurate, no boundary attack  
**Cons**: High memory (stores all timestamps), O(n) per request

---

## 6. Algorithm 5: Sliding Window Counter (Best of Both)

**How it works**: Combine fixed windows with a weighted calculation.

```
Limit: 100 requests/minute
Current time: 12:01:15 (25% into the current minute)

Previous window (12:00:00 - 12:00:59): 80 requests
Current window (12:01:00 - 12:01:59): 30 requests so far

Weighted count = (80 × 0.75) + (30 × 1.0) = 60 + 30 = 90

90 < 100 → Allow request
```

**Pros**: Accurate, low memory (only 2 counters per user)  
**Cons**: Slightly approximate (assumes uniform distribution in previous window)

**This is what most production systems use.**

---

## 7. Distributed Rate Limiting with Redis

In a distributed system, rate limiting must be centralized. Redis is the standard solution.

### Token Bucket in Redis (Lua Script)

```lua
-- Redis Lua script for atomic token bucket
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])  -- tokens per second
local now = tonumber(ARGV[3])

-- Get current state
local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens = tonumber(bucket[1]) or capacity
local last_refill = tonumber(bucket[2]) or now

-- Refill tokens based on elapsed time
local elapsed = now - last_refill
tokens = math.min(capacity, tokens + elapsed * refill_rate)

-- Check if request is allowed
if tokens >= 1 then
    tokens = tokens - 1
    redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
    redis.call('EXPIRE', key, 3600)
    return 1  -- Allowed
else
    redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
    return 0  -- Rejected
end
```

### Sliding Window Counter in Redis

```python
def is_allowed(user_id: str, limit: int, window_seconds: int) -> bool:
    now = time.time()
    window_start = now - window_seconds

    pipe = redis.pipeline()
    key = f"rate_limit:{user_id}"

    # Remove old entries
    pipe.zremrangebyscore(key, 0, window_start)
    # Count current entries
    pipe.zcard(key)
    # Add current request
    pipe.zadd(key, {str(now): now})
    # Set expiry
    pipe.expire(key, window_seconds * 2)

    results = pipe.execute()
    count = results[1]

    return count < limit
```

---

## 8. Rate Limiting in Practice

### HTTP Headers
```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1700000060

HTTP/1.1 429 Too Many Requests
Retry-After: 30
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1700000060
```

### Rate Limiting Dimensions

| Dimension | Example | Use Case |
|-----------|---------|----------|
| Per user | 100 req/min per user_id | API fairness |
| Per IP | 1000 req/min per IP | DDoS protection |
| Per API key | 10,000 req/min per key | API monetization |
| Per endpoint | 10 req/min for /login | Brute force protection |
| Global | 1M req/min total | System protection |

### Where to Implement Rate Limiting

```
Client → API Gateway (rate limit here) → Services
                ↑
         Best place: centralized, before any processing
         
Or: Middleware in each service
    Pros: Service-specific limits
    Cons: Distributed state management
```

---

## References
- [Stripe's Rate Limiting](https://stripe.com/blog/rate-limiters)
- [Cloudflare's Rate Limiting](https://developers.cloudflare.com/waf/rate-limiting-rules/)
- [Redis Rate Limiting Patterns](https://redis.io/docs/manual/patterns/rate-limiting/)
