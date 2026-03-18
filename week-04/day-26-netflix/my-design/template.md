# My Netflix Design — Learner Template

Practice designing a video streaming service like Netflix. The key challenges are video delivery at scale, content encoding, and personalized recommendations.

---

## Step 1: Clarify Requirements (5 minutes)

**Functional Requirements**:
- [ ] Users can browse and search content catalog
- [ ] Users can stream video (adaptive quality)
- [ ] System recommends content to users
- [ ] Users can create profiles and watchlists
- [ ] Other: _______________

**Non-Functional Requirements**:
- Concurrent streams: _______________
- Video start time: < ___ seconds
- Buffering rate: < ___% of playback time
- Availability: _______________
- Global reach: _______________

**Out of Scope**:
- Content licensing and acquisition
- Live streaming
- _______________

---

## Step 2: Capacity Estimation

```
Concurrent streams (peak): ___
Average bitrate per stream: ___ Mbps
Total bandwidth needed: ___ Tbps

Catalog size: ___ titles
Average encoded size per title (all variants): ___ GB
Total storage: ___ PB

Daily active users: ___
Recommendation requests/second: ___
```

---

## Step 3: High-Level Design

```
[Draw your architecture here]

Key components:
- Client (TV, mobile, web)
- CDN / Video delivery
- API servers
- Recommendation service
- Search service
- User service
- Content catalog service
- Encoding pipeline
- Storage (video files, metadata)
```

---

## Step 4: Deep Dive — Video Delivery

How do you stream video to millions of concurrent users?

**Your CDN strategy**:
- Use existing CDN (Akamai/Cloudflare)?
- Build your own?
- Hybrid?

**Content placement**:
- How do you decide what content to pre-position where?
- How do you handle a new release (cold start)?

**Adaptive bitrate streaming**:
- How does the player decide which quality to request?
- What happens when bandwidth drops mid-stream?
- What protocols do you use? (HLS, DASH, etc.)

---

## Step 5: Deep Dive — Video Encoding

Before a video can be streamed, it must be encoded. Design the pipeline:

```
Input: [raw video file]
Output: [list the variants you'd create]

Pipeline steps:
1. _______________
2. _______________
3. _______________
```

**Questions to answer**:
- How many quality levels do you encode?
- Which codecs? (H.264, H.265, AV1)
- How do you parallelize encoding?
- How long does encoding take for a 2-hour movie?
- Where do you store the encoded files?

---

## Step 6: Deep Dive — Recommendations

Design the recommendation system:

**Data you collect**:
- _______________
- _______________

**Algorithm approach**:
- Collaborative filtering?
- Content-based filtering?
- Hybrid?

**Architecture**:
- Batch processing vs. real-time?
- How do you serve recommendations in < 100ms?
- How do you handle a new user (cold start problem)?

---

## Step 7: Deep Dive — Search

How do you implement content search?

**Challenges**:
- Typo tolerance
- Multi-language support
- Ranking (popular vs. personalized)

**Technology**: _______________

---

## Step 8: Bottlenecks and Solutions

| Bottleneck | Solution |
|------------|----------|
| New season release (thundering herd) | |
| Video storage costs | |
| Recommendation latency | |
| Global latency | |

---

## Self-Assessment

Compare to `../architecture-diagram.md` and `../scale-considerations.md`.

- [ ] Did I address video delivery at scale?
- [ ] Did I design the encoding pipeline?
- [ ] Did I handle the CDN strategy?
- [ ] Did I design the recommendation system?
- [ ] Did I address the thundering herd problem?
- [ ] Did I consider global distribution?

**What I got right**: _______________
**What I missed**: _______________
**What I'd do differently**: _______________
