# Matching Service Implementation Details

This module implements the core matching logic for the Uber clone. It is designed to be educational, highlighting the use of distributed locking and geospatial indexing.

## Core Decisions

### 1. Sequential Notification Loop
The system iterates through nearby drivers one by one rather than broadcasting to all. This reduces "thundering herd" issues and ensures that the first eligible driver has a fair window to accept.

### 2. Distributed Locking (Redis)
To prevent the same driver from being notified for multiple rides simultaneously, we use Redis-based distributed locks with a 10-second TTL.
- **Why?** In a high-throughput environment, multiple matching instances might find the same nearby driver. The lock ensures atomicity during the "check availability -> notify -> update status" phase.
- **Implementation:** `await self.redis.set(lock_key, "locked", ex=self.lock_ttl, nx=True)`

### 3. Geospatial Indexing
We use Redis `GEOADD` and `GEOSEARCH` for real-time location tracking.
- **Why?** Traditional relational databases are not optimized for 5-second location updates from millions of drivers. Redis's in-memory geospatial commands provide sub-millisecond proximity queries.

## Status Flow
1. **REQUESTED:** Initial state when a rider creates a request.
2. **MATCHED:** Transitioned by the `MatchingService` or `driver/accept` endpoint when a driver is paired with the ride.
3. **IN_PROGRESS:** (Future) When the driver starts the trip.
