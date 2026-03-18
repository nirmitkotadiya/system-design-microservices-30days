# Uber Architecture Diagram

## High-Level Architecture

```
Rider App / Driver App
         │
    ┌────▼────────────────────────────────────────────┐
    │                  API Gateway                     │
    │  (Auth, Rate Limiting, WebSocket upgrade)        │
    └──┬──────┬──────┬──────┬──────┬──────────────────┘
       │      │      │      │      │
    ┌──▼──┐ ┌─▼──┐ ┌─▼──┐ ┌─▼──┐ ┌─▼──────────┐
    │Rider│ │Drvr│ │Loc │ │Ride│ │  Payment   │
    │ Svc │ │ Svc│ │ Svc│ │ Svc│ │  Service   │
    └──┬──┘ └─┬──┘ └─┬──┘ └─┬──┘ └─┬──────────┘
       │      │      │      │      │
       │      │      │      │      │
    ┌──▼──────────────────────────────────────────┐
    │                  Kafka                       │
    │  Topics: location_updates, ride_events       │
    └──┬──────────────────────────────────────────┘
       │
    ┌──▼──────────────────────────────────────────┐
    │           Matching Service                   │
    │  (Finds best driver for each ride request)   │
    └──┬──────────────────────────────────────────┘
       │
    ┌──▼──────────────────────────────────────────┐
    │           Location Store (Redis)             │
    │  Geospatial index of all active drivers      │
    └─────────────────────────────────────────────┘
```

## Location Service Deep Dive

```
Driver App → Location Update (every 4 seconds)
                │
         ┌──────▼──────────────────────────────────┐
         │         Location Service                 │
         │                                          │
         │  1. Validate location (reasonable speed?)│
         │  2. Update Redis geospatial index        │
         │  3. Publish to Kafka (for analytics)     │
         │  4. Push to rider's app (if in ride)     │
         └──────────────────────────────────────────┘
                │
         ┌──────▼──────────────────────────────────┐
         │         Redis Geospatial                 │
         │                                          │
         │  GEOADD drivers:available                │
         │    longitude latitude driver_id          │
         │                                          │
         │  GEORADIUS drivers:available             │
         │    longitude latitude 5 km               │
         │    → [driver_1, driver_2, driver_3]      │
         └──────────────────────────────────────────┘
```

## Ride Request Flow

```
1. Rider requests ride
   Rider App → Ride Service → Create ride (status: SEARCHING)
                            → Publish RideRequested to Kafka

2. Matching Service picks up event
   Matching Service → Query Redis: "Drivers within 5km of pickup"
                   → Score drivers (distance, rating, acceptance rate)
                   → Send request to best driver

3. Driver accepts
   Driver App → Ride Service → Update ride (status: DRIVER_ASSIGNED)
                             → Notify rider via WebSocket

4. During ride
   Driver App → Location Service → Update Redis
                                 → Push to rider via WebSocket

5. Ride completes
   Driver App → Ride Service → Update ride (status: COMPLETED)
                             → Publish RideCompleted to Kafka
                             → Payment Service processes payment
                             → Rating Service requests ratings
```

## Surge Pricing Architecture

```
Every 60 seconds:
  Surge Service reads:
    - Active ride requests in each geographic cell (demand)
    - Available drivers in each geographic cell (supply)
  
  Calculates surge multiplier:
    surge = max(1.0, demand / supply × base_multiplier)
  
  Stores in Redis:
    SETEX surge:cell:{cell_id} 60 {multiplier}
  
  Pushes to driver/rider apps via WebSocket
```
