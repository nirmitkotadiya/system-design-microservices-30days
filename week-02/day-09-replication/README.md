# Day 9: Replication Strategies

## "How Do You Keep Multiple Copies of Data in Sync?"

**Estimated Time**: 90 minutes  
**Difficulty**: Advanced  
**Prerequisites**: Days 1–8 complete

---

## Learning Objectives
- Explain leader-follower, multi-leader, and leaderless replication
- Describe synchronous vs. asynchronous replication tradeoffs
- Explain replication lag and its consequences
- Describe conflict resolution strategies for multi-leader replication
- Design a high-availability database setup

---

## Quick Summary

Replication means keeping a copy of the same data on multiple machines. You do this for two reasons: fault tolerance (if one machine dies, others have the data) and read scaling (spread read load across replicas). But keeping replicas in sync is harder than it sounds.

The core insight: **replication lag is inevitable in asynchronous systems. Your application must be designed to handle it.**

---

## Files in This Folder

| File | Description |
|------|-------------|
| `concepts.md` | Leader-follower, multi-leader, leaderless replication |
| `exercises.md` | 5 exercises from HA design to conflict resolution |
| `diagrams/` | Replication topology diagrams |

---

## Success Criteria

You've mastered Day 9 when you can:
- [ ] Explain the three replication models and their tradeoffs
- [ ] Describe synchronous vs. asynchronous replication
- [ ] Explain what replication lag is and how it affects applications
- [ ] Describe how multi-leader replication handles conflicts
- [ ] Design a high-availability PostgreSQL setup

---

## Interview Questions for This Day
- "How does database replication work?"
- "What is replication lag and how do you handle it?"
- "What's the difference between synchronous and asynchronous replication?"
- "How does Cassandra achieve high availability without a leader?"
