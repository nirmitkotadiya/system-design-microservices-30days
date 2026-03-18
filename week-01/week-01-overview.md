# Week 1: Foundations of Scalable Systems

## Focus Area
Building the mental models that underpin all system design. Before you can design Twitter, you need to understand why a single server fails, how data moves across a network, and what "scale" actually means in practice.

## Prerequisites
- Basic programming in any language
- Understanding of what HTTP is
- Familiarity with the concept of a database

## Learning Objectives
By the end of Week 1, you will be able to:
- Explain vertical vs. horizontal scaling and when to use each
- Describe how HTTP, TCP, and DNS work at a level useful for system design
- Design a load-balanced architecture with multiple strategies
- Choose between caching strategies (write-through, write-back, cache-aside)
- Explain when to use SQL vs. NoSQL and why
- Sketch a basic scalable architecture for a web application

## Day-by-Day Breakdown

| Day | Topic | Key Concept | Deliverable |
|-----|-------|-------------|-------------|
| 1 | Scalability Fundamentals | Vertical vs. horizontal scaling | Sketch a 3-tier architecture |
| 2 | Networking & Protocols | TCP/IP, HTTP, DNS, CDN | Trace a request from browser to DB |
| 3 | Load Balancing | Round-robin, least connections, consistent hashing | Design an LB strategy for a given scenario |
| 4 | Caching Strategies | Cache-aside, write-through, eviction policies | Choose the right cache strategy |
| 5 | SQL Databases Deep Dive | ACID, indexes, query optimization | Design a normalized schema |
| 6 | NoSQL Databases | Document, key-value, column, graph stores | Choose the right DB for 3 scenarios |
| 7 | Week 1 Review | Synthesis | Design a URL shortener (mini) |

## Required Tools
- Docker Desktop
- Python 3.9+
- Redis (via Docker): `docker run -p 6379:6379 redis`
- PostgreSQL (via Docker): `docker run -p 5432:5432 -e POSTGRES_PASSWORD=pass postgres`

## Success Criteria
You've mastered Week 1 when you can:
- [ ] Explain the difference between latency and throughput without looking it up
- [ ] Draw a load-balanced, cached, database-backed architecture from memory
- [ ] Explain why you'd choose MongoDB over PostgreSQL for a specific use case
- [ ] Describe what happens when a cache miss occurs
- [ ] Explain what a database index is and why it matters

## Resources for This Week
- DDIA Chapters 1–3 (Reliable, Scalable, Maintainable Applications; Data Models; Storage and Retrieval)
- [What is a CDN?](https://www.cloudflare.com/learning/cdn/what-is-a-cdn/)
- [PostgreSQL Documentation: Indexes](https://www.postgresql.org/docs/current/indexes.html)
- [Redis Documentation](https://redis.io/docs/)

## Progress Checklist
- [ ] Day 1: Scalability concepts read and exercises done
- [ ] Day 2: Networking concepts read and exercises done
- [ ] Day 3: Load balancing concepts read and exercises done
- [ ] Day 4: Caching concepts read and exercises done
- [ ] Day 5: SQL deep dive read and exercises done
- [ ] Day 6: NoSQL concepts read and exercises done
- [ ] Day 7: Review complete and mini-design done
