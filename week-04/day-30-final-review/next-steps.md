# Next Steps: Your Path Forward

Finishing this 30-day curriculum is a milestone, not a finish line. Here's how to keep growing.

---

## Immediate Next Steps (Next 2 Weeks)

### 1. Mock Interviews

The biggest gap between knowing system design and performing well in interviews is practice under pressure. Do at least 5 mock interviews before your real ones.

**Options**:
- [Pramp](https://www.pramp.com) — Free peer-to-peer mock interviews
- [interviewing.io](https://interviewing.io) — Anonymous mock interviews with engineers from top companies
- [Hello Interview](https://www.hellointerview.com) — AI-powered system design practice
- Find a study partner on [Blind](https://www.teamblind.com) or [Reddit r/cscareerquestions](https://reddit.com/r/cscareerquestions)

**Protocol**: 45 minutes, timed, no notes. Record yourself if possible.

### 2. Fill Your Knowledge Gaps

From your Day 30 checklist, pick your top 3 gaps and spend 2-3 days on each:

- If weak on **distributed systems**: Read DDIA Chapters 5-9
- If weak on **databases**: Build a small app with PostgreSQL + Redis
- If weak on **case studies**: Do 2 more case studies from the exercises list

---

## Books (Ranked by Impact)

### Must Read

**Designing Data-Intensive Applications** — Martin Kleppmann
The bible of distributed systems. If you've been referencing it throughout this course, now read it cover to cover. Chapters 5-9 are particularly valuable.
[Available on O'Reilly](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/)

**System Design Interview (Vol 1 & 2)** — Alex Xu
The most practical interview prep book. Vol 1 covers fundamentals, Vol 2 covers advanced case studies. Read after this course to reinforce.

### Highly Recommended

**The Art of Scalability** — Abbott & Fisher
Covers organizational and technical scalability. The "Scale Cube" model is particularly useful.

**Building Microservices** — Sam Newman
The definitive guide to microservices architecture. Read after Week 3 to go deeper.

**Database Internals** — Alex Petrov
Deep dive into storage engines, distributed consensus, and database internals. For when you want to go beyond DDIA.

**Site Reliability Engineering** — Google SRE Team
Free online at [sre.google/books](https://sre.google/books/). Essential for understanding how Google operates at scale.

---

## Online Resources

### Blogs and Articles

**High Scalability** — [highscalability.com](http://highscalability.com)
Real architecture posts from companies like Twitter, Facebook, Amazon. Read 2-3 per week.

**The Morning Paper** — [blog.acolyer.org](https://blog.acolyer.org)
Academic papers explained accessibly. Great for going deep on specific topics.

**Netflix Tech Blog** — [netflixtechblog.com](https://netflixtechblog.com)
First-hand accounts of how Netflix solves engineering problems.

**Uber Engineering** — [eng.uber.com](https://eng.uber.com)
Deep dives into Uber's systems (location, matching, payments).

**AWS Architecture Blog** — [aws.amazon.com/blogs/architecture](https://aws.amazon.com/blogs/architecture)
Real-world architecture patterns on AWS.

### Video Courses

**Grokking the System Design Interview** — Educative.io
The most popular system design course. Good for interview prep.

**MIT 6.824: Distributed Systems** — [pdos.csail.mit.edu/6.824](https://pdos.csail.mit.edu/6.824)
Free MIT course. Rigorous, academic, excellent. Includes labs building Raft consensus.

**CMU 15-445: Database Systems** — [15445.courses.cs.cmu.edu](https://15445.courses.cs.cmu.edu)
Free CMU course on database internals. Excellent if you want to understand databases deeply.

---

## Projects to Build

Nothing cements learning like building. Here are projects ordered by difficulty:

### Beginner Projects (1-2 weeks each)

**1. URL Shortener (Full Stack)**
Build the Day 22 design for real:
- Python/FastAPI backend
- PostgreSQL for storage
- Redis for caching
- Deploy on Railway or Render
- Add analytics dashboard

**2. Rate Limiter Library**
Implement all 4 algorithms from Day 13:
- Token bucket, leaky bucket, sliding window log, fixed window
- Redis-backed for distributed use
- Publish to PyPI
- Write benchmarks comparing algorithms

**3. Consistent Hash Ring**
Extend the Day 11 code example:
- Add virtual nodes
- Simulate node addition/removal
- Visualize the ring with matplotlib
- Benchmark key distribution

### Intermediate Projects (2-4 weeks each)

**4. Mini Redis**
Build a subset of Redis from scratch:
- TCP server (handle multiple connections)
- GET, SET, DEL, EXPIRE commands
- RDB persistence (snapshot to disk)
- Benchmark against real Redis

**5. Distributed Key-Value Store**
Extend the Day 23 LSM tree:
- Add HTTP API
- Add replication (leader-follower)
- Add consistent hashing for sharding
- Test with chaos (kill nodes, partition network)

**6. Message Queue**
Build a simple Kafka-like system:
- Topics and partitions
- Producer and consumer APIs
- At-least-once delivery
- Consumer groups with offset tracking

### Advanced Projects (1-3 months each)

**7. Distributed Task Scheduler**
Design from the Day 30 exercises:
- Cron-like job scheduling
- Distributed workers (no duplicate execution)
- Failure handling and retry
- Web UI for job management

**8. Real-Time Chat Application**
WhatsApp-lite:
- WebSocket connections
- Message delivery receipts
- Group chats
- Offline message queuing
- Deploy with Docker Compose

**9. Video Streaming Service**
Netflix-lite:
- Video upload and transcoding (FFmpeg)
- HLS adaptive bitrate streaming
- CDN simulation with nginx
- Basic recommendation (collaborative filtering)

---

## Communities to Join

**Discord Servers**:
- [Coding Interview Prep](https://discord.gg/coding-interview) — Active community for interview prep
- [CS Career Hub](https://discord.gg/cscareerhub) — Career advice and mock interviews

**Reddit**:
- [r/cscareerquestions](https://reddit.com/r/cscareerquestions) — Career advice
- [r/ExperiencedDevs](https://reddit.com/r/ExperiencedDevs) — Senior engineer discussions
- [r/systemdesign](https://reddit.com/r/systemdesign) — System design discussions

**Twitter/X**:
Follow engineers at companies you're interested in. Many share architecture insights publicly.

---

## Your 90-Day Plan

### Days 1-30 (Done ✅)
Foundations, distributed systems, microservices, case studies.

### Days 31-60
- 5 mock interviews
- Read DDIA Chapters 5-9
- Build one intermediate project
- Do 10 more case study designs (timed)

### Days 61-90
- 5 more mock interviews
- Apply to target companies
- Build one advanced project
- Read company engineering blogs for companies you're interviewing at

---

## A Final Note

System design is a skill that compounds. Every system you build, every architecture post you read, every mock interview you do makes the next one easier.

The engineers who ace these interviews aren't necessarily smarter — they've just seen more patterns. You've now seen the core patterns. Keep building, keep reading, keep practicing.

Good luck. You've got this.
