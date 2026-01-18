# Uber Clone - Educational Ride-Sharing System

An asynchronous, real-time ride-sharing system built with FastAPI, PostgreSQL, and Redis. This project is designed as an educational resource to explore complex system design patterns like geospatial indexing, distributed locking, and microservices architecture.

## 🚀 Tech Stack

- **Backend:** Python 3.10+, FastAPI
- **Database:** PostgreSQL (Persistence), Redis (Geospatial tracking & Locking)
- **Infrastructure:** Docker Compose
- **Package Management:** `uv`
- **Architecture:** API-First, Modular Microservices

## ✨ Key Features

- **Real-Time Matching Engine:** Efficiently pairs available drivers with riders using a sequential notification loop.
- **Geospatial Tracking:** High-frequency location updates and proximity search using Redis Geospatial indexes.
- **Distributed Locking:** Prevents "double-matching" drivers or rides in high-concurrency scenarios.
- **Educational Documentation:** Embedded context and deep dives into architectural decisions.
- **Driver Simulator:** A CLI tool to simulate multiple active drivers moving in real-time.

## 🛠️ Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
- [uv](https://github.com/astral-sh/uv) (Python package manager)

### Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Start the infrastructure (PostgreSQL & Redis):
   ```bash
   docker-compose up -d
   ```
4. Run migrations:
   ```bash
   $env:DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/uber"
   uv run alembic upgrade head
   ```

### Running the Application

1. Start the API server:
   ```bash
   uv run uvicorn app.main:app --reload
   ```
2. Access the interactive API documentation (Swagger) at: `http://localhost:8000/docs`

### Running the Driver Simulator

To simulate active drivers moving on the map:
```bash
uv run python -m app.scripts.driver_simulator --driver-ids "1,2,3" --interval 2
```

## 🧪 Testing

Run the full test suite with coverage:
```bash
uv run python -m pytest --cov=app --cov-report=term-missing
```

## 📂 Project Structure

This project follows the **Conductor** spec-driven development framework.
- `app/`: Core application logic (routers, models, services, schemas).
- `conductor/`: Project context, workflow definitions, and track archives.
- `migrations/`: Alembic database migration scripts.
- `tests/`: Unit and integration tests.

## 📖 Educational Context

For a deep dive into the matching logic and architectural decisions, see [app/services/README.md](./app/services/README.md).
