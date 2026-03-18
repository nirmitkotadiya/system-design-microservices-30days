# Uber: Scale Considerations

## The Numbers

Uber operates at a scale that makes most engineering problems interesting:

- 130+ million monthly active users
- 5+ million drivers
- 25+ million trips per day
- Operations in 70+ countries, 10,000+ cities
- Location updates: ~500,000 per second (drivers pinging every 4 seconds)
- Peak: millions of concurrent active sessions

---

## The Core Scaling Challenge: Real-Time Location

The hardest part of Uber's architecture isn't the ride matching — it's handling 500,000 location updates per second from drivers, while simultaneously serving millions of "find nearby drivers" queries.

### Location Storage: Why Traditional Databases Fail

```
Naive approach:
  UPDATE drivers SET lat=37.7, lng=-122.4, updated_at=NOW() WHERE id=123

At 500K updates/second:
  → 500K writes/second to a single table
  → Even with sharding, each shard gets ~50K writes/second
  → Index maintenance on lat/lng columns is expensive
  → Geospatial queries (find drivers within 1km) are slow on B-trees
```

### The Solution: Geospatial Indexing

**S2 Geometry Library** (what Uber actually uses):
- Divides Earth into a hierarchy of cells
- Each cell has a unique 64-bit integer ID
- Nearby cells have nearby IDs (locality-preserving)

```
Level 12 cell ≈ 3.3 km²  (city neighborhood)
Level 14 cell ≈ 0.2 km²  (city block)
Level 16 cell ≈ 0.01 km² (building)

Driver at (37.7749, -122.4194) → S2 cell ID: 3318846965553561600

Find drivers within 1km:
  1. Get S2 cells covering the 1km radius
  2. Query: WHERE s2_cell_id IN (cell1, cell2, ..., cellN)
  3. Integer range queries → fast B-tree lookups
```

**Alternative: Geohash** (simpler, slightly less accurate):
```
(37.7749, -122.4194) → geohash: "9q8yy"
Nearby drivers: WHERE geohash LIKE "9q8y%"
```

### In-Memory Location Store

For 500K updates/second, even a fast database is too slow. Uber uses an in-memory store:

```
Architecture:
  Driver app → Location Service → Redis Cluster
                                → Kafka (for persistence/analytics)

Redis data model:
  Key: "driver:{id}:location"
  Value: {lat, lng, heading, speed, timestamp}
  TTL: 30 seconds (driver considered offline if no update)

Geospatial index:
  GEOADD drivers:active {lng} {lat} {driver_id}
  GEORADIUS drivers:active {lng} {lat} 1 km ASC COUNT 10
```

---

## Scaling the Dispatch System

### The Matching Problem

When a rider requests a ride:
1. Find all available drivers within X km
2. Rank them by ETA (not just distance)
3. Offer the ride to the best driver
4. If declined, offer to next driver
5. Complete within 30 seconds or rider cancels

At peak: millions of concurrent matching operations.

### Supply/Demand Forecasting

Uber predicts where drivers will be needed before riders request:

```
Inputs:
  - Historical trip data (same time last week/year)
  - Current driver locations
  - Current ride requests
  - Events (concerts, sports games)
  - Weather

Output:
  - Surge pricing zones (increase supply, decrease demand)
  - Driver incentive zones ("drive to downtown, earn bonus")
```

This runs as a streaming ML pipeline on Kafka + Flink.

---

## Multi-Region Architecture

Uber operates globally with strict latency requirements (matching must complete in < 5 seconds).

```
Global Architecture:
  Region: US-West (San Francisco HQ)
  Region: US-East
  Region: EU-West (Amsterdam)
  Region: AP-Southeast (Singapore)
  Region: AP-South (Mumbai)

Each region:
  - Fully independent (can operate if other regions fail)
  - Handles local trips
  - Syncs non-real-time data globally (user profiles, payment history)

Cross-region:
  - User profile: replicated globally (read anywhere)
  - Active trips: owned by one region (consistency)
  - Driver location: local only (no need to share globally)
```

### Data Residency

Many countries require user data to stay within their borders (GDPR in EU, data localization laws in India, China, etc.). Uber's multi-region architecture handles this by keeping data in the appropriate region.

---

## Handling 100x Growth

### Phase 1: 1x (Current baseline)
- Single region
- PostgreSQL for trips, MySQL for users
- Redis for driver locations
- Monolithic dispatch service

### Phase 2: 10x Growth
- Add read replicas to databases
- Shard trips table by city_id
- Add Kafka for async processing
- Separate dispatch into its own service
- Add CDN for static assets

### Phase 3: 100x Growth
- Multi-region deployment
- Custom geospatial store (replace Redis GEO with S2-based system)
- ML-based demand forecasting
- Microservices for each domain (pricing, matching, routing, payments)
- Event sourcing for trip state machine
- Dedicated analytics pipeline (Kafka → Spark → Data Warehouse)

---

## The Trip State Machine

A trip goes through many states. At scale, managing these transitions reliably is critical.

```
States:
  REQUESTED → DRIVER_ASSIGNED → DRIVER_EN_ROUTE → 
  DRIVER_ARRIVED → TRIP_STARTED → TRIP_COMPLETED → PAYMENT_PROCESSED

Each transition:
  - Must be atomic (can't be in two states at once)
  - Must be durable (survives crashes)
  - Must be auditable (for disputes)

Implementation:
  - Event sourcing: store every state transition as an immutable event
  - Current state = replay of all events
  - Kafka for event streaming
  - PostgreSQL for event store (append-only)
```

---

## Surge Pricing at Scale

Surge pricing is a real-time supply/demand balancing mechanism. Computing it at scale:

```
Every 5 minutes, for every city zone:
  supply = count of available drivers in zone
  demand = count of ride requests in zone (last 5 min)
  
  if demand/supply > threshold:
    surge_multiplier = f(demand/supply)
  else:
    surge_multiplier = 1.0

Challenges:
  - 10,000+ cities × hundreds of zones each = millions of computations
  - Must be consistent (all users in a zone see same surge)
  - Must update quickly (surge can change in minutes)

Solution:
  - Streaming computation (Kafka + Flink)
  - Results cached in Redis with 5-minute TTL
  - Surge multiplier stored per S2 cell
```

---

## Key Lessons

1. **Location data is special** — use geospatial indexes (S2, geohash), not lat/lng columns
2. **In-memory for hot data** — driver locations must be in RAM, not on disk
3. **Event sourcing for state machines** — trips have complex state, events are the source of truth
4. **Predict demand** — proactive supply positioning beats reactive matching
5. **Multi-region from day one** — retrofitting is painful; design for it early
6. **Separate read and write paths** — location writes and "find nearby" reads have very different patterns
