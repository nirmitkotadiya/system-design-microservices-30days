# Day 7: Week 1 Review & Mini-Design Challenge

## "Putting It All Together"

**Estimated Time**: 2 hours  
**Difficulty**: Intermediate  
**Prerequisites**: Days 1–6 complete

---

## Learning Objectives
- Synthesize all Week 1 concepts into a coherent design
- Practice the system design interview framework
- Identify gaps in your understanding
- Build a complete URL shortener design from scratch

---

## Quick Summary

Today is about synthesis. You've learned scalability, networking, load balancing, caching, SQL, and NoSQL. Now you'll apply all of it to design a real system: a URL shortener (like bit.ly).

This is a classic system design interview question. It's simple enough to design in 45 minutes but complex enough to reveal whether you understand the fundamentals.

---

## Files in This Folder

| File | Description |
|------|-------------|
| `concepts.md` | System design interview framework + Week 1 review |
| `exercises.md` | URL shortener design challenge (full walkthrough) |
| `my-design/` | Template for your own design |

---

## The System Design Interview Framework

Use this framework for every design problem:

1. **Clarify requirements** (5 min)
   - Functional requirements: What does the system do?
   - Non-functional requirements: Scale, latency, availability

2. **Estimate scale** (5 min)
   - Users, requests per second, storage, bandwidth

3. **High-level design** (10 min)
   - Draw the major components
   - Identify the data flow

4. **Deep dive** (20 min)
   - Database schema
   - API design
   - Key algorithms
   - Bottlenecks and solutions

5. **Discuss tradeoffs** (5 min)
   - What did you sacrifice?
   - What would you do differently at 10x scale?

---

## Success Criteria

You've mastered Day 7 when you can:
- [ ] Design a URL shortener end-to-end in 45 minutes
- [ ] Estimate scale (RPS, storage, bandwidth) for a given system
- [ ] Identify the bottlenecks in your design
- [ ] Discuss tradeoffs in your design choices
- [ ] Apply the 5-step framework to any design problem

---

## Interview Questions for This Week (Review)
- "Design a URL shortener"
- "How would you scale a web application from 1,000 to 1,000,000 users?"
- "What's the difference between SQL and NoSQL? When would you use each?"
- "How does caching improve system performance?"
