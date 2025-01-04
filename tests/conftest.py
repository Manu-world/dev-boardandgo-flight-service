import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app
from app.core.config import Settings
from app.services.flight_service import FlightService
from app.core.cache import Cache

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_settings():
    """Fixture for test settings."""
    return Settings(
        AVIATION_STACK_API_KEY="test_key",
        REDIS_URL="redis://localhost:6379/0",
        RATE_LIMIT_REQUESTS=100,
        RATE_LIMIT_WINDOW=60
    )

@pytest.fixture
async def mock_redis():
    """Fixture for mocked Redis client."""
    mock = AsyncMock()
    mock.get.return_value = None
    mock.set.return_value = True
    mock.incr.return_value = 1
    return mock

@pytest.fixture
async def mock_cache(mock_redis):
    """Fixture for mocked Cache instance."""
    cache = AsyncMock(spec=Cache)
    cache.redis = mock_redis
    return cache

@pytest.fixture
def test_client():
    """Fixture for FastAPI test client."""
    return TestClient(app)

@pytest.fixture
async def async_client():
    """Fixture for async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
        
# Sample test data
@pytest.fixture
def sample_flight_data():
    """Fixture for sample flight data."""
    return {
        "flight": {"number": "AA123"},
        "airline": {"name": "American Airlines"},
        "departure": {
            "airport": "JFK",
            "scheduled": "2025-01-04T10:00:00Z",
            "gate": "A1",
            "terminal": "T1",
            "delay": 15
        },
        "arrival": {
            "airport": "LAX",
            "scheduled": "2025-01-04T13:00:00Z"
        },
        "flight_status": "active",
        "live": {
            "updated": "2025-01-04T11:00:00Z",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "altitude": 35000,
            "direction": 270,
            "speed_horizontal": 500,
            "speed_vertical": 0
        }
    }
