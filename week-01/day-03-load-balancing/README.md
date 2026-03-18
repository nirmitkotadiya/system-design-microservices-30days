# Day 3: Load Balancing

## "How Do You Distribute Work Fairly Across Many Servers?"

**Estimated Time**: 90 minutes  
**Difficulty**: Intermediate  
**Prerequisites**: Days 1–2 complete

---

## Learning Objectives
- Explain the role of a load balancer in a distributed system
- Compare load balancing algorithms: round-robin, least connections, IP hash, weighted
- Distinguish between Layer 4 and Layer 7 load balancing
- Explain health checks and why they matter
- Describe sticky sessions and their tradeoffs
- Design a load balancing strategy for a given scenario

---

## Quick Summary

A load balancer is the traffic cop of your system. It sits in front of your servers and decides which server handles each incoming request. The algorithm it uses determines how evenly work is distributed — and poor distribution can leave some servers idle while others are overwhelmed.

The core insight: **load balancing is not just about distributing requests evenly — it's about distributing work evenly**. A request that takes 10ms and one that takes 10 seconds are not equal.

---

## Files in This Folder

| File | Description |
|------|-------------|
| `concepts.md` | LB algorithms, L4 vs L7, health checks, sticky sessions |
| `exercises.md` | 5 exercises from algorithm selection to design |
| `code-examples/` | Simple load balancer implementation in Python |
| `diagrams/` | Load balancing topology diagrams |

---

## Success Criteria

You've mastered Day 3 when you can:
- [ ] Explain 4 load balancing algorithms and when to use each
- [ ] Describe the difference between L4 and L7 load balancing
- [ ] Explain what a health check is and what happens when a server fails
- [ ] Describe sticky sessions and their tradeoffs
- [ ] Design a load balancing strategy for a stateful application

---

## Interview Questions for This Day
- "How does a load balancer decide which server to send a request to?"
- "What happens when a server behind a load balancer goes down?"
- "What are sticky sessions and when would you use them?"
- "What's the difference between a Layer 4 and Layer 7 load balancer?"
