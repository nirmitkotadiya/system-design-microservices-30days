# Day 15: Exercises — Microservices Architecture

---

## Exercise 1: Basic Comprehension (15 minutes)

1. A startup has 5 engineers and is building a new product. Should they use microservices or a monolith? Justify your answer.

2. What is a "bounded context"? Give an example of the same concept meaning different things in two different bounded contexts.

3. What is the "strangler fig pattern"? Why is it safer than a big-bang rewrite?

4. A microservices system has 20 services. Service A calls Service B, which calls Service C, which calls Service D. Service D is slow. What happens to Service A's response time?

5. Why do microservices require "database per service"? What problem does a shared database cause?

---

## Exercise 2: Domain Decomposition (30 minutes)

### Scenario: Ride-Sharing App (like Uber)

Decompose this monolith into microservices:

**Current monolith functionality**:
- User registration and authentication
- Driver registration and background checks
- Ride request and matching
- Real-time GPS tracking
- Pricing and surge calculation
- Payment processing
- Rating and reviews
- Notifications (push, SMS, email)
- Analytics and reporting
- Customer support ticketing

**Your task**:
1. Identify the bounded contexts (group related functionality)
2. Define the service boundaries (what goes in each service)
3. For each service, identify:
   - Its primary responsibility
   - Its data store (what database type?)
   - Its communication pattern (sync or async?)
4. Draw the service dependency graph
5. Identify which services are on the critical path for a ride request

---

## Exercise 3: Service Communication Design (25 minutes)

### Scenario: Order Placement Flow

When a user places an order on an e-commerce site, these things must happen:
1. Validate the order (items exist, user is valid)
2. Reserve inventory
3. Process payment
4. Create order record
5. Send confirmation email
6. Update analytics
7. Notify warehouse

**Design the communication**:
1. Which steps must be synchronous (user is waiting)?
2. Which steps can be asynchronous?
3. Draw the event flow for a successful order
4. Draw the event flow for a failed payment
5. What events do you publish? What's the event schema?

---

## Exercise 4: Strangler Fig Migration (20 minutes)

### Scenario

You have a monolith e-commerce application. You want to extract the "Recommendations" feature into a microservice.

The recommendations feature:
- Runs ML models to generate product recommendations
- Is called on every product page view
- Currently takes 500ms (slowing down the whole page)
- Has its own database tables

**Design the migration**:
1. What's the first step? (Don't say "rewrite everything")
2. How do you route traffic to the new service without breaking the monolith?
3. How do you handle the database migration?
4. How do you verify the new service is working correctly before fully cutting over?
5. What's your rollback plan?

---

## Exercise 5: Challenge — Design the Service Mesh for a Social Network (35 minutes)

### Scenario

Design the microservices architecture for a social network with:
- 500 million users
- Services: User, Post, Feed, Follow, Notification, Search, Media, Analytics

**Design challenges**:

1. **Service dependencies**: Draw the dependency graph. Which services are most critical?

2. **The feed problem**: When a user opens the app, they need posts from all followed users. This requires data from User, Post, and Follow services. How do you aggregate this efficiently?

3. **Cascading failures**: If the Post service goes down, what happens to the Feed service? How do you prevent cascading failures?

4. **Data consistency**: User A follows User B. User B posts something. User A's feed should show it. But the Follow service and Post service have separate databases. How do you ensure consistency?

5. **Team structure**: You have 100 engineers. How do you organize teams around these services? (Hint: Conway's Law)

---

## Hints

**Exercise 2**: Think about what changes independently. Pricing logic changes frequently (surge pricing). GPS tracking has different scaling needs than user registration.

**Exercise 3**: The user is waiting for steps 1-4. Steps 5-7 can be async. But what if step 3 (payment) fails after step 2 (inventory reserved)?

**Exercise 5, Q3**: Circuit breakers prevent cascading failures. If Post service is down, Feed service should return cached data or a degraded response, not fail completely.

---

## Self-Assessment Checklist

- [ ] I can explain when to use microservices vs. monolith
- [ ] I can identify bounded contexts in a given domain
- [ ] I can design service communication (sync vs. async)
- [ ] I understand the strangler fig migration pattern
- [ ] I can identify cascading failure risks in a microservices architecture
- [ ] I understand why database-per-service is important
