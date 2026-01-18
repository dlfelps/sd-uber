import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.models import RideStatus, User, UserRole, Ride
from app.db.base import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

@pytest.fixture
def override_db(db_session):
    async def _override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_create_ride_request(db_session: AsyncSession, override_db):
    # Setup: Create a rider
    rider = User(email="rider@test.com", hashed_password="pw", role=UserRole.RIDER)
    db_session.add(rider)
    await db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "rider_id": rider.id,
            "source_lat": 37.7749,
            "source_long": -122.4194,
            "dest_lat": 37.7849,
            "dest_long": -122.4094
        }
        response = await ac.post("/ride/request", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "requested"
    assert data["rider_id"] == rider.id
    
    ride_id = data["id"]
    
    # Test getting ride status
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/ride/{ride_id}")
    
    assert response.status_code == 200
    assert response.json()["status"] == "requested"

@pytest.mark.asyncio
async def test_get_ride_not_found(db_session: AsyncSession, override_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/ride/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Ride not found"