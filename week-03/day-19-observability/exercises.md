# Day 19: Exercises — Observability & Monitoring

---

## Exercise 1: Basic Comprehension (15 minutes)

1. What are the "Four Golden Signals"? Give a concrete example of each for an e-commerce API.

2. What's the difference between a counter and a gauge metric? Give an example of each.

3. A user reports that their order is "stuck." You have metrics, logs, and traces. In what order do you use them to debug? Why?

4. What is an "error budget"? If your SLO is 99.9% availability and you've had 30 minutes of downtime this month, how much error budget remains?

5. Why is "alert when CPU > 90%" a bad alert? What would be a better alert?

---

## Exercise 2: Metrics Design (25 minutes)

### Scenario: Payment Service

Design the metrics for a payment processing service:

**Business metrics** (what the business cares about):
- Payment success rate
- Revenue processed per minute
- Average payment amount

**Technical metrics** (what engineers care about):
- Request latency (p50, p95, p99)
- Error rate by error type
- Database query latency
- External API (Stripe) latency

For each metric:
1. What type is it? (Counter, Gauge, Histogram)
2. What labels/dimensions would you add?
3. What alert threshold would you set?

---

## Exercise 3: Distributed Trace Analysis (20 minutes)

### Scenario

A user reports that checkout is slow. You pull up the distributed trace:

```
Checkout Request (total: 3200ms)
├── API Gateway (12ms)
├── Order Service (3150ms)
│   ├── Validate cart (5ms)
│   ├── Get user profile (2800ms)  ← !!!
│   │   └── User Service HTTP call (2795ms)
│   │       └── Database query (2790ms)
│   └── Create order record (345ms)
│       └── PostgreSQL INSERT (340ms)
└── Response serialization (38ms)
```

**Analysis**:
1. Where is the bottleneck?
2. The User Service database query takes 2790ms. What are the possible causes?
3. The Order Service PostgreSQL INSERT takes 340ms. Is this normal? What might cause it?
4. What would you investigate first?
5. How would you fix the User Service bottleneck?

---

## Exercise 4: SLO Design (20 minutes)

### Scenario: E-Commerce Platform

Design SLOs for these services:

| Service | User Impact | Your SLO | Rationale |
|---------|-------------|----------|-----------|
| Product search | Users can't find products | ? | ? |
| Checkout | Users can't buy | ? | ? |
| Order history | Users can't see past orders | ? | ? |
| Recommendations | Users see fewer suggestions | ? | ? |
| Admin dashboard | Internal tool | ? | ? |

For each SLO:
1. What's the SLI? (What do you measure?)
2. What's the target? (99%? 99.9%? 99.99%?)
3. What's the error budget per month?
4. What triggers a freeze on new deployments?

---

## Exercise 5: Challenge — Design the Observability Stack (35 minutes)

### Scenario

You're building the observability stack for a system with:
- 20 microservices
- 200 service instances total
- 100,000 requests/second
- 5 engineers on the platform team

**Design**:

1. **Metrics**: Which metrics tool? (Prometheus, Datadog, CloudWatch?) How do you handle 200 instances sending metrics?

2. **Logs**: Which logging tool? How do you handle log volume at 100k RPS? (Estimate: 1KB per request = 100MB/second of logs)

3. **Traces**: Which tracing tool? Do you trace 100% of requests or sample? What sampling rate?

4. **Dashboards**: Design the "golden signals" dashboard for one service. What panels would you include?

5. **On-call**: Design the alerting strategy. How many alerts per day is acceptable? What's your escalation policy?

---

## Hints

**Exercise 3**: A 2790ms database query is almost certainly missing an index or doing a full table scan. Check the query execution plan.

**Exercise 4**: Not all services need 99.99% SLO. Recommendations being down is annoying but not critical. Checkout being down loses revenue.

**Exercise 5, Q3**: Tracing 100% of requests at 100k RPS generates enormous data. 1% sampling is common. But you always want to trace errors (100% of errors).

---

## Self-Assessment Checklist

- [ ] I can explain the three pillars of observability
- [ ] I can design metrics for a given service
- [ ] I can read a distributed trace and identify bottlenecks
- [ ] I understand SLOs and error budgets
- [ ] I can design actionable alerts
- [ ] I know the difference between monitoring and observability
