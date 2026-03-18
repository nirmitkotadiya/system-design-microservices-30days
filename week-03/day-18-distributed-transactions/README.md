# Day 18: Distributed Transactions

## "ACID Across Multiple Services — The Hardest Problem in Microservices"

**Estimated Time**: 90 minutes  
**Difficulty**: Advanced  
**Prerequisites**: Days 1–17 complete

---

## Learning Objectives
- Explain why distributed transactions are hard
- Describe the Two-Phase Commit (2PC) protocol and its limitations
- Explain the Saga pattern and its two implementations
- Design a saga for a given distributed transaction
- Explain eventual consistency and how to design for it

---

## Quick Summary

In a monolith with a single database, ACID transactions are free. In microservices with separate databases, there's no such thing as a free transaction. You must choose between 2PC (strong consistency, low availability) or Sagas (eventual consistency, high availability).

The core insight: **distributed transactions are fundamentally hard. The best strategy is to design your system to minimize the need for them.**

---

## Files in This Folder

| File | Description |
|------|-------------|
| `concepts.md` | 2PC, Saga pattern, choreography vs. orchestration |
| `exercises.md` | 5 exercises from saga design to failure handling |
| `code-examples/` | Saga orchestrator implementation |

---

## Success Criteria

You've mastered Day 18 when you can:
- [ ] Explain why 2PC is problematic in microservices
- [ ] Describe the Saga pattern and its two implementations
- [ ] Design a saga for a given distributed transaction
- [ ] Explain compensating transactions
- [ ] Design a system that minimizes distributed transactions

---

## Interview Questions for This Day
- "How do you handle transactions across multiple microservices?"
- "What is the Saga pattern?"
- "What's the difference between choreography and orchestration in sagas?"
- "What is a compensating transaction?"
