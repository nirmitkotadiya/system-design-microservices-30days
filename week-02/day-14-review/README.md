# Day 14: Week 2 Review & Mini-Design Challenge

## "Distributed Data Systems — Putting It All Together"

**Estimated Time**: 2 hours  
**Difficulty**: Advanced  
**Prerequisites**: Days 8–13 complete

---

## Learning Objectives
- Synthesize Week 2 concepts into a coherent design
- Apply CAP theorem reasoning to real design decisions
- Design a distributed cache from scratch
- Practice the system design interview framework

---

## Quick Summary

Week 2 was about the hard problems of distributed data: consistency, replication, sharding, and coordination. Today you'll apply all of it to design a distributed cache — a system that requires careful thinking about all these concepts simultaneously.

---

## Files in This Folder

| File | Description |
|------|-------------|
| `concepts.md` | Week 2 review and key mental models |
| `exercises.md` | Distributed cache design challenge |

---

## Week 2 Key Insights

1. **CAP**: You can't have consistency, availability, AND partition tolerance. Choose based on your use case.

2. **Replication**: Leader-follower for simplicity, leaderless for availability. Replication lag is inevitable.

3. **Sharding**: Solves write scaling but adds complexity. Consistent hashing minimizes data movement.

4. **Message queues**: Decouple services, enable async processing, provide fault isolation.

5. **Rate limiting**: Protect your system and ensure fair access. Sliding window counter is the practical choice.

---

## Success Criteria

You've mastered Week 2 when you can:
- [ ] Apply CAP theorem to a real design decision
- [ ] Design a replication strategy for high availability
- [ ] Choose a sharding strategy and shard key for a given system
- [ ] Design an event-driven architecture using message queues
- [ ] Implement a distributed rate limiter

---

## Interview Questions for This Week (Review)
- "Design a distributed cache"
- "How does Cassandra achieve high availability?"
- "What is consistent hashing and why is it useful?"
- "How would you design a rate limiter for a public API?"
