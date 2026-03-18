# Day 29: Whiteboard Practice — Interview Framework

## The System Design Interview Framework

### Step 1: Clarify Requirements (5 minutes)

Never start designing without clarifying. Ask:

**Functional requirements**:
- "What are the core features we need to support?"
- "Are there any features we should explicitly exclude?"
- "Who are the users? (consumers, businesses, both?)"

**Non-functional requirements**:
- "What's the expected scale? (users, requests per second)"
- "What are the latency requirements?"
- "What's the availability requirement?"
- "Is consistency or availability more important?"

**Constraints**:
- "Are there any technology constraints?"
- "Any regulatory requirements? (GDPR, PCI DSS)"

---

### Step 2: Estimate Scale (5 minutes)

Back-of-envelope calculations show you can reason about scale.

**Estimation formulas**:

```
Requests per second:
  Daily active users × requests per user per day ÷ 86,400

Storage per year:
  Writes per second × record size × 86,400 × 365

Bandwidth:
  Requests per second × average response size

Cache size:
  Daily reads × record size × cache hit rate × 20% (hot data)
```

**Common numbers to memorize**:
```
1 day = 86,400 seconds ≈ 100,000 seconds (for easy math)
1 month = 2.5M seconds
1 year = 31.5M seconds

1KB = 1,000 bytes
1MB = 1,000,000 bytes
1GB = 1,000,000,000 bytes
1TB = 1,000,000,000,000 bytes

1M users × 1KB = 1GB
1B users × 1KB = 1TB
```

---

### Step 3: High-Level Design (10 minutes)

Draw the major components:
- Client (web, mobile)
- Load balancer
- Application servers
- Cache
- Database(s)
- Message queue (if needed)
- CDN (if needed)

Show the data flow for the most important use case.

---

### Step 4: Deep Dive (15 minutes)

Pick the most interesting/challenging components:

**Database design**:
- Schema (tables, columns, indexes)
- SQL vs. NoSQL choice
- Sharding strategy (if needed)

**Key algorithms**:
- How do you generate unique IDs?
- How do you compute the feed?
- How do you handle the celebrity problem?

**Bottleneck analysis**:
- Where is the bottleneck at current scale?
- How does it change at 10x scale?

---

### Step 5: Tradeoffs (5 minutes)

Proactively discuss:
- "I chose X over Y because..."
- "The tradeoff here is..."
- "At 10x scale, I would change..."

---

## Common Interview Mistakes

### Mistake 1: Jumping to Solutions
**Wrong**: "I'd use Kafka for this."  
**Right**: "Let me clarify the requirements first..."

### Mistake 2: Designing in Silence
**Wrong**: Drawing without explaining  
**Right**: "I'm drawing the load balancer here because..."

### Mistake 3: Ignoring Scale
**Wrong**: Designing for 100 users when the problem says 100M  
**Right**: Estimate scale first, let it drive your design

### Mistake 4: Not Discussing Tradeoffs
**Wrong**: "I'll use PostgreSQL."  
**Right**: "I'll use PostgreSQL because we need ACID transactions. The tradeoff is that it's harder to scale writes horizontally."

### Mistake 5: Designing the Perfect System
**Wrong**: Designing for 1 billion users on day one  
**Right**: "I'll start with this simple design and explain how it evolves as scale grows."

### Mistake 6: Not Asking for Feedback
**Wrong**: Designing for 45 minutes without checking in  
**Right**: "Does this direction make sense? Should I go deeper on any component?"

---

## Estimation Practice

Practice these until they're automatic:

**Twitter**:
```
500M tweets/day ÷ 86,400 = ~6,000 tweets/second
Read:write = 100:1 → 600,000 reads/second
Each tweet: 280 chars = ~280 bytes
Storage: 6,000 × 280 × 86,400 × 365 = ~54TB/year
```

**URL Shortener**:
```
100M URLs/day ÷ 86,400 = ~1,200 writes/second
Read:write = 100:1 → 120,000 reads/second
Each URL: ~500 bytes
Storage: 1,200 × 500 × 86,400 × 365 = ~19TB/year
```

**Instagram**:
```
1B users, 100M photos/day
100M ÷ 86,400 = ~1,200 photo uploads/second
Each photo: ~1MB
Storage: 1,200 × 1MB × 86,400 × 365 = ~38PB/year
```

---

## The "What If" Questions

Interviewers will ask "what if scale is 10x?" Be ready:

| Component | At 1x | At 10x |
|-----------|-------|--------|
| App servers | 10 servers | 100 servers (add more) |
| Database reads | Read replicas | More replicas + caching |
| Database writes | Single primary | Sharding |
| Cache | Single Redis | Redis Cluster |
| Message queue | Single Kafka cluster | More partitions/brokers |
