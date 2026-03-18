# Netflix: Scale Considerations

## The Numbers

Netflix is one of the most demanding streaming systems ever built:

- 260+ million subscribers in 190+ countries
- 15% of global internet traffic at peak
- 1+ billion hours of content watched per day
- 15,000+ titles in the catalog
- Streams at up to 4K HDR (25+ Mbps per stream)
- 100+ microservices
- Deploys code thousands of times per day

---

## The Core Scaling Challenge: Video Delivery

Streaming video is fundamentally different from serving web pages. A single 2-hour movie in 4K is ~50GB. Serving millions of concurrent streams means moving petabytes of data per hour.

### Why You Can't Serve Video from Your Own Servers

```
Naive approach:
  User in Tokyo → Netflix servers in US → stream video

Problems:
  1. Latency: 150ms+ round trip → buffering
  2. Bandwidth: 1M concurrent streams × 5 Mbps = 5 Tbps
     (you'd need thousands of 10Gbps links)
  3. Cost: transit bandwidth is expensive
  4. Single point of failure
```

### Open Connect: Netflix's Custom CDN

Netflix built its own CDN called Open Connect. Instead of paying Akamai/Cloudflare, they:

1. **Place servers inside ISPs**: Netflix ships physical servers (OCAs — Open Connect Appliances) to ISPs worldwide. The ISP hosts them for free in exchange for reduced transit costs.

2. **Pre-position content**: Before peak hours, Netflix pushes popular content to local OCAs. When you watch Stranger Things, it's likely served from a server in your city.

3. **Adaptive bitrate**: Netflix encodes each title at 20+ different quality levels. The player switches quality based on your bandwidth.

```
Content delivery flow:
  User clicks "Play"
  → Netflix API: "Which OCA should serve this user?"
  → Steering service: picks best OCA based on:
      - Geographic proximity
      - OCA load
      - ISP peering agreements
      - Content availability on OCA
  → Player connects directly to OCA
  → OCA streams video (no Netflix servers involved!)
```

---

## Video Encoding Pipeline

Before a title can be streamed, it must be encoded into hundreds of variants.

```
Source file (camera raw or studio master):
  → 4K HDR, 2K, 1080p, 720p, 480p, 360p
  × H.264, H.265/HEVC, AV1 (different codecs)
  × Multiple audio tracks (languages, Dolby Atmos)
  × Subtitles (50+ languages)
  = 1,200+ files per title

Encoding pipeline:
  Source → S3 → Encoding Farm (thousands of EC2 instances)
         → Quality validation
         → S3 (encoded files)
         → Distributed to OCAs worldwide
```

**Per-title encoding time**: A 2-hour movie takes ~1 hour to encode all variants using massive parallelism.

**Storage**: Netflix stores ~100 petabytes of encoded content.

---

## Recommendation System at Scale

Netflix's recommendation engine is responsible for 80% of content watched. Getting it right is critical for retention.

```
Data inputs:
  - What you watched (and when you stopped)
  - What you searched for
  - What you rated
  - What similar users watched
  - Time of day, device type
  - How long you browsed before choosing

ML pipeline:
  User events → Kafka → Spark Streaming → Feature store
  Batch training → Model store → A/B testing → Serving layer

Serving:
  User opens Netflix → API call → Recommendation service
  → Fetch pre-computed recommendations from cache (Redis)
  → Personalize ranking in real-time (< 100ms)
  → Return ranked list of titles
```

**Scale**: 260M users × 100 recommendations each = 26 billion recommendation slots to fill.

Pre-computation (batch) + real-time personalization (online) is the key pattern.

---

## Chaos Engineering: Netflix's Secret Weapon

Netflix invented Chaos Engineering. The idea: deliberately break things in production to find weaknesses before they cause outages.

```
Chaos Monkey: randomly terminates EC2 instances
Chaos Gorilla: terminates entire availability zones
Chaos Kong: simulates entire region failure
Latency Monkey: adds artificial latency to service calls
```

**Why this works**: If you know your system will fail (and it will), you want to find the failures during business hours when engineers are available, not at 3am during peak traffic.

**Result**: Netflix has survived multiple AWS outages that took down other major services.

---

## Handling 100x Growth

### Phase 1: DVD-by-mail era (1997-2007)
- Simple web app + database
- No streaming infrastructure needed

### Phase 2: Early streaming (2007-2010)
- Monolithic application
- Own data centers
- Simple CDN (Akamai)

### Phase 3: Cloud migration (2010-2016)
- Migrated entirely to AWS (7-year migration)
- Broke monolith into microservices
- Built Open Connect CDN
- Developed Chaos Engineering

### Phase 4: Global scale (2016-present)
- 190+ countries
- Custom encoding (AV1 codec)
- ML-driven everything
- Edge computing for personalization

---

## The Thundering Herd Problem

When a popular show releases (Stranger Things season 5), millions of users try to watch simultaneously.

```
Problem:
  10M users click play at 3am (new season drops)
  → 10M requests to recommendation service
  → 10M cache misses (new content not cached yet)
  → 10M database queries
  → Database falls over

Solutions:
  1. Pre-warm caches before release
  2. Request coalescing (one DB query serves many waiting requests)
  3. Circuit breakers (fail fast, serve degraded experience)
  4. Gradual rollout (release to 1% of users first)
  5. Staggered release by timezone
```

---

## Microservices at Netflix Scale

Netflix has 100+ microservices. Managing them requires:

**Service Mesh (Hystrix → Resilience4j)**:
- Circuit breakers on every service call
- Fallback responses when services fail
- Bulkhead pattern (isolate failures)

**API Gateway (Zuul)**:
- Single entry point for all client requests
- Authentication, rate limiting, routing
- A/B testing at the edge

**Service Discovery (Eureka)**:
- Services register themselves
- Clients discover services dynamically
- Health checks remove unhealthy instances

---

## Key Lessons

1. **Build your own CDN** at Netflix scale — third-party CDNs are too expensive and less controllable
2. **Pre-compute everything** — recommendations, thumbnails, encoding variants
3. **Chaos Engineering** — find failures before they find you
4. **Adaptive bitrate** — meet users where their bandwidth is
5. **Separate the control plane from the data plane** — API servers handle metadata; OCAs handle video bytes
6. **A/B test everything** — even thumbnail images (Netflix tests 20+ thumbnails per title)
