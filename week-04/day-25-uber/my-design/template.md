# My Uber Design — Learner Template

Practice designing Uber's ride-sharing system from scratch. The key challenge here is real-time location tracking and matching at massive scale.

---

## Step 1: Clarify Requirements (5 minutes)

**Functional Requirements**:
- [ ] Riders can request a ride from location A to B
- [ ] System matches rider with nearby available driver
- [ ] Driver can accept/decline ride requests
- [ ] Real-time location tracking during trip
- [ ] Fare calculation and payment
- [ ] Other: _______________

**Non-Functional Requirements**:
- Matching latency: _______________
- Location update frequency: _______________
- Availability: _______________
- Consistency: _______________
- Scale: ___ drivers, ___ riders, ___ trips/day

**Out of Scope**:
- _______________

---

## Step 2: Capacity Estimation

```
Drivers (active at peak): ___
Location updates per driver: every ___ seconds
Total location updates/second: ___

Riders (active at peak): ___
Ride requests per second: ___

Storage per location update: ___ bytes
Total location storage per day: ___
```

---

## Step 3: High-Level Design

```
[Draw your architecture here]

Key components to include:
- Rider app / Driver app
- API Gateway
- Location Service
- Matching/Dispatch Service
- Trip Service
- Notification Service
- Payment Service
- Database(s)
- Cache
```

---

## Step 4: Deep Dive — Location Tracking

This is the hardest part. How do you handle 500K location updates/second?

**Your approach**:
- Storage technology: _______________
- Data model: _______________
- How do you find nearby drivers efficiently?
- What geospatial indexing do you use?

**Geospatial indexing options**:

| Approach | How it works | Pros | Cons |
|----------|-------------|------|------|
| Lat/Lng columns | | | |
| Geohash | | | |
| S2 Geometry | | | |
| Redis GEO | | | |

**Your choice and why**: _______________

---

## Step 5: Deep Dive — Matching Algorithm

When a rider requests a ride, how do you find the best driver?

**Your algorithm**:
```
1. _______________
2. _______________
3. _______________
```

**How do you rank drivers?**
- Just by distance?
- By ETA (estimated time of arrival)?
- By driver rating?
- By acceptance rate?

**What happens if the best driver declines?**
_______________

**How do you handle surge pricing?**
_______________

---

## Step 6: Deep Dive — Trip State Machine

A trip goes through multiple states. Design the state machine:

```
States: [list them]
Transitions: [list them]

REQUESTED → ___ → ___ → ___ → COMPLETED
```

**How do you ensure state transitions are atomic?**
_______________

**How do you handle a driver going offline mid-trip?**
_______________

---

## Step 7: Deep Dive — Real-Time Updates

How does the rider see the driver moving on the map in real-time?

**Options**:
- Polling (client asks server every N seconds)
- Long polling
- WebSockets
- Server-Sent Events

**Your choice**: _______________
**Why**: _______________

---

## Step 8: Bottlenecks and Solutions

| Bottleneck | At what scale? | Solution |
|------------|---------------|----------|
| | | |
| | | |
| | | |

---

## Self-Assessment

Compare your design to `../architecture-diagram.md` and `../scale-considerations.md`.

- [ ] Did I address the location update volume (500K/sec)?
- [ ] Did I use geospatial indexing?
- [ ] Did I design the matching algorithm?
- [ ] Did I handle the trip state machine?
- [ ] Did I address real-time updates to the rider?
- [ ] Did I consider multi-region deployment?

**What I got right**: _______________
**What I missed**: _______________
**What I'd do differently**: _______________
