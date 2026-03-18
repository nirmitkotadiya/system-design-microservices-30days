# Day 18: Distributed Transactions — Concepts Deep Dive

## 1. The Problem

In a monolith with one database:
```sql
BEGIN;
  UPDATE accounts SET balance = balance - 100 WHERE id = 'alice';
  UPDATE accounts SET balance = balance + 100 WHERE id = 'bob';
COMMIT;
-- Either both happen or neither happens. ACID guarantees this.
```

In microservices with separate databases:
```
Order Service (PostgreSQL) → Create order
Payment Service (PostgreSQL) → Charge credit card
Inventory Service (MongoDB) → Reserve items

No single transaction spans all three!
If inventory reservation fails after payment succeeds:
  - Payment was charged
  - Order was created
  - But items can't be shipped
  - System is in an inconsistent state
```

---

## 2. Two-Phase Commit (2PC)

2PC is a protocol for achieving atomicity across multiple databases.

### Phase 1: Prepare
```
Coordinator → Order Service: "Prepare to commit"
Coordinator → Payment Service: "Prepare to commit"
Coordinator → Inventory Service: "Prepare to commit"

Each service:
  - Executes the transaction
  - Writes to WAL (but doesn't commit)
  - Responds: "Ready" or "Abort"
```

### Phase 2: Commit or Abort
```
If all responded "Ready":
  Coordinator → All: "Commit"
  All services commit their transactions

If any responded "Abort":
  Coordinator → All: "Abort"
  All services roll back
```

### Why 2PC is Problematic

**Blocking protocol**: If the coordinator crashes after Phase 1, all participants are stuck waiting. They've locked resources but can't commit or abort.

```
Phase 1 complete: All services said "Ready"
Coordinator crashes!

Order Service: "I'm ready to commit, waiting for coordinator..."
Payment Service: "I'm ready to commit, waiting for coordinator..."
Inventory Service: "I'm ready to commit, waiting for coordinator..."

All three are blocked, holding locks, until coordinator recovers.
```

**Performance**: Two round trips to all participants for every transaction.

**Availability**: If any participant is unavailable, the transaction can't proceed.

**Verdict**: 2PC is rarely used in microservices. It's used in some database systems internally.

> **DDIA Reference**: Chapter 9 covers 2PC and its limitations in detail.

---

## 3. The Saga Pattern

A saga is a sequence of local transactions. Each step publishes an event that triggers the next step. If a step fails, compensating transactions undo the previous steps.

### Example: Order Placement Saga

```
Step 1: Order Service → Create order (status: PENDING)
Step 2: Payment Service → Charge credit card
Step 3: Inventory Service → Reserve items
Step 4: Order Service → Update order (status: CONFIRMED)
Step 5: Notification Service → Send confirmation email

If Step 3 fails:
  Compensating Step 2: Payment Service → Refund credit card
  Compensating Step 1: Order Service → Cancel order (status: CANCELLED)
```

### Compensating Transactions

A compensating transaction undoes the effect of a previous transaction.

| Transaction | Compensating Transaction |
|-------------|-------------------------|
| Create order | Cancel order |
| Charge credit card | Refund credit card |
| Reserve inventory | Release inventory reservation |
| Send email | (Can't unsend — log it, maybe send correction) |

**Important**: Not all transactions can be compensated. Sending an email can't be undone. Design your saga to put non-compensatable steps last.

---

## 4. Saga Implementation 1: Choreography

Services communicate via events. No central coordinator.

```
Order Service → publishes: OrderCreated
  ↓
Payment Service → listens: OrderCreated
Payment Service → publishes: PaymentProcessed (or PaymentFailed)
  ↓
Inventory Service → listens: PaymentProcessed
Inventory Service → publishes: InventoryReserved (or InventoryFailed)
  ↓
Order Service → listens: InventoryReserved
Order Service → publishes: OrderConfirmed
```

**Failure handling**:
```
Inventory Service → publishes: InventoryFailed
  ↓
Payment Service → listens: InventoryFailed
Payment Service → refunds payment
Payment Service → publishes: PaymentRefunded
  ↓
Order Service → listens: PaymentRefunded
Order Service → cancels order
```

**Pros**: Loose coupling, no single point of failure  
**Cons**: Hard to track overall saga state, complex failure handling, "choreography hell"

---

## 5. Saga Implementation 2: Orchestration

A central orchestrator tells each service what to do.

```
Order Orchestrator:
  1. Call Order Service: "Create order"
  2. Call Payment Service: "Charge card"
  3. Call Inventory Service: "Reserve items"
  4. Call Order Service: "Confirm order"
  5. Call Notification Service: "Send email"

If step 3 fails:
  Orchestrator calls Payment Service: "Refund payment"
  Orchestrator calls Order Service: "Cancel order"
```

**Pros**: Clear saga state, easy to monitor, simpler failure handling  
**Cons**: Orchestrator is a single point of failure, tight coupling to orchestrator

---

## 6. Choreography vs. Orchestration

| Aspect | Choreography | Orchestration |
|--------|-------------|---------------|
| Coupling | Loose | Tighter (to orchestrator) |
| Visibility | Hard to see overall state | Easy to see overall state |
| Failure handling | Complex | Simpler |
| Single point of failure | No | Yes (orchestrator) |
| Best for | Simple sagas | Complex sagas |

---

## 7. Designing for Minimal Distributed Transactions

The best distributed transaction is the one you don't need.

### Strategy 1: Design Around Bounded Contexts
Keep related data in the same service. If Order and Payment are always transactional together, maybe they should be one service.

### Strategy 2: Accept Eventual Consistency
Not everything needs to be immediately consistent. "The order is confirmed, payment will be processed shortly" is often acceptable.

### Strategy 3: Idempotent Operations
Design all operations to be idempotent. If a step is retried, it should be safe.

```python
def charge_payment(order_id: str, amount: float):
    # Idempotency check
    if payment_exists(order_id):
        return get_payment(order_id)  # Already charged, return existing

    # Process payment
    result = payment_gateway.charge(amount)
    save_payment(order_id, result)
    return result
```

### Strategy 4: Outbox Pattern
Ensure database write and event publish are atomic.

```python
# In a single database transaction:
with db.transaction():
    db.execute("INSERT INTO orders ...")
    db.execute("INSERT INTO outbox (event) VALUES ('OrderCreated')")

# Separate process reads outbox and publishes to Kafka
# Deletes from outbox after successful publish
```

---

## References
- DDIA Chapter 9: Consistency and Consensus (2PC)
- [Saga Pattern by Chris Richardson](https://microservices.io/patterns/data/saga.html)
- [Designing Distributed Systems by Brendan Burns](https://www.oreilly.com/library/view/designing-distributed-systems/9781491983638/)
