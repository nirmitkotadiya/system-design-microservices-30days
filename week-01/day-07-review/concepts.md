# Day 7: Week 1 Review — Key Concepts Summary

## Week 1 Mental Model Map

```
                        SCALABILITY
                            │
              ┌─────────────┼─────────────┐
              │             │             │
         Vertical       Horizontal    Measure
         (Scale Up)    (Scale Out)   (Metrics)
                            │
                    ┌───────┴───────┐
                    │               │
              Load Balance      Stateless
                    │           Services
              ┌─────┴─────┐
              │           │
           Layer 4     Layer 7
                            │
                    ┌───────┴───────┐
                    │               │
                 Cache           Database
                    │               │
              ┌─────┴─────┐   ┌────┴────┐
              │           │   │         │
           Strategies  Eviction  SQL    NoSQL
           (aside,     (LRU,    (ACID)  (BASE)
           write-thru) LFU)
```

---

## Quick Reference: When to Use What

### Scaling Strategy
| Situation | Solution |
|-----------|----------|
| < 10k RPS, simple app | Single server + vertical scaling |
| 10k-100k RPS | Load balancer + multiple app servers |
| 100k+ RPS | Caching + read replicas + CDN |
| 1M+ RPS | Sharding + microservices (Week 3) |

### Caching Strategy
| Situation | Strategy |
|-----------|----------|
| Read-heavy, occasional writes | Cache-aside |
| Must always have fresh data | Write-through |
| Write-heavy, can tolerate some loss | Write-back |
| Write-once, rarely read | Write-around |

### Database Selection
| Situation | Database |
|-----------|----------|
| Default choice | PostgreSQL |
| Need flexible schema | MongoDB |
| Need fast key lookup | Redis/DynamoDB |
| Time-series, high write throughput | Cassandra |
| Highly connected data | Neo4j |

---

## The 5 Numbers Every System Designer Should Know

```
1. Latency numbers:
   - Memory access: ~100ns
   - SSD read: ~100μs
   - Network (same DC): ~1ms
   - Network (cross-continent): ~100ms

2. Throughput estimates:
   - Single server: ~10k-50k RPS (simple requests)
   - With caching: 10x improvement
   - With CDN: 100x improvement for static content

3. Storage estimates:
   - 1 tweet: ~280 bytes
   - 1 photo: ~1MB
   - 1 video (1 min): ~50MB
   - 1 billion users × 1KB profile = 1TB

4. Availability:
   - 99%: 3.65 days downtime/year
   - 99.9%: 8.7 hours downtime/year
   - 99.99%: 52 minutes downtime/year
   - 99.999%: 5 minutes downtime/year

5. Scale of the internet:
   - Twitter: ~500M tweets/day = ~6k tweets/second
   - YouTube: ~500 hours of video uploaded/minute
   - Google: ~8.5 billion searches/day = ~100k/second
```

---

## Common Interview Mistakes (and How to Avoid Them)

### Mistake 1: Jumping to Solutions
**Wrong**: "I'd use Kafka for this."  
**Right**: "Let me clarify the requirements first. What's the expected scale? What are the consistency requirements?"

### Mistake 2: Ignoring Non-Functional Requirements
Always ask about:
- Scale (users, RPS, data volume)
- Latency requirements (p99 target)
- Availability requirements (99.9%? 99.99%?)
- Consistency requirements (strong vs. eventual)

### Mistake 3: Not Estimating
Back-of-envelope calculations show you can reason about scale:
```
URL shortener:
- 100M URLs created per day
- 100M / 86,400 seconds = ~1,200 writes/second
- Read:write ratio = 100:1 → 120,000 reads/second
- Each URL: ~500 bytes → 100M × 500B = 50GB/day
```

### Mistake 4: Not Discussing Tradeoffs
Every design decision has tradeoffs. Interviewers want to see that you understand them.

### Mistake 5: Designing for 1 Billion Users on Day 1
Start simple. Explain how you'd evolve the design as scale grows.

---

## Week 1 Checklist

Before moving to Week 2, verify you can:

**Scalability**
- [ ] Explain vertical vs. horizontal scaling
- [ ] Define latency and throughput with units
- [ ] Identify bottlenecks in a system

**Networking**
- [ ] Trace a full HTTP request
- [ ] Explain TCP vs. UDP tradeoffs
- [ ] Describe what a CDN does

**Load Balancing**
- [ ] Name 4 LB algorithms and their use cases
- [ ] Explain L4 vs. L7 load balancing
- [ ] Describe health checks and sticky sessions

**Caching**
- [ ] Explain cache-aside, write-through, write-back
- [ ] Describe LRU and LFU eviction
- [ ] Explain cache stampede and prevention

**SQL Databases**
- [ ] Explain ACID properties
- [ ] Describe how B-tree indexes work
- [ ] Identify the N+1 query problem

**NoSQL Databases**
- [ ] Name 4 NoSQL types with use cases
- [ ] Explain BASE vs. ACID
- [ ] Choose the right DB for a given scenario
