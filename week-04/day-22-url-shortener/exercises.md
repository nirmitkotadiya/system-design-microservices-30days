# Day 22: Exercises — URL Shortener

---

## Exercise 1: Implement Base62 Encoding (20 minutes)

```python
CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode_base62(num: int) -> str:
    """Convert an integer to a base62 string."""
    # Your implementation here
    pass

def decode_base62(s: str) -> int:
    """Convert a base62 string back to an integer."""
    # Your implementation here
    pass

# Test cases:
assert encode_base62(0) == "0"
assert encode_base62(61) == "Z"
assert encode_base62(62) == "10"
assert decode_base62("10") == 62
assert decode_base62(encode_base62(1000000)) == 1000000
print("All tests passed!")
```

---

## Exercise 2: Design Custom Aliases (20 minutes)

Users want to create custom short URLs like `short.ly/my-brand`.

**Design challenges**:
1. How do you prevent conflicts between auto-generated codes and custom aliases?
2. What characters should you allow in custom aliases?
3. What's the maximum length for a custom alias?
4. How do you handle reserved words? (`api`, `admin`, `login`, etc.)
5. Should custom aliases be case-sensitive?

---

## Exercise 3: Design URL Expiration (20 minutes)

URLs expire after a configurable period.

**Design**:
1. How do you store expiration time in the database?
2. How do you check expiration on every redirect? (Without slowing down the critical path)
3. How do you clean up expired URLs from the database? (Background job? Lazy deletion?)
4. What HTTP status code do you return for an expired URL? (404? 410 Gone?)
5. How do you handle the case where a user tries to create a URL with an alias that was previously used but has expired?

---

## Exercise 4: Analytics Design (25 minutes)

Design the analytics system for the URL shortener:

**Metrics to track**:
- Total clicks per URL
- Unique visitors per URL
- Clicks by country
- Clicks by device type (mobile/desktop)
- Clicks over time (hourly, daily, weekly)
- Top referrers

**Design**:
1. Should analytics be synchronous (in the redirect path) or asynchronous?
2. What's the data model for storing click events?
3. How do you count unique visitors? (Exact count vs. approximate with HyperLogLog)
4. How do you handle the analytics for a URL with 1 billion clicks?
5. What's the retention policy for raw click data?

---

## Exercise 5: Challenge — Scale to 10 Billion URLs (30 minutes)

At 10 billion URLs:
- Storage: 5TB (manageable)
- But: 1.2 million writes/second (not manageable with single DB)

**Design the scaled architecture**:

1. **Write scaling**: How do you handle 1.2M writes/second?

2. **ID generation**: With multiple write nodes, how do you generate unique IDs without coordination? (Hint: look up Twitter Snowflake IDs)

3. **Read scaling**: 12 million reads/second. Redis can handle ~1M ops/second per node. How many Redis nodes do you need?

4. **Hot URLs**: A URL goes viral and gets 1 million clicks/second. How do you handle this?

5. **Geographic distribution**: Users are global. How do you minimize redirect latency for users in Asia when your database is in the US?

---

## Hints

**Exercise 1**: For encode, repeatedly divide by 62 and collect remainders. For decode, multiply by 62 and add each character's value.

**Exercise 5, Q2**: Twitter Snowflake: 64-bit ID = timestamp (41 bits) + machine ID (10 bits) + sequence (12 bits). No coordination needed.

**Exercise 5, Q4**: Hot URL → cache at CDN edge. The CDN handles the traffic, not your servers.

---

## Self-Assessment Checklist

- [ ] I can implement base62 encoding/decoding
- [ ] I can design custom alias handling
- [ ] I understand the tradeoffs between 301 and 302 redirects
- [ ] I can design an async analytics pipeline
- [ ] I can scale the design to handle 10 billion URLs
