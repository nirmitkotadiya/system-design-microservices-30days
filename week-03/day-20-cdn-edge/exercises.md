# Day 20: Exercises — CDN & Edge Computing

---

## Exercise 1: Basic Comprehension (15 minutes)

1. A user in Sydney requests an image from your server in Virginia. The round-trip latency is 150ms. With a CDN edge in Sydney, what's the latency for the first request? For subsequent requests?

2. What's the difference between `Cache-Control: no-cache` and `Cache-Control: no-store`?

3. You update your website's CSS file. Users are still seeing the old version. What's the likely cause? How do you fix it?

4. What is an ETag? How does it reduce bandwidth?

5. What's the difference between CDN caching and edge computing?

---

## Exercise 2: Cache Header Design (25 minutes)

Design the `Cache-Control` headers for each resource type:

| Resource | Changes How Often | Sensitivity | Your Header | Rationale |
|----------|------------------|-------------|-------------|-----------|
| `logo.png` | Never | Public | ? | ? |
| `app.v2.3.js` | Never (versioned) | Public | ? | ? |
| `GET /api/products` | Every hour | Public | ? | ? |
| `GET /api/user/profile` | Anytime | Private | ? | ? |
| `GET /api/trending` | Every 5 minutes | Public | ? | ? |
| `POST /api/orders` | N/A | Private | ? | ? |
| `GET /api/search?q=shoes` | Frequently | Public | ? | ? |

---

## Exercise 3: Cache Invalidation Strategy (25 minutes)

### Scenario: E-Commerce Product Pages

Your product pages are cached at the CDN. When a product's price changes, users might see the old price.

**Design the invalidation strategy**:

1. **Option A**: Short TTL (5 minutes). Users see stale prices for up to 5 minutes.
   - Pros? Cons?

2. **Option B**: Long TTL (24 hours) + explicit purge on price change.
   - Pros? Cons?
   - How do you trigger the purge? (Webhook? Event? Manual?)

3. **Option C**: Versioned URLs. When price changes, generate a new URL.
   - Pros? Cons?
   - How do you update all links to the new URL?

4. **Option D**: Surrogate keys. Tag all product pages with `product-{id}`. Purge by tag on price change.
   - Pros? Cons?

Which would you choose? Why?

---

## Exercise 4: Edge Function Design (20 minutes)

### Scenario

Design edge functions for these use cases:

1. **Authentication**: Reject requests without a valid JWT token before they reach your origin.
   - What does the edge function check?
   - What does it return for invalid tokens?
   - What's the performance benefit?

2. **Geo-blocking**: Block requests from certain countries (compliance requirement).
   - How does the edge function know the user's country?
   - What do you return for blocked countries?

3. **A/B Testing**: Route 10% of users to a new homepage design.
   - How do you ensure the same user always gets the same variant?
   - How do you track which variant a user saw?

---

## Exercise 5: Challenge — Design CDN Strategy for a Video Platform (35 minutes)

### Scenario

Design the CDN strategy for a video streaming platform:
- 50 million daily active users globally
- 10,000 videos, average 2GB each
- 20% of videos account for 80% of views (Pareto principle)
- New videos are uploaded daily
- Live streaming events (up to 1M concurrent viewers)

**Design**:

1. **Content distribution**: You can't cache all 20TB at every edge. What do you cache where?

2. **Pre-positioning**: For a major live event (Super Bowl), how do you pre-position content at edge nodes before the event starts?

3. **Cache invalidation**: A video is taken down due to copyright. How do you remove it from all CDN edges quickly?

4. **Adaptive bitrate**: How does the CDN serve different quality levels to different users?

5. **Live streaming**: Live content can't be cached (it's real-time). How does the CDN help with live streaming?

---

## Hints

**Exercise 2**: Versioned assets (with version in filename) can be cached forever. Non-versioned assets need shorter TTLs or ETags.

**Exercise 3**: Option D (surrogate keys) is what Fastly and Varnish use. It's the most flexible approach.

**Exercise 5, Q1**: Use tiered caching. Popular content at all edges. Less popular content at regional hubs. Rare content only at origin.

---

## Self-Assessment Checklist

- [ ] I can explain how a CDN reduces latency
- [ ] I can design appropriate cache headers for different content types
- [ ] I understand the tradeoffs between different cache invalidation strategies
- [ ] I can describe edge functions and their use cases
- [ ] I can design a CDN strategy for a video streaming platform
- [ ] I understand adaptive bitrate streaming
