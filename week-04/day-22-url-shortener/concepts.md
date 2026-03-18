# Day 22: URL Shortener — Complete Design

## 1. Requirements

### Functional
- Given a long URL, generate a short URL (7 characters)
- Given a short URL, redirect to the long URL
- Custom aliases (user-defined short codes)
- URL expiration (default: 1 year)
- Click analytics (count, location, device, referrer)

### Non-Functional
- 100 million URLs created per day
- Read:write ratio = 100:1
- Redirect latency: < 10ms (p99)
- Availability: 99.9%
- Analytics can be eventually consistent

---

## 2. Scale Estimation

```
Writes:
  100M URLs/day ÷ 86,400 sec/day = ~1,200 writes/second

Reads:
  100:1 ratio → 120,000 reads/second

Storage:
  Each URL record: ~500 bytes
  100M URLs/day × 365 days = 36.5B URLs/year
  36.5B × 500 bytes = ~18TB/year

Bandwidth:
  Reads: 120,000 req/sec × 200 bytes/response = 24 MB/second
```

---

## 3. API Design

```
POST /api/urls
  Request:  { "long_url": "https://...", "alias": "optional", "expires_in": 86400 }
  Response: { "short_url": "https://short.ly/abc1234", "expires_at": "..." }
  Status:   201 Created

GET /{short_code}
  Response: 302 Redirect to long URL
  Status:   302 Found (or 301 Moved Permanently)

GET /api/urls/{short_code}/stats
  Response: { "clicks": 1234, "created_at": "...", "expires_at": "..." }
  Status:   200 OK

DELETE /api/urls/{short_code}
  Status:   204 No Content
```

### 301 vs. 302 Redirect

| | 301 Permanent | 302 Temporary |
|-|---------------|---------------|
| Browser caches | Yes | No |
| Analytics | Misses repeat visits | Captures all visits |
| SEO | Passes link equity | Doesn't |
| Use when | URL never changes | Need analytics |

**Choose 302** for analytics. The browser won't cache it, so every click goes through your server.

---

## 4. Short Code Generation

### Option A: Base62 Encoding of Auto-Increment ID

```python
CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode_base62(num: int) -> str:
    if num == 0:
        return CHARS[0]
    result = []
    while num:
        result.append(CHARS[num % 62])
        num //= 62
    return ''.join(reversed(result))

def decode_base62(s: str) -> int:
    result = 0
    for char in s:
        result = result * 62 + CHARS.index(char)
    return result

# Examples:
# ID 1 → "1"
# ID 1000000 → "4c92"
# ID 3521614606207 → "zzzzzzz" (7 chars, max)
```

**Capacity**: 62^7 = 3.5 trillion unique codes. More than enough.

**Pros**: No collisions, deterministic, sequential IDs are predictable  
**Cons**: Sequential IDs are guessable (security concern)

### Option B: Random + Collision Check

```python
import secrets
import string

def generate_code(length: int = 7) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

# Check for collision in DB, retry if exists
def create_short_url(long_url: str) -> str:
    for _ in range(5):  # Max 5 retries
        code = generate_code()
        if not db.exists(f"url:{code}"):
            db.set(f"url:{code}", long_url)
            return code
    raise Exception("Failed to generate unique code")
```

**Pros**: Not guessable  
**Cons**: Collision probability increases as DB fills up

---

## 5. Database Design

```sql
CREATE TABLE urls (
    id          BIGSERIAL PRIMARY KEY,
    short_code  VARCHAR(10) UNIQUE NOT NULL,
    long_url    TEXT NOT NULL,
    user_id     BIGINT,
    created_at  TIMESTAMP DEFAULT NOW(),
    expires_at  TIMESTAMP,
    is_active   BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_urls_short_code ON urls(short_code);
CREATE INDEX idx_urls_user_id ON urls(user_id);
CREATE INDEX idx_urls_expires_at ON urls(expires_at) WHERE expires_at IS NOT NULL;

-- Analytics table (separate, can be eventually consistent)
CREATE TABLE url_clicks (
    id          BIGSERIAL PRIMARY KEY,
    short_code  VARCHAR(10) NOT NULL,
    clicked_at  TIMESTAMP DEFAULT NOW(),
    ip_address  INET,
    user_agent  TEXT,
    referrer    TEXT,
    country     VARCHAR(2)
);

CREATE INDEX idx_clicks_short_code ON url_clicks(short_code);
CREATE INDEX idx_clicks_clicked_at ON url_clicks(clicked_at);
```

---

## 6. Architecture

```
                    ┌─────────────────────────────────────┐
                    │           CDN / Edge                 │
                    │  (Cache popular redirects at edge)   │
                    └──────────────────┬──────────────────┘
                                       │
                    ┌──────────────────▼──────────────────┐
                    │           Load Balancer              │
                    └──────┬───────────────────┬──────────┘
                           │                   │
              ┌────────────▼──┐         ┌──────▼────────────┐
              │  Write API    │         │   Redirect API    │
              │  (Create URLs)│         │   (Fast path)     │
              └────────┬──────┘         └──────┬────────────┘
                       │                       │
              ┌────────▼──────┐         ┌──────▼────────────┐
              │  PostgreSQL   │         │   Redis Cache     │
              │  (Primary)    │         │   (short→long)    │
              └───────────────┘         └──────┬────────────┘
                                               │ Cache miss
                                        ┌──────▼────────────┐
                                        │  PostgreSQL       │
                                        │  (Read Replica)   │
                                        └───────────────────┘
                                               │
                                        ┌──────▼────────────┐
                                        │  Kafka            │
                                        │  (Click events)   │
                                        └──────┬────────────┘
                                               │
                                        ┌──────▼────────────┐
                                        │  Analytics DB     │
                                        │  (ClickHouse)     │
                                        └───────────────────┘
```

---

## 7. The Redirect Flow (Critical Path)

```python
def redirect(short_code: str) -> str:
    # 1. Check Redis cache (< 1ms)
    long_url = redis.get(f"url:{short_code}")
    if long_url:
        # Async: publish click event to Kafka
        kafka.publish("url_clicks", {"code": short_code, "timestamp": now()})
        return long_url

    # 2. Cache miss: check database (< 10ms)
    url = db.query("SELECT long_url, expires_at FROM urls WHERE short_code = ?", short_code)

    if not url:
        raise NotFoundException("Short URL not found")

    if url.expires_at and url.expires_at < now():
        raise GoneException("Short URL has expired")

    # 3. Populate cache (TTL = 24 hours)
    redis.setex(f"url:{short_code}", 86400, url.long_url)

    # 4. Async: publish click event
    kafka.publish("url_clicks", {"code": short_code, "timestamp": now()})

    return url.long_url
```

---

## 8. Analytics Pipeline

```
Click event → Kafka → Stream Processor → ClickHouse (analytics DB)
                                       → Redis (real-time counters)

Real-time counter (Redis):
  INCR url:clicks:{short_code}

Historical analytics (ClickHouse):
  SELECT
    short_code,
    toDate(clicked_at) as date,
    count() as clicks,
    uniqExact(ip_address) as unique_visitors
  FROM url_clicks
  WHERE short_code = 'abc1234'
  GROUP BY short_code, date
  ORDER BY date DESC
```

---

## 9. Scaling to 1 Billion URLs

```
Current: 18TB/year, 120k reads/second

At 1 billion URLs:
  Storage: 500 bytes × 1B = 500GB (manageable in one DB)
  Reads: 120k/second → Redis handles this easily
  Writes: 1,200/second → Single PostgreSQL handles this

The bottleneck is NOT the database — it's the redirect latency.

Solution: CDN caching
  Popular URLs cached at CDN edge
  99% of redirects served from CDN (< 5ms)
  Only 1% hit the application servers
```

---

## References
- [bit.ly Engineering Blog](https://word.bitly.com/)
- [TinyURL Architecture](https://systemdesign.one/url-shortening-system-design/)
