# Day 8: CAP Theorem

## "You Can Only Pick Two — But It's More Complicated Than That"

**Estimated Time**: 90 minutes  
**Difficulty**: Intermediate-Advanced  
**Prerequisites**: Week 1 complete

---

## Learning Objectives
- State the CAP theorem precisely and explain what it actually means
- Classify real databases by their CAP properties
- Explain why "CA" systems don't really exist in distributed systems
- Describe PACELC as a more nuanced model than CAP
- Apply CAP reasoning to real design decisions

---

## Quick Summary

The CAP theorem states that a distributed system can only guarantee two of three properties: Consistency, Availability, and Partition Tolerance. But this is often misunderstood. In practice, network partitions always happen — so the real choice is between consistency and availability when a partition occurs.

The core insight: **CAP is not a design choice you make once. It's a tradeoff you make per operation, per use case.**

---

## Files in This Folder

| File | Description |
|------|-------------|
| `concepts.md` | CAP theorem, PACELC, real database classifications |
| `exercises.md` | 5 exercises from classification to design decisions |
| `diagrams/` | CAP triangle, partition scenario diagrams |

---

## Success Criteria

You've mastered Day 8 when you can:
- [ ] State the CAP theorem precisely
- [ ] Explain why "CA" is not a real option in distributed systems
- [ ] Classify MongoDB, Cassandra, HBase, and DynamoDB by CAP properties
- [ ] Explain PACELC and why it's more useful than CAP
- [ ] Make a CAP-informed database choice for a given scenario

---

## Interview Questions for This Day
- "Explain the CAP theorem"
- "Is it possible to have a CA system? Why or why not?"
- "How does Cassandra handle network partitions?"
- "When would you choose availability over consistency?"
