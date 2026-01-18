# Specification: Core Matching Engine

## Overview
This track focuses on the foundational components of the Uber-like ride-sharing system. The goal is to implement the end-to-end flow of requesting a ride, tracking driver locations in real-time, and matching a rider with an available driver using an asynchronous matching loop.

## Functional Requirements
- **Rider/Driver Management:** Persistence of Rider and Driver entities in PostgreSQL.
- **Real-Time Location Tracking:** Fast updates and proximity queries using Redis Geospatial indexes.
- **Ride Request Flow:** Riders can initiate a ride request which enters a pending state.
- **Asynchronous Matching Engine:** A service that identifies nearby drivers and sequentially notifies them until one accepts.
- **Distributed Locking:** Ensure a driver is only matched to one ride at a time using Redis-based locks.
- **Status Updates:** Real-time updates of Ride, Rider, and Driver statuses throughout the matching process.

## Technical Requirements
- **Language/Framework:** Python 3.10+ with FastAPI.
- **Persistence:** PostgreSQL for entities, Redis for location and locking.
- **Concurrency:** Asynchronous matching logic using Python's `asyncio` and Redis Pub/Sub for notifications.
- **Observability:** Structured logging of every step in the matching loop for educational purposes.

## Out of Scope
- Fare estimation (will be added in a future track).
- Complex payment processing.
- Multi-region support.
- Production-grade authentication.
