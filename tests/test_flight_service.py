from unittest.mock import AsyncMock
import pytest
from fastapi import HTTPException
import httpx
from app.core.config import Settings
from app.services.flight_service import FlightService
from unittest.mock import patch
from fastapi import status


@pytest.mark.asyncio
async def test_validate_flight_icao():
    """Test ICAO flight identifier validation."""
    service = FlightService(Settings())
    
    assert service.validate_flight_icao("AA1234") == True
    assert service.validate_flight_icao("AAA123") == True
    assert service.validate_flight_icao("AA123456") == True
    assert service.validate_flight_icao("aa1234") == True  # Should handle lowercase
    
    assert service.validate_flight_icao("AA12") == False  # Too short
    assert service.validate_flight_icao("AA123456789") == False  # Too long
    assert service.validate_flight_icao("AA12!@") == False  # Invalid characters
    assert service.validate_flight_icao("") == False  # Empty string

@pytest.mark.asyncio
async def test_fetch_flight_data_success(test_settings, sample_flight_data):
    """Test successful flight data fetching."""
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [sample_flight_data]}
        mock_get.return_value = mock_response
        
        service = FlightService(test_settings)
        result = await service.fetch_flight_data("AA1234")
        
        assert result == sample_flight_data
        mock_get.assert_called_once_with(
            test_settings.AVIATION_API_URL,
            params={
                "access_key": test_settings.AVIATION_STACK_API_KEY,
                "flight_icao": "AA1234",
            }
        )

# @pytest.mark.asyncio
# async def test_fetch_flight_data_not_found(test_settings):
#     """Test flight data fetching when flight is not found."""
#     with patch('httpx.AsyncClient.get') as mock_get:
#         mock_response = AsyncMock()
#         mock_response.status_code = 200
#         mock_response.json.return_value = {"data": []}
#         mock_get.return_value = mock_response
        
#         service = FlightService(test_settings)
#         result = await service.fetch_flight_data("AA1234")
        
#         assert result is None

@pytest.mark.asyncio
async def test_fetch_flight_data_rate_limit(test_settings):
    """Test flight data fetching when rate limited."""
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.side_effect = httpx.HTTPStatusError(
            message="Rate limit exceeded",
            request=AsyncMock(),
            response=AsyncMock(status_code=429)
        )
        
        service = FlightService(test_settings)
        with pytest.raises(HTTPException) as exc_info:
            await service.fetch_flight_data("AA1234")
        
        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_format_flight_data(test_settings, sample_flight_data):
    """Test flight data formatting."""
    service = FlightService(test_settings)
    result = await service.format_flight_data(sample_flight_data)
    
    assert result.flight_number == "AA123"
    assert result.airline == "American Airlines"
    assert result.departure_airport == "JFK"
    assert result.arrival_airport == "LAX"
    assert result.flight_status == "ACTIVE"
    assert result.gate == "A1"
    assert result.terminal == "T1"
    assert result.delay == 15
    
    # Check live data
    assert result.live.latitude == 40.7128
    assert result.live.longitude == -74.0060
    assert result.live.altitude == 35000
    assert result.live.direction == 270
    assert result.live.speed_horizontal == 500
    assert result.live.speed_vertical == 0

# @pytest.mark.asyncio
# async def test_get_flight_data_not_found(async_client, mock_cache):
#     """Test flight data retrieval when flight is not found."""
#     with patch('app.services.flight_service.FlightService.fetch_flight_data') as mock_fetch:
#         mock_fetch.return_value = None  # Simulate not found
        
#         response = await async_client.get("/api/v1/flights/AA1234")
        
#         # Check if the response status code is 404
#         assert response.status_code == status.HTTP_404_NOT_FOUND  # Ensure your endpoint handles this correctly
#         data = response.json()
#         assert "Flight not found" in data["detail"]  # Ensure this matches your error response structure
