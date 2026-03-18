# Uber Design — Tradeoffs

## Location Storage: Redis vs. PostGIS vs. Custom

### Option A: Redis Geospatial (Chosen)
```
GEOADD drivers:available -73.9857 40.7484 "driver_123"
GEORADIUS drivers:available -73.9857 40.7484 5 km
```

**Pros**: Sub-millisecond queries, simple API, handles 1.25M updates/second  
**Cons**: In-memory only (expensive at scale), limited query complexity

### Option B: PostGIS (PostgreSQL extension)
```sql
SELECT driver_id FROM drivers
WHERE ST_DWithin(location, ST_MakePoint(-73.9857, 40.7484)::geography, 5000)
AND status = 'available'
ORDER BY location <-> ST_MakePoint(-73.9857, 40.7484)::geography
LIMIT 10;
```

**Pros**: Rich geospatial queries, persistent storage, SQL  
**Cons**: Slower than Redis for simple radius queries, harder to scale writes

### Option C: Custom Geospatial Index (S2 Geometry)
Google's S2 library divides the Earth into cells at multiple levels.

**Pros**: Very efficient for complex geospatial queries  
**Cons**: Complex to implement and maintain

**Decision**: Redis for real-time driver locations (speed), PostgreSQL/PostGIS for historical ride data (complex queries).

---

## Matching Algorithm: Nearest vs. Optimal

### Nearest Driver
Simply pick the closest available driver.

**Pros**: Simple, fast, minimizes rider wait time  
**Cons**: Doesn't consider driver's current direction, acceptance rate, or overall system efficiency

### Optimal Matching (Uber's actual approach)
Batch ride requests and driver availability, solve as an assignment problem.

```
Every 5 seconds:
  Collect all pending ride requests
  Collect all available drivers
  Solve: minimize total wait time across all matches
  Assign drivers to riders
```

**Pros**: Better overall system efficiency  
**Cons**: Adds up to 5 seconds of latency, complex algorithm

**Decision**: Uber uses a hybrid — quick initial match with nearest driver, then optimization in background.

---

## Real-Time Communication: WebSocket vs. Polling

### WebSocket (Chosen)
Persistent bidirectional connection. Server pushes updates to client.

**Pros**: Real-time updates, low latency, efficient  
**Cons**: Stateful connections (harder to scale), connection management complexity

### HTTP Polling
Client polls server every N seconds.

**Pros**: Simple, stateless  
**Cons**: High latency (up to N seconds), wasteful (most polls return no new data)

**Decision**: WebSocket for real-time location updates. HTTP for non-real-time operations.

---

## Consistency: Ride State Machine

Ride state must be consistent. Two drivers can't be assigned to the same ride.

```
States: SEARCHING → DRIVER_ASSIGNED → IN_PROGRESS → COMPLETED
                 ↘ CANCELLED

Consistency requirement: DRIVER_ASSIGNED must be atomic
  (Only one driver can be assigned)

Solution: Optimistic locking
  UPDATE rides SET driver_id = ?, status = 'DRIVER_ASSIGNED', version = version + 1
  WHERE id = ? AND status = 'SEARCHING' AND version = ?
  
  If 0 rows updated: another driver was assigned first → retry
```
