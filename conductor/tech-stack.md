# Technology Stack

## Backend Services
- **Language:** Python 3.10+
- **Framework:** FastAPI
- **Rationale:** Chosen for its high performance, ease of use, and excellent support for asynchronous programming, which is critical for the real-time nature of ride-sharing. It also provides automatic OpenAPI documentation, supporting our API-first goal.

## Data Persistence
- **Primary Database:** PostgreSQL
- **Rationale:** A robust relational database that ensures strong consistency for Rider, Driver, and Ride entities. Its rich feature set and reliability make it ideal for the core data of our educational MVP.

## Real-Time & Caching
- **Location Tracking:** Redis (using Geospatial indexes/Geohashing)
- **Message Broker:** Redis Pub/Sub
- **Rationale:** Redis provides the extremely low latency required for 5-second location updates from drivers. Its built-in geospatial commands allow for efficient proximity searches. Using Redis Pub/Sub for inter-service communication keeps our stack lean and efficient.

## Infrastructure & Tooling
- **Orchestration:** Docker Compose
- **Rationale:** Enables a consistent development environment where all services (FastAPI, PostgreSQL, Redis) can be spun up with a single command.
- **API Documentation:** Swagger/OpenAPI (built into FastAPI)
