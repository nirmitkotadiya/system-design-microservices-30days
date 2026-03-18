# Day 19: Observability & Monitoring

## "You Can't Fix What You Can't See"

**Estimated Time**: 90 minutes  
**Difficulty**: Intermediate  
**Prerequisites**: Days 1–18 complete

---

## Learning Objectives
- Explain the three pillars of observability: metrics, logs, and traces
- Design a metrics strategy for a microservices system
- Explain distributed tracing and how it works
- Design alerting rules that are actionable
- Describe the difference between monitoring and observability

---

## Quick Summary

Observability is the ability to understand the internal state of a system from its external outputs. In a distributed system with 20 services, a single user request might touch 10 of them. When something goes wrong, you need to know where and why.

The core insight: **observability is not an afterthought. Design it in from day one. Retrofitting observability into a system is painful.**

---

## Files in This Folder

| File | Description |
|------|-------------|
| `concepts.md` | Metrics, logs, traces, alerting, SLOs |
| `exercises.md` | 5 exercises from metric design to alert tuning |
| `code-examples/` | OpenTelemetry instrumentation examples |

---

## Success Criteria

You've mastered Day 19 when you can:
- [ ] Explain the three pillars of observability
- [ ] Design a metrics strategy for a given system
- [ ] Explain distributed tracing and how spans work
- [ ] Design actionable alerts (not noisy ones)
- [ ] Define SLOs and error budgets

---

## Interview Questions for This Day
- "How would you debug a latency spike in a microservices system?"
- "What's the difference between monitoring and observability?"
- "What are SLOs and error budgets?"
- "How does distributed tracing work?"
