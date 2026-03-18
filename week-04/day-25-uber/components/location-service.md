# Uber Component: Location Service

## Overview

The location service handles the most write-intensive part of Uber's architecture: processing 500,000 driver location updates per second.

## Data Model

```python
# Driver location update (sent every 4 seconds)
{
    "driver_id": "d_123456",
    "lat": 37.7749,
    "lng": -122.4194,
    "heading": 270,        # degrees (0=North, 90=East, etc.)
    "speed": 35,           # mph
    "timestamp": 1704067200,
    "status": "available"  # available | on_trip | offline
}
```

## Storage Architecture

```
Driver app → Location Service → Redis Cluster (hot data)
                              → Kafka → S3 (cold storage / analytics)

Redis data model:
  # Current location (TTL: 30 seconds)
  SET driver:d_123456:location '{"lat":37.77,"lng":-122.41,...}' EX 30
  
  # Geospatial index for "find nearby drivers"
  GEOADD drivers:available -122.4194 37.7749 d_123456
  
  # Remove when driver goes offline or on trip
  ZREM drivers:available d_123456
```

## Geospatial Query

```python
# Find available drivers within 2km of a rider
def find_nearby_drivers(rider_lat, rider_lng, radius_km=2, limit=10):
    # Redis GEORADIUS: O(N+log(M)) where N=results, M=total drivers
    drivers = redis.georadius(
        "drivers:available",
        rider_lng, rider_lat,
        radius_km, "km",
        withcoord=True,
        withdist=True,
        count=limit,
        sort="ASC"  # closest first
    )
    return drivers

# Result: [("d_123456", 0.3, (37.77, -122.41)), ...]
```

## S2 Geometry for Advanced Queries

For more complex queries (e.g., "find drivers in this polygon"), Uber uses Google's S2 library:

```python
import s2sphere

def get_s2_cell_id(lat, lng, level=14):
    """Level 14 ≈ 0.2 km² (city block size)"""
    latlng = s2sphere.LatLng.from_degrees(lat, lng)
    cell = s2sphere.CellId.from_lat_lng(latlng).parent(level)
    return cell.id()

def find_nearby_cells(lat, lng, radius_km, level=14):
    """Get all S2 cells covering a circular area."""
    center = s2sphere.LatLng.from_degrees(lat, lng)
    cap = s2sphere.Cap.from_axis_angle(
        center.to_point(),
        s2sphere.Angle.from_degrees(radius_km / 111.0)  # ~111km per degree
    )
    coverer = s2sphere.RegionCoverer()
    coverer.min_level = level
    coverer.max_level = level
    return coverer.get_covering(cap)
```

## Handling 500K Updates/Second

```
Single Redis instance: ~100K ops/second
Need: 500K updates/second

Solution: Redis Cluster with 10 shards
  Shard by driver_id: driver_id % 10 → shard number
  Each shard handles ~50K updates/second ✓

But: "find nearby drivers" query spans all shards
  → Scatter-gather: query all 10 shards, merge results
  → Acceptable because it's a read (fast) and results are small
```

## Interview Talking Points

- Explain why you can't use a traditional database for location updates
- Discuss the tradeoff between Redis GEO and S2 geometry
- Explain how you shard the location data
- Discuss TTL for driver locations (30 seconds = driver considered offline)
- Mention Kafka for durability and analytics (Redis is ephemeral)
