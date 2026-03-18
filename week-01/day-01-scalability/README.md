# Day 1: Scalability Fundamentals

## "Why Does My App Crash When It Gets Popular?"

**Estimated Time**: 90 minutes  
**Difficulty**: Beginner  
**Prerequisites**: Basic programming knowledge

---

## Learning Objectives
- Distinguish between vertical and horizontal scaling
- Explain latency vs. throughput and why both matter
- Describe the three tiers of a web application
- Identify the bottleneck in a simple system
- Sketch a basic scalable architecture

---

## Quick Summary

Scalability is the ability of a system to handle increased load. But "load" is vague — it could mean more users, more data, more requests per second, or more complex queries. Today you'll build the mental model for thinking about scale before you ever touch a distributed system.

The core insight: **every system has a bottleneck**. Your job as a system designer is to find it, fix it, and find the next one.

---

## Files in This Folder

| File | Description |
|------|-------------|
| `concepts.md` | Deep dive: vertical vs. horizontal scaling, latency, throughput, 3-tier architecture |
| `exercises.md` | 5 progressive exercises from basic to design challenge |
| `code-examples/` | Python examples demonstrating scaling concepts |
| `diagrams/` | Architecture diagrams with Mermaid.js |

---

## Success Criteria

You've mastered Day 1 when you can:
- [ ] Explain vertical vs. horizontal scaling without looking it up
- [ ] Define latency and throughput and give units for each
- [ ] Draw a 3-tier architecture from memory
- [ ] Identify the bottleneck in a given scenario
- [ ] Explain what "stateless" means and why it matters for scaling

---

## Interview Questions for This Day
- "What's the difference between scaling up and scaling out?"
- "How would you handle a sudden 10x spike in traffic?"
- "What does it mean for a service to be stateless?"
