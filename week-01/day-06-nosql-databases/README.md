# Day 6: NoSQL Databases

## "When SQL Isn't the Right Tool for the Job"

**Estimated Time**: 90 minutes  
**Difficulty**: Intermediate  
**Prerequisites**: Days 1–5 complete

---

## Learning Objectives
- Explain the four main NoSQL database types and their use cases
- Describe when to choose NoSQL over SQL
- Understand document databases (MongoDB), key-value stores (Redis/DynamoDB), column stores (Cassandra), and graph databases (Neo4j)
- Explain eventual consistency and BASE properties
- Design a data model for a document database
- Know the tradeoffs of each NoSQL type

---

## Quick Summary

NoSQL databases emerged to solve problems that SQL databases handle poorly: massive scale, flexible schemas, and specific access patterns. But "NoSQL" is not one thing — it's four very different types of databases, each optimized for different problems.

The core insight: **choose your database based on your access patterns, not your data shape**. The question isn't "is my data relational?" — it's "how will I query this data?"

---

## Files in This Folder

| File | Description |
|------|-------------|
| `concepts.md` | Document, key-value, column, graph databases; BASE vs ACID |
| `exercises.md` | 5 exercises from database selection to data modeling |
| `code-examples/` | MongoDB and Redis examples |
| `diagrams/` | NoSQL data model comparisons |

---

## Success Criteria

You've mastered Day 6 when you can:
- [ ] Name the four NoSQL types and give a real-world example of each
- [ ] Explain BASE properties and how they differ from ACID
- [ ] Design a document model for a given domain
- [ ] Choose the right database for 5 different scenarios
- [ ] Explain why Cassandra is good for time-series data
- [ ] Describe the tradeoffs of eventual consistency

---

## Interview Questions for This Day
- "When would you choose MongoDB over PostgreSQL?"
- "What is eventual consistency and when is it acceptable?"
- "How does Cassandra achieve high write throughput?"
- "What's the difference between a document database and a key-value store?"
