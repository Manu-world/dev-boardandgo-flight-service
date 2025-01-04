from fastapi import Depends, HTTPException, Request, status
from app.services.flight_service import FlightService
from app.core.config import Settings
from app.core.cache import Cache
import time
from redis.exceptions import RedisError
import logging
from typing import AsyncGenerator
from typing import Annotated
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
async def get_cache(
    settings: Settings = Depends(get_settings)
) -> AsyncGenerator[Cache, None]:
    cache = Cache(settings)
    try:
        yield cache
    finally:
        await cache.close()


async def rate_limit(
    request: Request,
    cache: Annotated[Cache, Depends(get_cache)]
) -> None:
    """
    Rate limiting middleware that allows 100 requests per minute per IP.
    
    Args:
        request: FastAPI request object
        cache: Redis cache instance
    
    Raises:
        HTTPException: When rate limit is exceeded
    """
    client_ip = request.client.host
    current_minute = datetime.utcnow().strftime("%Y-%m-%d-%H-%M")
    key = f"rate_limit:{client_ip}:{current_minute}"
    
    try:
        requests = await cache.redis.incr(key)
        await cache.redis.expire(key, 60)  # Expire after 1 minute
        
        if requests > 100:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again in a minute."
            )
    except AttributeError:
        # If redis connection fails, we'll skip rate limiting rather than break the app
        pass