# Day 7: Mini-Design Challenge — URL Shortener

Set a 45-minute timer. Work through this as if it were a real interview.

---

## The Problem

Design a URL shortening service like bit.ly.

**Functional Requirements**:
- Given a long URL, generate a short URL (e.g., `short.ly/abc123`)
- Given a short URL, redirect to the original long URL
- Users can optionally create custom short URLs
- URLs expire after 1 year by default

**Non-Functional Requirements**:
- 100 million URLs created per day
- Read:write ratio = 100:1
- Availability: 99.9%
- Redirect latency: < 10ms (p99)

---

## Step 1: Estimate Scale (10 minutes)

Calculate:

1. **Write throughput**: 100M URLs/day = ? writes/second

2. **Read throughput**: Given 100:1 read:write ratio = ? reads/second

3. **Storage**: 
   - Each URL record: ~500 bytes (short URL + long URL + metadata)
   - 100M URLs/day × 365 days = ? URLs/year
   - Total storage = ?

4. **Bandwidth**:
   - Each redirect response: ~200 bytes
   - Read throughput × 200 bytes = ? MB/second

Show your math. These numbers will drive your design decisions.

---

## Step 2: API Design (5 minutes)

Design the REST API:

```
POST /api/urls
  Request: { "long_url": "https://...", "custom_alias": "optional" }
  Response: { "short_url": "https://short.ly/abc123", "expires_at": "..." }

GET /{short_code}
  Response: 301/302 redirect to long URL

DELETE /api/urls/{short_code}
  Response: 204 No Content
```

Questions to answer:
1. Should the redirect use 301 (permanent) or 302 (temporary)? What are the caching implications?
2. How do you handle a short code that doesn't exist?
3. How do you handle an expired URL?

---

## Step 3: Database Design (10 minutes)

Design the schema:

```sql
-- Your schema here
CREATE TABLE urls (
    -- What columns do you need?
    -- What's the primary key?
    -- What indexes do you need?
);
```

Questions:
1. What's the primary key? The short code or an auto-increment ID?
2. Do you need a separate table for custom aliases?
3. What index do you need for the redirect lookup?
4. SQL or NoSQL? Why?

---

## Step 4: Short Code Generation (10 minutes)

How do you generate a unique 6-character short code?

**Option A: Random generation**
```python
import random, string
def generate_code():
    chars = string.ascii_letters + string.digits  # 62 characters
    return ''.join(random.choices(chars, k=6))
    # 62^6 = 56 billion possible codes
```
Problem: Collisions. Two URLs might get the same code.

**Option B: Hash the URL**
```python
import hashlib
def generate_code(long_url):
    hash = hashlib.md5(long_url.encode()).hexdigest()
    return hash[:6]  # Take first 6 characters
```
Problem: Two different URLs could hash to the same prefix.

**Option C: Auto-increment ID → Base62 encode**
```python
def encode_base62(num):
    chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = []
    while num:
        result.append(chars[num % 62])
        num //= 62
    return ''.join(reversed(result))
# ID 1000000 → "4c92"
```
No collisions. Predictable. But sequential IDs are guessable.

Which approach would you use? Why?

---

## Step 5: Architecture Design (10 minutes)

Draw the full architecture. Include:
- Load balancer
- Application servers
- Cache layer
- Database (primary + replicas)
- CDN (if applicable)

Answer these questions in your diagram:
1. Where does the redirect happen? (App server? CDN edge?)
2. What do you cache? (The short_code → long_url mapping)
3. How do you handle cache misses?
4. How do you handle the write path? (Creating new short URLs)

---

## Step 6: Bottleneck Analysis (5 minutes)

Given your design:
1. What's the bottleneck at 1,000 reads/second?
2. What's the bottleneck at 100,000 reads/second?
3. What's the bottleneck at 1,000,000 reads/second?
4. How does your design evolve at each scale?

---

## Step 7: Tradeoffs Discussion (5 minutes)

Discuss:
1. You chose SQL (or NoSQL). What did you give up?
2. You chose 301 (or 302) redirects. What are the implications?
3. You chose random codes (or sequential IDs). What are the security implications?
4. What would you do differently if you had to support 10x the scale?

---

## Reference Solution Outline

After completing your design, compare with this outline:

**Scale estimates**:
- Writes: ~1,200/second
- Reads: ~120,000/second
- Storage: ~18TB/year

**Architecture**:
- CDN handles redirects for cached URLs (< 1ms)
- App servers handle new URL creation and cache misses
- Redis cache: short_code → long_url (TTL = 24 hours)
- PostgreSQL: source of truth (with read replicas for cache misses)

**Short code**: Base62 encoding of auto-increment ID (no collisions, fast)

**Redirect type**: 302 (temporary) — allows analytics tracking and URL updates

**Key insight**: 99% of redirects can be served from CDN/cache. The database only handles new URL creation and cache misses.

---

## Self-Assessment

After completing the design:
- [ ] I estimated scale correctly (within 2x)
- [ ] My API design is RESTful and handles edge cases
- [ ] My database schema is appropriate for the access patterns
- [ ] I chose a short code generation strategy and justified it
- [ ] My architecture handles the read-heavy workload
- [ ] I identified the bottlenecks at different scales
- [ ] I discussed tradeoffs in my design choices
