# Netflix Design — Tradeoffs

## CDN Strategy: Third-Party vs. Own CDN

### Third-Party CDN (Akamai, Cloudflare)
**Pros**: No infrastructure investment, global coverage  
**Cons**: Expensive at Netflix's scale, less control, shared infrastructure

### Netflix Open Connect (Own CDN)
Netflix built their own CDN, deployed directly in ISP data centers.

**Pros**:
- Dramatically lower bandwidth costs (ISPs benefit too — less traffic on their backbone)
- Better performance (content is literally inside the ISP's network)
- Full control over caching and delivery

**Cons**:
- Massive infrastructure investment
- Operational complexity

**Decision**: At Netflix's scale (15% of global internet bandwidth), owning the CDN is economically necessary.

---

## Video Encoding: H.264 vs. HEVC vs. AV1

| Codec | Compression | Quality | CPU Cost | Support |
|-------|-------------|---------|----------|---------|
| H.264 | Baseline | Good | Low | Universal |
| HEVC (H.265) | 2x better | Better | High | Most devices |
| AV1 | 3x better | Best | Very High | Modern devices |

**Netflix's approach**: Encode in multiple codecs. Serve the best codec the device supports.

**Per-title encoding**: Netflix analyzes each title and optimizes encoding parameters per scene. An action movie needs different settings than a documentary.

---

## Recommendation: Accuracy vs. Freshness

### Batch Processing (Daily)
Train recommendation models on all user data daily.

**Pros**: High accuracy (uses all data), computationally efficient  
**Cons**: Recommendations are up to 24 hours stale

### Real-Time Processing
Update recommendations as user watches content.

**Pros**: Immediately reflects current viewing session  
**Cons**: Less accurate (less data), computationally expensive

**Netflix's approach**: Hybrid
- Batch models for long-term preferences (updated daily)
- Real-time signals for session context (what you're watching right now)

---

## Availability: Chaos Engineering

Netflix famously runs "Chaos Monkey" — a tool that randomly kills production services.

**Why**: Forces engineers to build resilient systems. If you know any service can fail at any time, you design for it.

**Result**: Netflix can survive the failure of any single service, data center, or AWS region.

**Lesson**: Design for failure. Test failure in production. The only way to know your system is resilient is to break it intentionally.

---

## The "Thundering Herd" on New Releases

When a popular new show releases (Stranger Things, Wednesday), millions of users try to watch simultaneously.

**Problem**: CDN cache is cold. All requests go to origin.

**Solution**: Pre-positioning
1. Netflix predicts which content will be popular (based on marketing, pre-release data)
2. Before release, pushes content to all CDN edge nodes
3. When users start watching, CDN cache is already warm

**Result**: Even on release day, 95%+ of requests are served from CDN cache.
