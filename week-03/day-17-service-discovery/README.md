# Day 17: Service Discovery & Service Mesh

## "How Do Services Find Each Other?"

**Estimated Time**: 90 minutes  
**Difficulty**: Advanced  
**Prerequisites**: Days 1–16 complete

---

## Learning Objectives
- Explain why service discovery is necessary in microservices
- Compare client-side vs. server-side service discovery
- Describe what a service mesh does and why you'd want one
- Explain the sidecar proxy pattern
- Describe circuit breakers and why they prevent cascading failures

---

## Quick Summary

In a microservices architecture, services need to find each other. In a monolith, this is trivial (in-process calls). In microservices, services are deployed dynamically — IPs change, instances scale up and down. Service discovery solves this.

The core insight: **service discovery is the foundation of microservices. Without it, you're hardcoding IPs, which breaks the moment anything changes.**

---

## Files in This Folder

| File | Description |
|------|-------------|
| `concepts.md` | Service discovery, service mesh, circuit breakers |
| `exercises.md` | 5 exercises from discovery patterns to circuit breaker design |
| `diagrams/` | Service mesh topology diagrams |

---

## Success Criteria

You've mastered Day 17 when you can:
- [ ] Explain client-side vs. server-side service discovery
- [ ] Describe what a service mesh does
- [ ] Explain the sidecar proxy pattern
- [ ] Describe circuit breakers and their states
- [ ] Design a service mesh topology for a given system

---

## Interview Questions for This Day
- "How do microservices find each other?"
- "What is a service mesh and why would you use one?"
- "What is a circuit breaker and how does it work?"
- "What's the difference between client-side and server-side service discovery?"
