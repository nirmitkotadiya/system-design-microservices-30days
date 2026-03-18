# My Twitter Design — Learner Template

Use this template to practice designing Twitter from scratch. Fill in each section before looking at the reference design. This is your interview practice space.

---

## Step 1: Clarify Requirements (5 minutes)

Before designing anything, ask clarifying questions. Write your answers here.

**Functional Requirements** (what the system does):
- [ ] Users can post tweets (max ___ characters)
- [ ] Users can follow other users
- [ ] Users can see a home timeline (tweets from people they follow)
- [ ] Users can search tweets
- [ ] Other features: _______________

**Non-Functional Requirements** (how the system performs):
- Daily Active Users: _______________
- Tweets per day: _______________
- Read/write ratio: _______________
- Latency requirement: _______________
- Consistency requirement: _______________
- Availability requirement: _______________

**Out of Scope** (what you're NOT designing):
- _______________
- _______________

---

## Step 2: Capacity Estimation (5 minutes)

Show your math. Interviewers want to see your reasoning, not just the answer.

**Storage**:
```
Tweets per day: ___
Tweet size (avg): ___ bytes
Storage per day: ___
Storage per year: ___
With replication (3x): ___
```

**Bandwidth**:
```
Write bandwidth: ___ tweets/sec × ___ bytes = ___ MB/s
Read bandwidth: ___ reads/sec × ___ bytes = ___ MB/s
```

**Servers**:
```
Assuming ___ requests/server/sec:
Write servers needed: ___
Read servers needed: ___
```

---

## Step 3: High-Level Design (10 minutes)

Draw your architecture here. Use ASCII art or describe the components.

```
[Draw your architecture here]

Hint: Start with these components:
- Client (web/mobile)
- Load Balancer
- API Servers
- Database(s)
- Cache
- Message Queue (if needed)
```

**Key components and their responsibilities**:

| Component | Responsibility | Technology Choice |
|-----------|---------------|-------------------|
| | | |
| | | |
| | | |

---

## Step 4: Deep Dive — Tweet Storage

**Database schema**:
```sql
-- Write your schema here
CREATE TABLE tweets (
    -- your columns
);

CREATE TABLE users (
    -- your columns
);

CREATE TABLE follows (
    -- your columns
);
```

**Indexing strategy**:
- What indexes do you need?
- Why?

**Sharding strategy**:
- How do you shard the tweets table?
- What's your shard key?
- What are the tradeoffs?

---

## Step 5: Deep Dive — Timeline Generation

This is the hardest part of Twitter's design. Two approaches:

**Approach A: Fan-out on Write (Push)**
```
When user posts tweet:
  → Find all N followers
  → Write tweet to each follower's timeline cache
  
Read timeline:
  → Just read from cache (fast!)
  
Problem: Celebrity with 10M followers posts → 10M cache writes
```

Your analysis:
- When does this work well?
- When does it break down?
- How would you handle celebrities?

**Approach B: Fan-out on Read (Pull)**
```
When user posts tweet:
  → Just store the tweet
  
Read timeline:
  → Find all people user follows
  → Fetch their recent tweets
  → Merge and sort
  
Problem: User follows 1000 people → 1000 database reads per timeline load
```

Your analysis:
- When does this work well?
- When does it break down?

**Your hybrid approach**:
```
[Describe your solution here]
```

---

## Step 6: Deep Dive — Search

How would you implement tweet search?

**Approach**:
- Technology: _______________
- Indexing strategy: _______________
- How do you handle real-time tweets (< 1 second old)?
- How do you rank results?

---

## Step 7: Identify Bottlenecks

What are the top 3 bottlenecks in your design?

1. **Bottleneck**: _______________
   **Solution**: _______________

2. **Bottleneck**: _______________
   **Solution**: _______________

3. **Bottleneck**: _______________
   **Solution**: _______________

---

## Step 8: Tradeoffs

What tradeoffs did you make? Be explicit.

| Decision | Option A | Option B | Why I chose... |
|----------|----------|----------|----------------|
| Timeline | Fan-out on write | Fan-out on read | |
| Database | SQL | NoSQL | |
| Cache | Redis | Memcached | |

---

## Self-Assessment

After completing your design, compare it to the reference design in `../architecture-diagram.md`.

- [ ] Did I cover all functional requirements?
- [ ] Did I do capacity estimation?
- [ ] Did I address the timeline generation problem?
- [ ] Did I handle the celebrity problem?
- [ ] Did I identify the main bottlenecks?
- [ ] Did I discuss tradeoffs?
- [ ] Could I explain this in 45 minutes?

**What I got right**: _______________

**What I missed**: _______________

**What I'd do differently**: _______________
