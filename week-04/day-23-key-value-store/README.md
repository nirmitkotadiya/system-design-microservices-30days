# Day 23: Design a Key-Value Store

## Learning Objectives
- Understand the internals of a distributed key-value store
- Implement core data structures (LSM trees, SSTables, bloom filters)
- Design for high availability, consistency, and partition tolerance
- Apply CAP theorem tradeoffs in a real system

## Estimated Time: 6-8 hours

## Prerequisites
- Day 8: CAP Theorem
- Day 9: Replication
- Day 10: Sharding
- Day 11: Consistent Hashing

## What You'll Build
A mental model (and partial implementation) of a system like Redis, DynamoDB, or Cassandra — a distributed key-value store that can handle millions of operations per second.

## Files in This Folder
- `README.md` — This file
- `concepts.md` — Deep dive into KV store internals
- `exercises.md` — 5 progressive exercises
- `code-examples/kv_store.py` — Working KV store implementation
- `diagrams/kv-architecture.md` — Architecture diagrams

## Success Criteria
- [ ] Can explain LSM trees vs B-trees tradeoffs
- [ ] Understand how DynamoDB achieves its guarantees
- [ ] Can design a KV store for a given set of requirements
- [ ] Know when to use a KV store vs other storage options
- [ ] Can answer "Design Redis" in an interview
