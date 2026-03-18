# Day 11: Consistent Hashing

## "How to Add or Remove Servers Without Moving All Your Data"

**Estimated Time**: 90 minutes  
**Difficulty**: Advanced  
**Prerequisites**: Days 1–10 complete

---

## Learning Objectives
- Explain the problem that consistent hashing solves
- Describe the hash ring and how nodes are placed on it
- Explain virtual nodes and why they improve distribution
- Implement consistent hashing from scratch
- Describe how consistent hashing is used in real systems (Cassandra, CDNs)

---

## Quick Summary

Regular hash-based sharding has a fatal flaw: when you add or remove a server, almost all data needs to move. Consistent hashing solves this by ensuring that only K/N keys need to be remapped when a node is added or removed (where K is the number of keys and N is the number of nodes).

The core insight: **consistent hashing minimizes data movement during topology changes, making it practical to add and remove nodes in production.**

---

## Files in This Folder

| File | Description |
|------|-------------|
| `concepts.md` | Hash ring, virtual nodes, real-world applications |
| `exercises.md` | 5 exercises including implementation |
| `code-examples/` | Full consistent hashing implementation |
| `diagrams/` | Hash ring visualizations |

---

## Success Criteria

You've mastered Day 11 when you can:
- [ ] Explain why regular hashing fails when nodes are added/removed
- [ ] Describe the hash ring and how data is assigned to nodes
- [ ] Explain virtual nodes and their benefit
- [ ] Implement consistent hashing from scratch
- [ ] Describe how Cassandra uses consistent hashing

---

## Interview Questions for This Day
- "What is consistent hashing and why is it useful?"
- "What are virtual nodes and why do they improve consistent hashing?"
- "How does consistent hashing minimize data movement when adding a node?"
- "Where is consistent hashing used in real systems?"
