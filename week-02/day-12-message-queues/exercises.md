# Day 12: Exercises — Message Queues & Streaming

---

## Exercise 1: Basic Comprehension (15 minutes)

1. An e-commerce site processes orders synchronously: Order → Payment → Inventory → Email. The email service goes down. What happens to orders? How would a message queue fix this?

2. What's the difference between a queue and pub/sub? Give a real-world example of each.

3. Kafka retains messages for 7 days. RabbitMQ deletes messages after consumption. What does this enable in Kafka that's impossible in RabbitMQ?

4. You have a Kafka topic with 4 partitions and a consumer group with 6 consumers. How many consumers are actively processing messages? Why?

5. What is an idempotent consumer? Why is it necessary for at-least-once delivery?

---

## Exercise 2: Delivery Guarantee Analysis (20 minutes)

For each scenario, choose the appropriate delivery guarantee and justify:

| Scenario | At-Most-Once | At-Least-Once | Exactly-Once | Why |
|----------|-------------|---------------|--------------|-----|
| Page view tracking | ? | ? | ? | ? |
| Bank transfer events | ? | ? | ? | ? |
| Email notifications | ? | ? | ? | ? |
| Inventory deduction | ? | ? | ? | ? |
| Log aggregation | ? | ? | ? | ? |
| Payment processing | ? | ? | ? | ? |

For each "at-least-once" choice, describe how you'd make the consumer idempotent.

---

## Exercise 3: Design an Event-Driven Order System (30 minutes)

### Scenario

Design the event-driven architecture for an e-commerce order system:

**Services**:
- Order Service: Creates orders
- Payment Service: Processes payments
- Inventory Service: Reserves/deducts inventory
- Notification Service: Sends emails/SMS
- Analytics Service: Tracks order metrics
- Fraud Detection Service: Checks for suspicious orders

**Requirements**:
- Order placement must be fast (< 200ms response to user)
- Payment must be processed before inventory is deducted
- User must receive confirmation email
- Analytics must track all orders
- Fraud detection must run before payment

**Design**:
1. What events/topics do you create?
2. What's the event flow for a successful order?
3. What's the event flow for a failed payment?
4. Which services use pub/sub? Which use point-to-point queues?
5. How do you handle the case where inventory deduction fails after payment succeeds?

---

## Exercise 4: Kafka Partition Strategy (20 minutes)

### Scenario

You're designing a Kafka topic for a ride-sharing app:
- Events: `RideRequested`, `DriverAssigned`, `RideStarted`, `RideCompleted`, `PaymentProcessed`
- 10 million rides per day
- Events for the same ride must be processed in order
- You have 10 consumer instances

**Questions**:
1. How many partitions would you create? Why?
2. What partition key would you use? Why?
3. A consumer instance crashes. What happens to the partitions it was consuming?
4. You need to add 5 more consumer instances. What do you need to change?
5. You need to replay all events from 3 days ago (a bug was found). How does Kafka enable this?

---

## Exercise 5: Challenge — Design a Real-Time Analytics Pipeline (35 minutes)

### Scenario

Design a real-time analytics pipeline for a social media platform:
- 1 million events per second (likes, comments, shares, views)
- Real-time dashboard showing trending posts (updated every 30 seconds)
- Historical analytics (daily/weekly/monthly reports)
- Anomaly detection (viral content detection within 5 minutes)

**Design the pipeline**:

1. **Ingestion**: How do you get 1M events/second into the system?

2. **Stream processing**: How do you compute trending posts in real-time? (Hint: windowed aggregations)

3. **Storage**: Where do you store raw events? Aggregated metrics? For how long?

4. **Serving**: How do you serve the real-time dashboard? The historical reports?

5. **Fault tolerance**: If a stream processor crashes, how do you ensure no events are lost or double-counted?

Draw the full pipeline architecture.

---

## Hints

**Exercise 3**: Think about the Saga pattern for distributed transactions. When payment succeeds but inventory fails, you need a compensating transaction.

**Exercise 4**: Partition key should ensure all events for the same ride go to the same partition (for ordering). `ride_id` is the natural choice.

**Exercise 5**: Look up "tumbling windows" and "sliding windows" for stream processing. Apache Flink or Kafka Streams can compute these.

---

## Self-Assessment Checklist

- [ ] I can explain why message queues improve system resilience
- [ ] I understand the difference between queue and pub/sub patterns
- [ ] I can describe Kafka's log-based architecture
- [ ] I understand at-least-once delivery and how to make consumers idempotent
- [ ] I can design an event-driven architecture for a given system
- [ ] I know when to choose Kafka vs. RabbitMQ
