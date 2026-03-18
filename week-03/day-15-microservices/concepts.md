# Day 15: Microservices Architecture — Concepts Deep Dive

## 1. The Monolith

A monolith is a single deployable unit containing all application functionality.

```
┌─────────────────────────────────────────────────────┐
│                    MONOLITH                          │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  User    │  │  Order   │  │    Payment       │  │
│  │  Module  │  │  Module  │  │    Module        │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ Inventory│  │  Email   │  │   Analytics      │  │
│  │  Module  │  │  Module  │  │   Module         │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
│                                                      │
│              Single Database                         │
└─────────────────────────────────────────────────────┘
```

### Monolith Advantages
- **Simple to develop**: No network calls between modules
- **Simple to test**: Everything in one process
- **Simple to deploy**: One artifact to deploy
- **Simple to debug**: Single process, single log stream
- **Low latency**: In-process calls, no network overhead

### Monolith Disadvantages
- **Scaling**: Must scale the entire application, even if only one module needs more resources
- **Deployment**: Changing one module requires deploying everything
- **Technology lock-in**: All modules must use the same language/framework
- **Team coordination**: Large teams stepping on each other's code
- **Reliability**: One bug can crash the entire application

---

## 2. Microservices

Microservices decompose the application into small, independently deployable services.

```
┌──────────┐  ┌──────────┐  ┌──────────────────┐
│  User    │  │  Order   │  │    Payment       │
│ Service  │  │ Service  │  │    Service       │
│  DB      │  │  DB      │  │    DB            │
└──────────┘  └──────────┘  └──────────────────┘
     │              │                │
     └──────────────┴────────────────┘
                    │
              API Gateway / Message Bus
```

### Microservices Advantages
- **Independent deployment**: Deploy one service without touching others
- **Independent scaling**: Scale only the services that need it
- **Technology flexibility**: Each service can use different languages/databases
- **Team autonomy**: Each team owns their service end-to-end
- **Fault isolation**: One service failing doesn't crash everything

### Microservices Disadvantages (The Part Nobody Warns You About)
- **Distributed systems complexity**: Network calls fail, latency varies
- **Data consistency**: No ACID transactions across services
- **Testing complexity**: Integration testing is hard
- **Operational overhead**: 10 services = 10 deployment pipelines, 10 monitoring dashboards
- **Network latency**: In-process calls become network calls
- **Service discovery**: How does Service A find Service B?
- **Debugging**: A request spans 5 services — where did it fail?

> **The Rule of Thumb**: If you have fewer than 50 engineers, a monolith is probably better. Microservices are an organizational solution to a team coordination problem.

---

## 3. Domain-Driven Design (DDD)

DDD provides a framework for decomposing systems into services.

### Bounded Context

A bounded context is a boundary within which a particular domain model applies. Different contexts can use the same word to mean different things.

```
"Customer" in different contexts:

Sales Context:
  Customer = {name, contact_info, sales_rep, deal_stage}

Support Context:
  Customer = {name, contact_info, ticket_history, satisfaction_score}

Billing Context:
  Customer = {name, billing_address, payment_methods, invoices}
```

Each bounded context becomes a candidate for a microservice.

### Identifying Bounded Contexts

Ask these questions:
1. What are the core business domains? (Sales, Support, Billing, Shipping)
2. Where do the same words mean different things?
3. Where do teams have different vocabularies?
4. What can change independently?

### Example: E-Commerce Decomposition

```
E-Commerce Monolith → Microservices:

User Management → User Service
  - Registration, authentication, profiles

Product Catalog → Catalog Service
  - Product listings, search, categories

Inventory → Inventory Service
  - Stock levels, reservations, warehouse management

Orders → Order Service
  - Order creation, status tracking, history

Payments → Payment Service
  - Payment processing, refunds, billing

Notifications → Notification Service
  - Email, SMS, push notifications

Recommendations → Recommendation Service
  - "Customers also bought", personalization
```

---

## 4. Service Communication Patterns

### Synchronous (Request-Response)
```
Order Service → HTTP/gRPC → Payment Service → Response
```
- Simple to understand
- Tight coupling (Order Service waits for Payment Service)
- If Payment Service is slow, Order Service is slow

### Asynchronous (Event-Driven)
```
Order Service → Kafka → Payment Service (processes when ready)
```
- Loose coupling
- Better fault isolation
- More complex to reason about

### When to Use Each

| Pattern | Use When |
|---------|----------|
| Synchronous | Need immediate response (user is waiting) |
| Asynchronous | Background processing, notifications, analytics |
| Synchronous | Simple request-response with clear SLA |
| Asynchronous | Long-running operations, fan-out to many services |

---

## 5. The Strangler Fig Pattern

How to migrate from monolith to microservices without a big-bang rewrite.

**Named after**: The strangler fig tree, which grows around a host tree and eventually replaces it.

```
Phase 1: Monolith handles everything
  Client → Monolith → Database

Phase 2: Extract one service, route some traffic
  Client → API Gateway → Monolith (most requests)
                       → New Service (extracted functionality)

Phase 3: Extract more services
  Client → API Gateway → Service A
                       → Service B
                       → Monolith (remaining functionality)

Phase 4: Monolith is gone
  Client → API Gateway → Service A
                       → Service B
                       → Service C
```

### Steps for Each Extraction
1. Identify a bounded context to extract
2. Build the new service alongside the monolith
3. Route traffic to the new service (feature flag or API gateway rule)
4. Verify the new service works correctly
5. Remove the functionality from the monolith

---

## 6. Data Management in Microservices

### Database per Service
Each service owns its data. No shared databases.

```
Order Service → Orders DB (PostgreSQL)
Payment Service → Payments DB (PostgreSQL)
Catalog Service → Catalog DB (MongoDB)
```

**Why**: Shared databases create tight coupling. If the schema changes, all services break.

### The Distributed Transaction Problem

```
Place Order:
1. Order Service: Create order record
2. Payment Service: Charge credit card
3. Inventory Service: Reserve items

What if step 3 fails after step 2 succeeds?
  - Payment was charged but order can't be fulfilled
  - Need to refund the payment
  - This is a distributed transaction
```

**Solution**: Saga Pattern (Day 18)

---

## 7. When NOT to Use Microservices

- **Small team** (< 10 engineers): Operational overhead outweighs benefits
- **Early stage startup**: Requirements change too fast; microservices make pivoting hard
- **Simple domain**: If your domain doesn't have clear bounded contexts, microservices add complexity without benefit
- **Tight latency requirements**: Network calls add latency; in-process calls are faster

> **Martin Fowler's advice**: "Don't start with microservices. Start with a monolith, keep it modular, and break it apart when you have a good reason to."

---

## References
- [Building Microservices by Sam Newman](https://samnewman.io/books/building_microservices/)
- [Martin Fowler on Microservices](https://martinfowler.com/articles/microservices.html)
- [Domain-Driven Design by Eric Evans](https://www.domainlanguage.com/ddd/)
- DDIA Chapter 12: The Future of Data Systems
