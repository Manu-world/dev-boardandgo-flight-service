import pytest
from fastapi import status
from unittest.mock import patch

@pytest.mark.asyncio
async def test_get_flight_data_success(async_client, mock_cache, sample_flight_data):
    """Test successful flight data retrieval."""
    with patch('app.services.flight_service.FlightService.fetch_flight_data') as mock_fetch:
        mock_fetch.return_value = sample_flight_data
        
        response = await async_client.get("/api/v1/flights/AA1234")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["flight_number"] == "AA123"
        assert data["airline"] == "American Airlines"
        assert "X-Process-Time" in response.headers

# @pytest.mark.asyncio
# async def test_get_flight_data_not_found(async_client, mock_cache):
#     """Test flight data retrieval when flight is not found."""
#     with patch('app.services.flight_service.FlightService.fetch_flight_data', return_value=None):
#         response = await async_client.get("/api/v1/flights/AA1234")
        
#         # Assert that the status code is 404
#         assert response.status_code == status.HTTP_404_NOT_FOUND
        
#         # Assert that the response contains the expected error detail
#         data = response.json()
#         assert data["detail"] == "Flight not found"

@pytest.mark.asyncio
async def test_get_flight_data_invalid_icao(async_client, mock_cache):
    """Test flight data retrieval with invalid ICAO."""
    response = await async_client.get("/api/v1/flights/invalid!")
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "Invalid ICAO" in data["detail"]

# @pytest.mark.asyncio
# async def test_get_flight_data_rate_limit(async_client, mock_cache):
#     """Test rate limiting."""
#     mock_cache.redis.incr.return_value = 101  # Exceed rate limit
    
#     response = await async_client.get("/api/v1/flights/AA1234")
    
#     assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
#     data = response.json()
#     assert "Rate limit exceeded" in data["detail"]
