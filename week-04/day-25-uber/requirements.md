# Uber System Design — Requirements

## Functional Requirements

### Rider Features
1. Request a ride (specify pickup and destination)
2. See nearby available drivers in real-time
3. Track driver location during ride
4. Pay for ride (credit card, cash, Uber Cash)
5. Rate driver after ride
6. View ride history

### Driver Features
1. Go online/offline
2. Accept/reject ride requests
3. Navigate to rider and destination
4. View earnings
5. Rate rider after ride

### System Features
1. Match riders to nearest available driver
2. Calculate fare (base + distance + time + surge)
3. Surge pricing based on supply/demand
4. ETA calculation

## Scale Requirements (Uber's actual scale)
- 130 million monthly active users
- 25 million rides per day
- 5 million active drivers
- Driver location updates: every 4 seconds
- Peak: 100,000 concurrent rides

## Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Ride matching latency | < 5 seconds |
| Driver location update | Every 4 seconds |
| Surge pricing update | Every 1 minute |
| Availability | 99.99% |
| Location accuracy | < 10 meters |

## Key Technical Challenges
1. Real-time geospatial queries (find drivers within 5km)
2. High-frequency location updates (5M drivers × every 4s = 1.25M updates/second)
3. Matching algorithm (minimize wait time, maximize driver utilization)
4. Surge pricing (real-time supply/demand calculation)
