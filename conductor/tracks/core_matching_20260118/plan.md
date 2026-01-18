# Implementation Plan: Core Matching Engine

## Phase 1: Foundation & Models [checkpoint: 213def6]
- [x] Task: Set up the basic FastAPI project structure with Docker Compose. [0b4605e]
- [x] Task: Implement PostgreSQL models for Rider, Driver, and Ride. [d0fca8a]
    - [x] Write unit tests for database models and migrations. [d0fca8a]
    - [x] Implement the database models. [d0fca8a]
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Foundation & Models' (Protocol in workflow.md)

## Phase 2: Location & Proximity [checkpoint: 3f0c431]
- [x] Task: Implement the Location Service using Redis Geospatial commands. [35c2794]
    - [x] Write tests for location updates and proximity searches. [35c2794]
    - [x] Implement the Location Service logic. [35c2794]
- [x] Task: Create the CLI Driver Simulator to push mock location updates. [e2ddbd0]
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Location & Proximity' (Protocol in workflow.md)

## Phase 3: The Matching Loop
- [x] Task: Implement the Ride Request API and status management. [0e83102]
- [x] Task: Develop the asynchronous Matching Service. [26b6296]
    - [x] Implement proximity search for candidate drivers. [26b6296]
    - [x] Implement the sequential notification loop with Redis distributed locking. [26b6296]
    - [x] Add detailed observability logs for each step. [26b6296]
- [ ] Task: Implement the Driver Accept/Deny API.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: The Matching Loop' (Protocol in workflow.md)

## Phase 4: Integration & Verification
- [ ] Task: Create an end-to-end integration test for the matching flow.
- [ ] Task: Verify adherence to educational product guidelines (embedded context, PR deep dives).
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Integration & Verification' (Protocol in workflow.md)
