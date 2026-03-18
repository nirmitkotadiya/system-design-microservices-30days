# Week 2: Data at Scale

## Focus Area
When one database isn't enough. This week is about the hard problems that emerge when your data grows beyond what a single machine can handle — and the tradeoffs you must make to solve them.

## Prerequisites
- Week 1 complete
- Understanding of SQL and NoSQL basics
- Familiarity with what a distributed system is conceptually

## Learning Objectives
By the end of Week 2, you will be able to:
- Explain the CAP theorem and apply it to real database choices
- Design a replication strategy for high availability
- Shard a database and reason about the tradeoffs
- Implement consistent hashing and explain why it matters
- Choose between message queue systems (Kafka, RabbitMQ, SQS)
- Design a rate limiter using multiple algorithms

## Day-by-Day Breakdown

| Day | Topic | Key Concept | Deliverable |
|-----|-------|-------------|-------------|
| 8 | CAP Theorem | Consistency vs. availability tradeoff | Classify 5 real databases by CAP |
| 9 | Replication | Leader-follower, multi-leader, leaderless | Design HA setup for a given system |
| 10 | Partitioning & Sharding | Range, hash, directory-based sharding | Shard a user database |
| 11 | Consistent Hashing | Virtual nodes, ring topology | Implement consistent hashing |
| 12 | Message Queues & Streaming | Kafka, RabbitMQ, pub/sub patterns | Design an event-driven pipeline |
| 13 | Rate Limiting | Token bucket, leaky bucket, sliding window | Implement a rate limiter |
| 14 | Week 2 Review | Synthesis | Design a distributed cache |

## Required Tools
- Apache Kafka (via Docker Compose)
- Redis (for rate limiting examples)
- Python with `kafka-python` library

## Success Criteria
You've mastered Week 2 when you can:
- [ ] Explain why you can't have all three of CAP simultaneously
- [ ] Describe the difference between synchronous and asynchronous replication
- [ ] Explain what a "hot shard" is and how to prevent it
- [ ] Implement consistent hashing from scratch
- [ ] Explain the difference between Kafka and RabbitMQ
- [ ] Implement a token bucket rate limiter

## Resources for This Week
- DDIA Chapters 5–7 (Replication, Partitioning, Transactions)
- DDIA Chapter 9 (Consistency and Consensus)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [CAP Theorem Explained](https://www.ibm.com/topics/cap-theorem)
- [Consistent Hashing Paper](https://www.cs.princeton.edu/courses/archive/fall09/cos518/papers/chash.pdf)

## Progress Checklist
- [ ] Day 8: CAP theorem understood and databases classified
- [ ] Day 9: Replication strategies understood
- [ ] Day 10: Sharding strategies understood and schema designed
- [ ] Day 11: Consistent hashing implemented
- [ ] Day 12: Message queue patterns understood
- [ ] Day 13: Rate limiter implemented
- [ ] Day 14: Review complete and distributed cache designed
