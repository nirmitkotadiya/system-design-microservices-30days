# Day 12: Message Queues & Streaming

## "Decoupling Services with Asynchronous Communication"

**Estimated Time**: 90 minutes  
**Difficulty**: Intermediate-Advanced  
**Prerequisites**: Days 1–11 complete

---

## Learning Objectives
- Explain why message queues are essential for scalable systems
- Compare point-to-point queues vs. pub/sub patterns
- Describe Kafka's architecture and why it's different from traditional queues
- Explain at-least-once, at-most-once, and exactly-once delivery
- Design an event-driven architecture for a given system

---

## Quick Summary

Message queues decouple producers from consumers. Instead of Service A calling Service B directly, A puts a message in a queue and B processes it when ready. This enables async processing, load leveling, and fault isolation.

The core insight: **message queues turn synchronous, brittle dependencies into asynchronous, resilient ones. But they introduce new complexity around ordering, delivery guarantees, and consumer lag.**

---

## Files in This Folder

| File | Description |
|------|-------------|
| `concepts.md` | Queues, pub/sub, Kafka architecture, delivery guarantees |
| `exercises.md` | 5 exercises from queue selection to event-driven design |
| `code-examples/` | Kafka producer/consumer examples |
| `diagrams/` | Queue topology and Kafka architecture diagrams |

---

## Success Criteria

You've mastered Day 12 when you can:
- [ ] Explain the difference between a queue and pub/sub
- [ ] Describe Kafka's log-based architecture
- [ ] Explain at-least-once vs. exactly-once delivery
- [ ] Design an event-driven pipeline for a given system
- [ ] Explain consumer groups and how they enable parallel processing

---

## Interview Questions for This Day
- "Why would you use a message queue instead of direct service calls?"
- "What's the difference between Kafka and RabbitMQ?"
- "What does 'at-least-once delivery' mean? What problems does it cause?"
- "How does Kafka achieve high throughput?"
