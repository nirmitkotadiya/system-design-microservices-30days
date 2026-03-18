# Day 1: Exercises — Scalability Fundamentals

Work through these exercises in order. Each builds on the previous.

---

## Exercise 1: Basic Comprehension (15 minutes)

Answer these questions in your own words (no copy-paste from concepts.md):

1. A startup has a single server handling 100 requests/second. They expect 10x growth next month. What are their two main options? What are the tradeoffs of each?

2. A system has p50 latency of 20ms and p99 latency of 2000ms. What does this tell you about the system? Is this acceptable for a user-facing API?

3. An e-commerce site stores user shopping carts in server memory. They want to add a second server. What problem will they face? How would you fix it?

4. Rank these from fastest to slowest: SSD read, RAM access, network call to a server in the same datacenter, network call to a server on another continent.

5. What is a "load parameter"? Give three examples for a social media application.

**Self-check**: Can you answer all five without looking at the concepts? If not, re-read the relevant section.

---

## Exercise 2: Hands-On Implementation (30 minutes)

### Build a Simple Load Simulator

Run the provided Python script to simulate load on a "server" and observe how response time degrades:

```bash
cd code-examples/
python load_simulator.py
```

Then answer:
1. At what RPS does the simulated server start showing degraded performance?
2. What happens to p99 latency as load increases?
3. How does adding a second "server" change the behavior?

If you can't run the code, trace through it manually and predict the output.

---

## Exercise 3: Design Problem (20 minutes)

### Scenario
You're the first engineer at a startup. You have a simple web app:
- Users can post text updates (like Twitter)
- 1,000 users, 100 requests/second
- Single server: 4 CPU, 16GB RAM, PostgreSQL on the same machine

**Task**: Draw (on paper or in a text diagram) what this architecture looks like today, and what it should look like when you hit 100,000 users.

Your diagram should show:
- Where the web servers are
- Where the database is
- How load is distributed
- Where sessions are stored

**Hint**: Think about which tier you'd scale first and why.

---

## Exercise 4: Critical Thinking — Tradeoff Analysis (20 minutes)

### The Stateful vs. Stateless Debate

A colleague says: "Storing sessions in server memory is faster than Redis. We should keep sessions local."

They're right that local memory is faster. But they're missing something important.

Write a 3-paragraph response that:
1. Acknowledges what they're right about
2. Explains the problem with their approach at scale
3. Proposes a solution that gets the best of both worlds

**Hint**: Think about what happens when you have 10 servers and a user's request can go to any of them.

---

## Exercise 5: Challenge — Extend the Concept (30 minutes)

### The Twitter Fan-Out Problem

Twitter has two types of users:
- **Regular users**: 200 followers
- **Celebrity users**: 10 million followers

When a user posts a tweet, Twitter needs to deliver it to all followers' home timelines.

**Approach A (Push model)**: When a tweet is posted, immediately write it to every follower's timeline cache.
- For a regular user: 200 writes
- For a celebrity: 10,000,000 writes

**Approach B (Pull model)**: Don't pre-compute timelines. When a user opens the app, fetch tweets from everyone they follow.
- For a user following 200 people: 200 reads
- For a user following a celebrity: 1 read (but the celebrity's feed is huge)

**Your task**:
1. What are the tradeoffs of each approach?
2. Which approach is better for regular users? For celebrities?
3. Can you design a hybrid approach? Describe it.
4. What load parameters would you use to decide which approach to use?

This is a real problem Twitter solved. We'll revisit it on Day 24.

---

## Hints

**Exercise 1, Q3**: Think about what "stateless" means. Where should state live if not on the server?

**Exercise 3**: The database is almost always the first bottleneck. What can you do to reduce load on it?

**Exercise 4**: Consider a CDN-like approach for sessions — a fast, distributed cache.

**Exercise 5**: The answer isn't one or the other. Think about user segmentation.

---

## Self-Assessment Checklist

After completing all exercises:
- [ ] I can explain vertical vs. horizontal scaling in one sentence each
- [ ] I understand why stateless services are required for horizontal scaling
- [ ] I can read a latency percentile table and explain what it means
- [ ] I can identify the bottleneck in a simple 3-tier architecture
- [ ] I understand the fan-out problem and can propose a solution
