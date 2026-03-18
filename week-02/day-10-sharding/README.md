# Day 10: Partitioning & Sharding

## "When One Database Isn't Enough"

**Estimated Time**: 90 minutes  
**Difficulty**: Advanced  
**Prerequisites**: Days 1–9 complete

---

## Learning Objectives
- Explain why sharding is necessary and when to use it
- Compare range-based, hash-based, and directory-based sharding
- Identify and solve the hot shard problem
- Explain cross-shard queries and their limitations
- Design a sharding strategy for a given system

---

## Quick Summary

Sharding (also called partitioning) splits your data across multiple databases. Each shard holds a subset of the data. This allows you to scale writes horizontally — something read replicas can't do.

The core insight: **sharding solves write scalability but introduces enormous complexity. Exhaust all other options first.**

---

## Files in This Folder

| File | Description |
|------|-------------|
| `concepts.md` | Range, hash, directory sharding; hot shards; cross-shard queries |
| `exercises.md` | 5 exercises from shard key selection to resharding |
| `code-examples/` | Sharding router implementation |
| `diagrams/` | Sharding topology diagrams |

---

## Success Criteria

You've mastered Day 10 when you can:
- [ ] Explain the three sharding strategies and their tradeoffs
- [ ] Choose an appropriate shard key for a given system
- [ ] Explain what a hot shard is and how to prevent it
- [ ] Describe the challenges of cross-shard queries
- [ ] Explain how to rebalance shards when adding new nodes

---

## Interview Questions for This Day
- "How would you shard a user database?"
- "What is a hot shard and how do you prevent it?"
- "What are the challenges of cross-shard queries?"
- "How do you handle resharding when you need to add more shards?"
