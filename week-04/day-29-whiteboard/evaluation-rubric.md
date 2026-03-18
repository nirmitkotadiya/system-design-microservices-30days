# System Design Interview Evaluation Rubric

Use this rubric to evaluate your own practice sessions or to give feedback to a peer.

---

## Scoring Guide

Each dimension is scored 1-5:
- **1**: Not addressed or fundamentally wrong
- **2**: Mentioned but incomplete or incorrect
- **3**: Adequate — covers the basics
- **4**: Good — shows depth and handles edge cases
- **5**: Excellent — senior engineer level, proactively addresses tradeoffs

---

## Dimension 1: Requirements Clarification (0-20 points)

| Score | Criteria |
|-------|----------|
| 1-4 | Jumped straight into design without asking questions |
| 5-8 | Asked some questions but missed important ones |
| 9-12 | Clarified functional requirements, estimated scale |
| 13-16 | Clarified functional + non-functional requirements, defined scope |
| 17-20 | Excellent scoping, identified ambiguities, set clear success criteria |

**Key questions to ask**:
- [ ] How many users? DAU vs MAU?
- [ ] Read/write ratio?
- [ ] Latency requirements?
- [ ] Consistency requirements (strong vs eventual)?
- [ ] Availability requirements (99.9% vs 99.99%)?
- [ ] Geographic distribution?
- [ ] What's in scope vs out of scope?

---

## Dimension 2: Capacity Estimation (0-15 points)

| Score | Criteria |
|-------|----------|
| 1-3 | No estimation attempted |
| 4-6 | Rough numbers without showing work |
| 7-9 | Estimated storage or bandwidth but not both |
| 10-12 | Estimated storage, bandwidth, and server count |
| 13-15 | Complete estimation with clear reasoning, used estimates to drive design decisions |

**Expected calculations**:
- [ ] Storage per day / per year
- [ ] Read/write throughput (requests/second)
- [ ] Bandwidth (MB/s)
- [ ] Number of servers needed
- [ ] Cache size estimation

---

## Dimension 3: High-Level Design (0-20 points)

| Score | Criteria |
|-------|----------|
| 1-4 | Missing major components or fundamentally wrong architecture |
| 5-8 | Basic components present but poorly connected |
| 9-12 | Reasonable architecture covering main use cases |
| 13-16 | Good architecture with appropriate technology choices |
| 17-20 | Excellent architecture, proactively addressed scalability, clear data flow |

**Expected components**:
- [ ] Client layer
- [ ] Load balancer / API gateway
- [ ] Application servers
- [ ] Database(s) with appropriate type (SQL vs NoSQL)
- [ ] Cache layer
- [ ] CDN (if applicable)
- [ ] Message queue (if applicable)

---

## Dimension 4: Deep Dive Quality (0-25 points)

| Score | Criteria |
|-------|----------|
| 1-5 | Stayed at surface level, no depth |
| 6-10 | Some depth on one component |
| 11-15 | Good depth on 1-2 components |
| 16-20 | Strong depth on key components, addressed edge cases |
| 21-25 | Excellent depth, proactively identified and solved hard problems |

**Deep dive areas** (pick 2-3 based on the problem):
- [ ] Database schema design
- [ ] Sharding strategy
- [ ] Caching strategy
- [ ] API design
- [ ] The hardest algorithmic problem (e.g., timeline generation, matching)

---

## Dimension 5: Scalability and Bottlenecks (0-10 points)

| Score | Criteria |
|-------|----------|
| 1-2 | No discussion of scalability |
| 3-4 | Mentioned scaling but no specifics |
| 5-6 | Identified main bottlenecks |
| 7-8 | Identified bottlenecks and proposed solutions |
| 9-10 | Proactively identified bottlenecks before being asked, proposed concrete solutions with tradeoffs |

**Common bottlenecks to address**:
- [ ] Database write throughput
- [ ] Hot keys / hot partitions
- [ ] Single points of failure
- [ ] Network bandwidth
- [ ] Thundering herd / cache stampede

---

## Dimension 6: Tradeoffs and Alternatives (0-10 points)

| Score | Criteria |
|-------|----------|
| 1-2 | No tradeoff discussion |
| 3-4 | Mentioned tradeoffs superficially |
| 5-6 | Discussed tradeoffs for 1-2 decisions |
| 7-8 | Discussed tradeoffs for major decisions, acknowledged limitations |
| 9-10 | Excellent tradeoff analysis throughout, showed awareness of alternatives |

**Tradeoffs to discuss**:
- [ ] SQL vs NoSQL
- [ ] Consistency vs availability
- [ ] Fan-out on write vs read (if applicable)
- [ ] Synchronous vs asynchronous processing
- [ ] Build vs buy (managed services)

---

## Total Score Interpretation

| Score | Level | Interpretation |
|-------|-------|----------------|
| 0-40 | Junior | Needs significant preparation |
| 41-60 | Mid-level | Solid foundation, needs more depth |
| 61-75 | Senior | Ready for most senior roles |
| 76-90 | Staff | Strong candidate for staff/principal |
| 91-100 | Principal | Exceptional, rare |

---

## Common Mistakes (Automatic Deductions)

These mistakes signal a lack of experience and will hurt your score:

- **Jumping to solution**: Starting to design before clarifying requirements (-10)
- **No estimation**: Designing without knowing the scale (-10)
- **Single point of failure**: Designing a system with no redundancy (-5)
- **Ignoring the hard problem**: Avoiding the most challenging aspect of the design (-10)
- **No tradeoffs**: Presenting one option as obviously correct without discussion (-5)
- **Inconsistent design**: Components that don't work together (-10)
- **Overengineering**: Proposing Kubernetes + service mesh for a 1000-user app (-5)

---

## Communication Rubric

Technical correctness is only half the battle. Communication matters too.

| Behavior | Good | Bad |
|----------|------|-----|
| Thinking out loud | "I'm considering X because..." | Silent for 2 minutes |
| Handling uncertainty | "I'm not sure, but I'd approach it by..." | Pretending to know |
| Responding to hints | Incorporates feedback gracefully | Ignores or argues |
| Time management | Covers all areas in 45 min | Spends 30 min on one component |
| Whiteboard/diagram | Clear, organized, labeled | Messy, unlabeled |

---

## Self-Assessment After Each Practice Session

1. What was my total score? ___/100
2. Which dimension was weakest? _______________
3. What specific thing will I practice before next session? _______________
4. Did I address the hardest part of the problem? _______________
5. Would I hire myself based on this performance? _______________
