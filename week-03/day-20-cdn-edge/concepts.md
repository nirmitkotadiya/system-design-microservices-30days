# Day 20: CDN & Edge Computing — Concepts Deep Dive

## 1. Why CDN?

The speed of light in fiber optic cable is ~200,000 km/s. The round-trip time from New York to Tokyo is ~150ms — just from physics.

```
Without CDN:
  User in Tokyo → Origin in Virginia
  Round trip: ~150ms (just network latency)
  Plus: server processing, database queries
  Total: 300-500ms

With CDN:
  User in Tokyo → CDN edge in Tokyo
  Round trip: ~5ms
  Total: 5-10ms (for cached content)
```

CDNs work by caching content at edge nodes close to users. The first request goes to origin; subsequent requests are served from the edge.

---

## 2. CDN Architecture

```
                    ┌─────────────────┐
                    │  Origin Server  │
                    │  (Virginia)     │
                    └────────┬────────┘
                             │ Cache miss: fetch from origin
          ┌──────────────────┼──────────────────┐
          │                  │                  │
   ┌──────▼──────┐   ┌───────▼──────┐   ┌──────▼──────┐
   │ CDN Edge    │   │  CDN Edge    │   │  CDN Edge   │
   │ (Tokyo)     │   │  (London)    │   │  (São Paulo)│
   │ Cache: 95%  │   │  Cache: 92%  │   │  Cache: 88% │
   └──────┬──────┘   └───────┬──────┘   └──────┬──────┘
          │                  │                  │
   Tokyo Users        London Users       Brazil Users
```

### Cache Hit Flow
```
1. User requests: https://cdn.example.com/image.jpg
2. DNS resolves to nearest CDN edge (GeoDNS)
3. CDN edge checks cache: HIT
4. CDN edge returns cached content
5. Total time: ~5ms
```

### Cache Miss Flow
```
1. User requests: https://cdn.example.com/image.jpg
2. DNS resolves to nearest CDN edge
3. CDN edge checks cache: MISS
4. CDN edge fetches from origin
5. CDN edge caches the response
6. CDN edge returns content to user
7. Total time: ~150ms (first request only)
```

---

## 3. What to Cache

### Always Cache (Long TTL)
- Static assets: images, CSS, JavaScript, fonts
- Versioned assets: `app.v2.3.js` (version in filename = safe to cache forever)
- Video content

### Cache with Short TTL
- API responses for public data (product listings, prices)
- HTML pages (if content changes infrequently)

### Never Cache
- User-specific data (shopping cart, account info)
- Authentication tokens
- Real-time data (stock prices, live scores)
- POST/PUT/DELETE responses

---

## 4. Cache Headers

```http
# Cache for 1 year (immutable — content never changes)
Cache-Control: public, max-age=31536000, immutable

# Cache for 1 hour
Cache-Control: public, max-age=3600

# Cache but revalidate (check if content changed)
Cache-Control: public, max-age=3600, must-revalidate

# Don't cache (user-specific)
Cache-Control: private, no-store

# Cache but always revalidate
Cache-Control: no-cache
```

### ETag for Conditional Requests
```http
# First request
GET /api/products/123
Response: ETag: "abc123"

# Subsequent request (check if changed)
GET /api/products/123
If-None-Match: "abc123"

# If unchanged:
HTTP/1.1 304 Not Modified
(No body — saves bandwidth)

# If changed:
HTTP/1.1 200 OK
ETag: "def456"
{...new content...}
```

---

## 5. Cache Invalidation

The hardest problem in CDN management.

### Strategy 1: TTL-Based Expiration
Content expires after a fixed time. Simple but can serve stale content.

```
Cache-Control: max-age=3600  # Expires in 1 hour
```

### Strategy 2: Versioned URLs
Embed version in the URL. When content changes, change the URL.

```
# Old version
https://cdn.example.com/app.js → cached forever

# New version (different URL = new cache entry)
https://cdn.example.com/app.v2.js → cached forever
```

**Best for**: Static assets (CSS, JS, images)

### Strategy 3: Cache Purge API
Explicitly tell the CDN to remove a cached item.

```bash
# Cloudflare cache purge
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache" \
  -H "Authorization: Bearer {token}" \
  -d '{"files": ["https://example.com/product/123"]}'
```

**Best for**: Dynamic content that changes unpredictably

### Strategy 4: Surrogate Keys (Cache Tags)
Tag cached items and purge by tag.

```http
# Response includes cache tags
Surrogate-Key: product-123 category-electronics

# Purge all items tagged with product-123
POST /purge {"tags": ["product-123"]}
```

**Best for**: Related content (purge all pages that show product 123)

---

## 6. Edge Computing

Edge computing runs code at CDN edge nodes, not just caching static content.

### Edge Functions (Cloudflare Workers, Lambda@Edge)

```javascript
// Cloudflare Worker: A/B testing at the edge
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)

  // A/B test: 50% get new homepage
  const variant = Math.random() < 0.5 ? 'control' : 'treatment'

  if (variant === 'treatment') {
    url.pathname = '/homepage-v2'
  }

  return fetch(url.toString())
}
```

### Edge Function Use Cases

| Use Case | Why at Edge? |
|----------|-------------|
| A/B testing | No origin round trip for routing decision |
| Authentication | Reject unauthenticated requests before they hit origin |
| Geo-blocking | Block requests from certain countries |
| Request transformation | Modify headers, rewrite URLs |
| Personalization | Serve different content based on user attributes |
| Bot detection | Block bots before they reach origin |

### Edge vs. Origin

| Aspect | Edge | Origin |
|--------|------|--------|
| Latency | ~5ms | ~100-500ms |
| Compute | Limited | Unlimited |
| State | Stateless (mostly) | Stateful |
| Cost | Per request | Per compute hour |
| Use case | Simple logic, caching | Complex business logic |

---

## 7. CDN for Video Streaming

Video streaming is the most demanding CDN use case.

```
Netflix CDN Strategy:
  - 15,000+ CDN servers in 1,000+ locations
  - 80% of content served from CDN
  - Adaptive bitrate: CDN serves different quality based on bandwidth
  - Pre-positioning: Popular content pushed to edge before users request it
```

### Adaptive Bitrate Streaming (HLS/DASH)
```
Video is split into small segments (2-10 seconds each):
  video_1080p_segment_001.ts
  video_720p_segment_001.ts
  video_480p_segment_001.ts

Player requests segments based on available bandwidth:
  Good connection → 1080p segments
  Poor connection → 480p segments
  Connection improves → switch to higher quality
```

---

## References
- [Cloudflare CDN Documentation](https://developers.cloudflare.com/cache/)
- [AWS CloudFront Documentation](https://docs.aws.amazon.com/cloudfront/)
- [Netflix Open Connect (CDN)](https://openconnect.netflix.com/)
- [Cloudflare Workers](https://developers.cloudflare.com/workers/)
