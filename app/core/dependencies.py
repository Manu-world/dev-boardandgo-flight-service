from fastapi import Depends, HTTPException, Request, status
from app.services.flight_service import FlightService
from app.core.config import Settings
import logging
from typing import AsyncGenerator
from datetime import datetime

logger = logging.getLogger(__name__)

def get_settings() -> Settings:
    return Settings()

async def get_flight_service(
    settings: Settings = Depends(get_settings)
) -> AsyncGenerator[FlightService, None]:
    service = FlightService(settings)
    try:
        yield service
    finally:
        await service.client.aclose()

async def rate_limit(
    request: Request
) -> None:
    """
    Rate limiting middleware that allows 100 requests per minute per IP.
    
    Args:
        request: FastAPI request object
    
    Raises:
        HTTPException: When rate limit is exceeded
    """
    client_ip = request.client.host
    requests = 0  

    if requests > 100:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again in a minute."
        )