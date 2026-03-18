# Day 15: Microservices Architecture

## "Breaking the Monolith — When and How"

**Estimated Time**: 90 minutes  
**Difficulty**: Advanced  
**Prerequisites**: Weeks 1–2 complete

---

## Learning Objectives
- Explain the difference between monoliths and microservices
- Apply domain-driven design to decompose a monolith
- Identify the pain points of microservices that nobody warns you about
- Design service boundaries using bounded contexts
- Explain the strangler fig pattern for migrating from monolith to microservices

---

## Quick Summary

Microservices are not a silver bullet. They solve real problems (independent deployment, team autonomy, technology flexibility) but introduce new ones (distributed systems complexity, network latency, data consistency). Understanding both sides is essential.

The core insight: **microservices are an organizational pattern as much as a technical one. If your team is small, a monolith is probably better.**

---

## Files in This Folder

| File | Description |
|------|-------------|
| `concepts.md` | Monolith vs. microservices, DDD, bounded contexts, migration patterns |
| `exercises.md` | 5 exercises from decomposition to migration strategy |
| `diagrams/` | Service decomposition diagrams |

---

## Success Criteria

You've mastered Day 15 when you can:
- [ ] Explain the tradeoffs between monolith and microservices
- [ ] Apply domain-driven design to decompose a system
- [ ] Identify appropriate service boundaries
- [ ] Describe the strangler fig migration pattern
- [ ] Explain why microservices require organizational changes

---

## Interview Questions for This Day
- "When would you choose microservices over a monolith?"
- "How do you decompose a monolith into microservices?"
- "What are the biggest challenges with microservices?"
- "What is a bounded context?"
