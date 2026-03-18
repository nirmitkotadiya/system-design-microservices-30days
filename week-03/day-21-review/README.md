# Day 21: Week 3 Review & Mini-Design Challenge

## "Microservices in Practice"

**Estimated Time**: 2 hours  
**Difficulty**: Advanced  
**Prerequisites**: Days 15–20 complete

---

## Learning Objectives
- Synthesize Week 3 concepts into a coherent microservices design
- Apply service decomposition, API design, and observability together
- Design a ride-sharing backend from scratch

---

## Quick Summary

Week 3 covered the operational realities of microservices: how services find each other, how they communicate, how distributed transactions work, how you observe them, and how you deliver content efficiently. Today you'll apply all of it.

---

## Files in This Folder

| File | Description |
|------|-------------|
| `concepts.md` | Week 3 review and key mental models |
| `exercises.md` | Ride-sharing backend design challenge |

---

## Week 3 Key Insights

1. **Microservices**: Organizational pattern as much as technical. Start with a monolith.

2. **API Design**: APIs are permanent contracts. Design them carefully.

3. **Service Discovery**: Services need to find each other dynamically. Use a registry or DNS.

4. **Distributed Transactions**: Avoid them when possible. Use Sagas when necessary.

5. **Observability**: Metrics, logs, traces. Design it in from day one.

6. **CDN**: The speed of light is a hard limit. Put content closer to users.

---

## Success Criteria

You've mastered Week 3 when you can:
- [ ] Decompose a system into microservices with appropriate boundaries
- [ ] Design REST APIs following best practices
- [ ] Explain service discovery and circuit breakers
- [ ] Design a saga for a distributed transaction
- [ ] Design an observability strategy
- [ ] Design a CDN strategy

---

## Interview Questions for This Week (Review)
- "Design the backend for a ride-sharing app"
- "How do you handle distributed transactions in microservices?"
- "How would you debug a latency spike in a microservices system?"
- "What is a service mesh and why would you use one?"
