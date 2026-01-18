# Implementation Plan: Core Matching Engine

## Phase 1: Foundation & Models
- [ ] Task: Set up the basic FastAPI project structure with Docker Compose.
- [ ] Task: Implement PostgreSQL models for Rider, Driver, and Ride.
    - [ ] Write unit tests for database models and migrations.
    - [ ] Implement the database models.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Foundation & Models' (Protocol in workflow.md)

## Phase 2: Location & Proximity
- [ ] Task: Implement the Location Service using Redis Geospatial commands.
    - [ ] Write tests for location updates and proximity searches.
    - [ ] Implement the Location Service logic.
- [ ] Task: Create the CLI Driver Simulator to push mock location updates.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Location & Proximity' (Protocol in workflow.md)

## Phase 3: The Matching Loop
- [ ] Task: Implement the Ride Request API and status management.
- [ ] Task: Develop the asynchronous Matching Service.
    - [ ] Implement proximity search for candidate drivers.
    - [ ] Implement the sequential notification loop with Redis distributed locking.
    - [ ] Add detailed observability logs for each step.
- [ ] Task: Implement the Driver Accept/Deny API.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: The Matching Loop' (Protocol in workflow.md)

## Phase 4: Integration & Verification
- [ ] Task: Create an end-to-end integration test for the matching flow.
- [ ] Task: Verify adherence to educational product guidelines (embedded context, PR deep dives).
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Integration & Verification' (Protocol in workflow.md)
