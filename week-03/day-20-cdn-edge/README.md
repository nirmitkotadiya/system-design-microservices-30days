# Day 20: CDN & Edge Computing

## "Bringing Your Content Closer to Your Users"

**Estimated Time**: 90 minutes  
**Difficulty**: Intermediate  
**Prerequisites**: Days 1–19 complete

---

## Learning Objectives
- Explain how CDNs work and why they reduce latency
- Describe CDN caching strategies and cache invalidation
- Explain edge computing and edge functions
- Design a CDN strategy for a given system
- Understand the tradeoffs between CDN and origin

---

## Quick Summary

A CDN (Content Delivery Network) is a geographically distributed network of servers that caches content close to users. Instead of every user fetching content from your origin server in Virginia, they fetch it from a CDN edge node in their city.

The core insight: **the speed of light is a hard limit. The only way to reduce latency for global users is to put content closer to them.**

---

## Files in This Folder

| File | Description |
|------|-------------|
| `concepts.md` | CDN architecture, caching, edge functions, cache invalidation |
| `exercises.md` | 5 exercises from CDN strategy to edge function design |

---

## Success Criteria

You've mastered Day 20 when you can:
- [ ] Explain how a CDN reduces latency
- [ ] Design cache headers for different content types
- [ ] Explain cache invalidation strategies
- [ ] Describe edge functions and their use cases
- [ ] Design a CDN strategy for a video streaming platform

---

## Interview Questions for This Day
- "How does a CDN work?"
- "How do you invalidate CDN cache when content changes?"
- "What is edge computing?"
- "Design the CDN strategy for a video streaming platform"
