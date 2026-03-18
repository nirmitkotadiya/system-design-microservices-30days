# Day 12: Message Queues & Streaming — Concepts Deep Dive

## 1. Why Message Queues?

### The Problem with Synchronous Communication

```
Without queue (synchronous):
  Order Service → Payment Service → Inventory Service → Email Service
  
  If Email Service is slow: Order Service waits
  If Email Service is down: Order fails
  If traffic spikes: All services overwhelmed simultaneously
```

### The Solution: Async with Queues

```
With queue (asynchronous):
  Order Service → Queue → Payment Service (processes when ready)
                        → Inventory Service (processes when ready)
                        → Email Service (processes when ready)
  
  Order Service returns immediately after writing to queue
  Each service processes at its own pace
  If Email Service is down: messages wait in queue, processed when it recovers
```

**Benefits**:
1. **Decoupling**: Services don't need to know about each other
2. **Load leveling**: Queue absorbs traffic spikes
3. **Fault isolation**: One service failing doesn't cascade
4. **Async processing**: Slow operations don't block the user

---

## 2. Queue vs. Pub/Sub

### Point-to-Point Queue
One producer, one consumer. Each message is processed by exactly one consumer.

```
Producer → [Queue] → Consumer A
                   (Consumer B never sees this message)
```

**Use case**: Task queues (image processing, email sending, background jobs)

### Pub/Sub (Publish-Subscribe)
One producer, many consumers. Each subscriber gets a copy of every message.

```
Producer → [Topic] → Consumer A (gets all messages)
                   → Consumer B (gets all messages)
                   → Consumer C (gets all messages)
```

**Use case**: Event broadcasting (user signed up → send welcome email AND update analytics AND notify sales)

### Comparison

| Feature | Queue | Pub/Sub |
|---------|-------|---------|
| Consumers | One | Many |
| Message delivery | Once | Once per subscriber |
| Use case | Task distribution | Event broadcasting |
| Examples | SQS, RabbitMQ | SNS, Kafka topics |

---

## 3. Traditional Message Queues: RabbitMQ

RabbitMQ is a traditional message broker using AMQP protocol.

```
Producer → Exchange → Queue 1 → Consumer A
                    → Queue 2 → Consumer B
```

**Key concepts**:
- **Exchange**: Routes messages to queues based on routing rules
- **Queue**: Stores messages until consumed
- **Binding**: Rules connecting exchanges to queues
- **Acknowledgment**: Consumer tells broker "I processed this message"

**Message lifecycle**:
```
1. Producer sends message to exchange
2. Exchange routes to queue(s)
3. Consumer receives message
4. Consumer processes message
5. Consumer sends ACK to broker
6. Broker deletes message from queue

If consumer crashes before ACK:
  Broker re-delivers message to another consumer
```

**Strengths**: Complex routing, message priorities, dead letter queues  
**Weaknesses**: Messages deleted after consumption (no replay), limited throughput

---

## 4. Log-Based Message Streaming: Apache Kafka

Kafka is fundamentally different from traditional queues. It's a **distributed log**.

### The Core Concept: The Log

```
Kafka Topic (like a file you can only append to):

Offset: 0    1    2    3    4    5    6    7
        [msg][msg][msg][msg][msg][msg][msg][msg]
                              ↑
                    Consumer A is here (offset 4)
                    Consumer B is here (offset 6)
```

**Key difference from RabbitMQ**: Messages are NOT deleted after consumption. They're retained for a configurable period (default: 7 days). Multiple consumers can read the same messages independently.

### Kafka Architecture

```
                    ┌─────────────────────────────────┐
                    │           Kafka Cluster          │
                    │                                  │
Producer ──────────▶│  Topic: "orders"                 │
                    │  ┌──────────┐ ┌──────────┐       │
                    │  │Partition0│ │Partition1│       │
                    │  │[0][1][2] │ │[0][1][2] │       │
                    │  └──────────┘ └──────────┘       │
                    └──────────────────────────────────┘
                              │           │
                    ┌─────────▼─┐   ┌─────▼──────┐
                    │Consumer A │   │ Consumer B  │
                    │(Group 1)  │   │ (Group 1)   │
                    └───────────┘   └─────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Consumer C       │
                    │  (Group 2)        │
                    │  (reads all msgs) │
                    └───────────────────┘
```

### Partitions

Topics are split into partitions for parallelism:
- Each partition is an ordered, immutable log
- Messages within a partition are ordered
- Messages across partitions are NOT ordered
- Each partition is replicated across brokers for fault tolerance

```python
# Producer: choose partition by key
producer.send(
    topic="orders",
    key=b"user_123",  # Same user always goes to same partition
    value=b'{"order_id": 456}'
)
# hash("user_123") % num_partitions = partition 2
```

### Consumer Groups

Consumer groups enable parallel processing:

```
Topic: "orders" (3 partitions)
Consumer Group: "order-processor"

Partition 0 → Consumer A (exclusively)
Partition 1 → Consumer B (exclusively)
Partition 2 → Consumer C (exclusively)

Each partition is consumed by exactly one consumer in the group.
Adding more consumers than partitions doesn't help (some will be idle).
```

Multiple consumer groups can read the same topic independently:
```
Consumer Group "order-processor" → processes orders
Consumer Group "analytics" → tracks order metrics
Consumer Group "fraud-detection" → checks for fraud

All three groups read the same messages independently.
```

### Why Kafka is Fast

1. **Sequential disk writes**: Appending to a log is sequential I/O (fast)
2. **Zero-copy**: Data goes from disk to network without copying to user space
3. **Batching**: Messages are batched before sending
4. **Compression**: Messages are compressed in batches

Kafka can handle millions of messages per second on commodity hardware.

---

## 5. Delivery Guarantees

### At-Most-Once
Message is delivered zero or one times. May be lost.

```
Producer sends message → Broker receives → Consumer processes
If consumer crashes: message is lost (not redelivered)
```

**Use case**: Metrics, logs where some loss is acceptable

### At-Least-Once
Message is delivered one or more times. May be duplicated.

```
Producer sends message → Broker receives → Consumer processes
If consumer crashes before ACK: message is redelivered
Consumer may process the same message twice!
```

**Use case**: Most applications. Requires idempotent consumers.

### Exactly-Once
Message is delivered exactly once. No loss, no duplicates.

```
Requires coordination between producer, broker, and consumer.
Kafka supports this with transactions (since 0.11).
```

**Use case**: Financial transactions, inventory updates

### Making At-Least-Once Safe: Idempotency

```python
def process_order(order_id: str, amount: float):
    # Check if already processed (idempotency key)
    if db.exists(f"processed_order:{order_id}"):
        return  # Already processed, skip

    # Process the order
    db.execute("UPDATE accounts SET balance = balance - ? WHERE ...", amount)

    # Mark as processed
    db.set(f"processed_order:{order_id}", "1", ex=86400)
```

---

## 6. Kafka vs. RabbitMQ: When to Use Each

| Feature | Kafka | RabbitMQ |
|---------|-------|----------|
| Message retention | Days/weeks (replay possible) | Until consumed |
| Throughput | Millions/second | Thousands/second |
| Ordering | Per partition | Per queue |
| Consumer model | Pull (consumer controls pace) | Push (broker pushes) |
| Routing | Simple (topic/partition) | Complex (exchanges, bindings) |
| Use case | Event streaming, log aggregation | Task queues, RPC |
| Replay | Yes | No |

**Choose Kafka when**:
- High throughput (millions of events/second)
- Multiple consumers need the same events
- You need to replay events (audit, reprocessing)
- Event sourcing architecture

**Choose RabbitMQ when**:
- Complex routing rules
- Task queues with priorities
- Lower throughput requirements
- You need per-message TTL or dead letter queues

---

## 7. Common Patterns

### Event Sourcing
Store all changes as events, not just current state:
```
Instead of: UPDATE users SET name = 'Alice'
Store: {event: "UserNameChanged", user_id: 123, new_name: "Alice", timestamp: ...}

Benefits: Full audit trail, replay to any point in time, event-driven architecture
```

### CQRS (Command Query Responsibility Segregation)
Separate read and write models:
```
Write path: Command → Event → Kafka → Write DB
Read path:  Query → Read DB (optimized for reads, updated from Kafka)
```

### Outbox Pattern
Ensure database writes and message publishing are atomic:
```python
# In a transaction:
db.execute("INSERT INTO orders ...")
db.execute("INSERT INTO outbox (event_type, payload) VALUES ('OrderCreated', ...)")
# Commit transaction

# Separate process reads outbox and publishes to Kafka
# Deletes from outbox after successful publish
```

---

## References
- DDIA Chapter 11: Stream Processing
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [The Log: What every software engineer should know](https://engineering.linkedin.com/distributed-systems/log-what-every-software-engineer-should-know-about-real-time-datas-unifying) — Jay Kreps (Kafka creator)
