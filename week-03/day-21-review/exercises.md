# Day 21: Mini-Design Challenge — Ride-Sharing Backend

Set a 45-minute timer. Design the backend for a ride-sharing app like Uber.

---

## The Problem

Design the backend for a ride-sharing application.

**Functional Requirements**:
- Riders can request rides
- Drivers can accept/reject ride requests
- Real-time GPS tracking during rides
- Fare calculation and payment processing
- Ratings for both riders and drivers
- Ride history for both riders and drivers

**Non-Functional Requirements**:
- 10 million daily active users
- 1 million rides per day
- Driver location updates every 3 seconds
- Ride matching latency: < 5 seconds
- Availability: 99.99%

---

## Step 1: Service Decomposition (10 minutes)

Identify the microservices. For each service:
- What is its responsibility?
- What database does it use?
- What are its key APIs?

Suggested services to consider:
- User Service
- Driver Service
- Location Service
- Matching Service
- Ride Service
- Payment Service
- Notification Service
- Rating Service

---

## Step 2: Critical Path — Ride Request (10 minutes)

Trace the complete flow when a rider requests a ride:

1. Rider opens app and requests a ride
2. System finds nearby available drivers
3. System sends request to best driver
4. Driver accepts
5. Driver navigates to rider
6. Ride starts
7. Ride ends
8. Payment processed
9. Both parties rate each other

For each step:
- Which service handles it?
- Sync or async?
- What data is stored?

---

## Step 3: Location Service Design (10 minutes)

The location service is the most technically interesting:
- 1 million active drivers updating location every 3 seconds
- = 333,000 location updates/second
- Riders need to see nearby drivers in real-time

**Design**:
1. What database stores driver locations? (Hint: Redis has geospatial support)
2. How do you find drivers within 5km of a rider?
3. How do you push driver location updates to the rider's app?
4. How do you handle a driver going offline?

---

## Step 4: Matching Algorithm (5 minutes)

When a rider requests a ride:
1. Find all available drivers within 5km
2. Rank them by: distance, rating, acceptance rate
3. Send request to the best driver
4. If driver doesn't respond in 10 seconds, try next driver

**Design**:
- How do you prevent two riders from being matched to the same driver?
- What happens if no drivers are available?

---

## Step 5: Observability (5 minutes)

Design the key metrics and alerts:
1. What are the four golden signals for the Matching Service?
2. What alert would you set for "no drivers available in a city"?
3. How would you debug a spike in ride matching latency?

---

## Step 6: Tradeoffs (5 minutes)

Discuss:
1. You chose Redis for location storage. What are the tradeoffs?
2. You chose async for payment processing. What are the risks?
3. What's the biggest scalability challenge in your design?

---

## Reference Solution Outline

**Services**: User, Driver, Location, Matching, Ride, Payment, Notification, Rating

**Location Service**:
- Redis with geospatial commands (`GEOADD`, `GEORADIUS`)
- WebSocket for real-time updates to rider
- 333k writes/second → Redis Cluster

**Matching**:
- Distributed lock to prevent double-booking
- Timeout-based fallback to next driver

**Payment**:
- Async via Kafka (rider doesn't wait for payment)
- Saga pattern: charge → update ride status → notify

**Key insight**: Location updates are the hardest scaling challenge. 333k writes/second requires Redis Cluster with careful sharding.

---

## Week 3 Final Checklist

- [ ] Microservices: can decompose a system with appropriate boundaries
- [ ] API Design: can design RESTful APIs with pagination and versioning
- [ ] Service Discovery: can explain client-side vs. server-side discovery
- [ ] Circuit Breakers: can design fallback behavior
- [ ] Distributed Transactions: can design a saga
- [ ] Observability: can design metrics, logs, traces strategy
- [ ] CDN: can design caching strategy with appropriate TTLs
