# Day 5: SQL Databases Deep Dive

## "The Foundation That Everything Else Is Built On"

**Estimated Time**: 2 hours  
**Difficulty**: Intermediate  
**Prerequisites**: Days 1–4 complete

---

## Learning Objectives
- Explain ACID properties and why they matter
- Design a normalized database schema
- Understand indexes: B-tree, hash, composite, covering
- Explain query optimization and the query planner
- Describe common SQL scaling patterns: read replicas, connection pooling
- Know when SQL is the right choice (and when it isn't)

---

## Quick Summary

SQL databases have been the backbone of software systems for 50 years. Despite the NoSQL movement, SQL databases (PostgreSQL, MySQL) are still the right choice for the majority of applications. Understanding them deeply — not just how to write queries, but how they work internally — is essential for system design.

The core insight: **SQL databases give you ACID guarantees for free. Everything else you build will be trying to approximate these guarantees at scale.**

---

## Files in This Folder

| File | Description |
|------|-------------|
| `concepts.md` | ACID, indexes, query optimization, scaling patterns |
| `exercises.md` | 5 exercises from schema design to query optimization |
| `code-examples/` | PostgreSQL examples with indexes and query analysis |
| `diagrams/` | B-tree index visualization, query plan diagrams |

---

## Success Criteria

You've mastered Day 5 when you can:
- [ ] Explain each ACID property with a real-world example
- [ ] Design a normalized schema for a given domain
- [ ] Explain how a B-tree index works and when to use one
- [ ] Read a query execution plan and identify bottlenecks
- [ ] Describe the N+1 query problem and how to fix it
- [ ] Explain connection pooling and why it's necessary

---

## Interview Questions for This Day
- "What does ACID stand for and why does it matter?"
- "How does a database index work? What are the tradeoffs?"
- "What is the N+1 query problem?"
- "How would you scale a PostgreSQL database to handle 10x more read traffic?"
