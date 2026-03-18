# Day 18: Exercises — Distributed Transactions

---

## Exercise 1: Basic Comprehension (15 minutes)

1. Why can't you use a single ACID transaction across multiple microservices?

2. What is a "compensating transaction"? Give an example for a hotel booking system.

3. What is the "blocking" problem with 2PC? When does it occur?

4. What's the difference between choreography and orchestration in the Saga pattern?

5. What is the Outbox pattern and what problem does it solve?

---

## Exercise 2: Design a Saga (30 minutes)

### Scenario: Hotel Booking

Design a saga for booking a hotel room:

**Services**:
- Booking Service: Creates booking records
- Payment Service: Charges credit card
- Hotel Service: Reserves the room
- Notification Service: Sends confirmation email

**Happy path**: All steps succeed  
**Failure scenarios**:
- Payment fails (card declined)
- Room is no longer available (race condition)
- Notification fails (email service down)

**Design**:
1. List all saga steps in order
2. For each step, define the compensating transaction
3. Draw the event flow for the happy path
4. Draw the event flow for each failure scenario
5. Which step is non-compensatable? How do you handle it?

---

## Exercise 3: Choreography vs. Orchestration (20 minutes)

### Scenario: E-Commerce Order

You're implementing the order placement saga from concepts.md.

**Implement it both ways**:

**Choreography**:
- List all events published and consumed by each service
- Draw the event flow diagram
- Identify: how do you know if the entire saga succeeded?

**Orchestration**:
- Design the orchestrator's state machine
- List all states: PENDING, PAYMENT_PROCESSING, INVENTORY_RESERVING, CONFIRMED, FAILED
- Define transitions between states
- Identify: what happens if the orchestrator crashes mid-saga?

**Which would you choose for this scenario? Why?**

---

## Exercise 4: Idempotency Design (20 minutes)

### Scenario

Your Payment Service processes payments. Due to network issues, the same payment request might be sent multiple times.

**Design idempotent payment processing**:

1. What is an "idempotency key"? How does the client generate it?

2. Design the database schema to support idempotency:
```sql
CREATE TABLE payments (
    -- Your schema here
);
```

3. Write the pseudocode for an idempotent `process_payment` function:
```python
def process_payment(idempotency_key: str, amount: float, card_token: str) -> dict:
    # Your implementation here
    pass
```

4. What's the TTL for idempotency keys? (How long do you store them?)

5. What happens if two requests with the same idempotency key arrive simultaneously?

---

## Exercise 5: Challenge — Design a Travel Booking Saga (35 minutes)

### Scenario

Design a saga for booking a complete trip:
- Flight booking (external API, non-refundable after 24 hours)
- Hotel booking (can be cancelled up to 48 hours before)
- Car rental (can be cancelled anytime)
- Travel insurance (must be purchased with flight)

**Constraints**:
- All four must be booked or none
- Flight is non-refundable after 24 hours
- The entire booking must complete within 5 minutes

**Design challenges**:

1. **Ordering**: In what order should you book each component? Why does order matter?

2. **Non-compensatable steps**: The flight becomes non-refundable after 24 hours. How do you handle this in your saga?

3. **Timeout**: If the saga takes more than 5 minutes, what do you do?

4. **Partial success**: Flight and hotel are booked, but car rental fails. The user says "that's fine, I don't need a car." How do you handle this?

5. **Concurrency**: Two users try to book the last seat on the same flight simultaneously. How does your saga handle this?

---

## Hints

**Exercise 2**: The notification step (sending email) is non-compensatable. Put it last. If it fails, the booking is still valid — just log the failure and retry.

**Exercise 4, Q5**: Use a database unique constraint on the idempotency key. The second request will get a unique constraint violation, which you handle by returning the existing result.

**Exercise 5, Q1**: Book the most constrained resource first (flight). If the flight isn't available, you don't need to book anything else.

---

## Self-Assessment Checklist

- [ ] I can explain why 2PC is problematic in microservices
- [ ] I can design a saga with compensating transactions
- [ ] I understand the difference between choreography and orchestration
- [ ] I can design idempotent operations
- [ ] I understand the Outbox pattern
- [ ] I can identify non-compensatable steps and handle them appropriately
