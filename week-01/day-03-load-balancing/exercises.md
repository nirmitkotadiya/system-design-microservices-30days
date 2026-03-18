# Day 3: Exercises — Load Balancing

---

## Exercise 1: Basic Comprehension (15 minutes)

1. You have 3 servers. Server 1 has 2 active connections, Server 2 has 8, Server 3 has 1. Using least-connections, which server gets the next request?

2. A user logs into your app on Server 1. Their session is stored in Server 1's memory. The next request goes to Server 2. What happens? How do you fix this without sticky sessions?

3. Your health check endpoint just returns `200 OK` always, even when the database is down. What's the problem? What should it do instead?

4. You have servers in Virginia and Tokyo. A user in Sydney makes a request. How does global load balancing route them to the right server?

5. What is "connection draining" and why is it important when deploying new code?

---

## Exercise 2: Hands-On — Run the Load Balancer (25 minutes)

```bash
cd code-examples/
python simple_load_balancer.py
```

This starts a simple load balancer with 3 simulated backend servers.

Experiment with:
1. Sending 100 requests — which server gets the most?
2. Marking Server 2 as "unhealthy" — does traffic redistribute?
3. Changing the algorithm from round-robin to least-connections — does distribution change?

Record your observations.

---

## Exercise 3: Design Problem (25 minutes)

### Scenario: E-Commerce Checkout

You're designing the load balancing strategy for an e-commerce site:
- 3 tiers: web servers, API servers, database servers
- Peak traffic: 50,000 requests/second during Black Friday
- Checkout process requires 5 sequential API calls
- Payment processing takes 2-3 seconds (external API call)
- Sessions must be maintained during checkout

**Design**:
1. What load balancing algorithm would you use for web servers? API servers?
2. How do you handle the stateful checkout session?
3. How do you handle the slow payment processing calls? (Hint: should these block a server thread?)
4. How do you ensure the load balancer itself doesn't become a single point of failure?
5. Draw the full architecture with load balancers at each tier.

---

## Exercise 4: Critical Thinking — Algorithm Tradeoffs (20 minutes)

A startup is debating which load balancing algorithm to use. They have:
- 5 app servers (identical hardware)
- Mix of requests: 80% are fast (< 50ms), 20% are slow (2-5 seconds, involve ML inference)
- Stateless application (sessions in Redis)

**Evaluate each algorithm for this scenario**:

| Algorithm | Would it work? | Problem (if any) | Score (1-5) |
|-----------|---------------|------------------|-------------|
| Round Robin | ? | ? | ? |
| Least Connections | ? | ? | ? |
| IP Hash | ? | ? | ? |
| Weighted RR | ? | ? | ? |
| Least Response Time | ? | ? | ? |

Which would you choose and why?

---

## Exercise 5: Challenge — Design a Multi-Region Load Balancer (30 minutes)

### Scenario: Global SaaS Application

Your SaaS app has users in:
- North America (40% of users)
- Europe (35% of users)
- Asia-Pacific (25% of users)

Requirements:
- Users must be routed to the nearest region (< 50ms latency)
- If a region goes down, traffic must failover to another region
- Some enterprise customers require their data to stay in Europe (data residency)
- You need to handle 100,000 RPS globally

**Design the global load balancing architecture**:

1. How do you route users to the nearest region? (DNS? Anycast? Both?)
2. How do you detect a regional failure and failover?
3. How do you handle the European data residency requirement?
4. How do you handle a user who travels from New York to London? Do they get re-routed?
5. What's your capacity planning? If NA goes down, can EU + APAC handle 100% of traffic?

---

## Hints

**Exercise 3**: For slow payment calls, think about async processing. Does the user need to wait synchronously?

**Exercise 4**: Think about what happens when all the slow ML requests pile up on one server with round-robin.

**Exercise 5, Q1**: DNS has TTL issues. Anycast routes at the network level. What are the tradeoffs?

---

## Self-Assessment Checklist

- [ ] I can explain 4 load balancing algorithms and their tradeoffs
- [ ] I understand why sticky sessions are a problem and how to avoid them
- [ ] I know the difference between L4 and L7 load balancing
- [ ] I can design a health check endpoint that actually validates server health
- [ ] I understand how global load balancing works
- [ ] I can identify when a load balancer itself becomes a bottleneck
