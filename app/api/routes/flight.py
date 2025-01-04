import json
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from typing import Annotated
from app.services.flight_service import FlightService
from app.schemas.flight import FlightDataResponseSchema
from app.schemas.error import ErrorResponseSchema
from app.core.dependencies import get_flight_service, get_cache, rate_limit
from app.core.logging import logger
from app.core.cache import Cache
from opentelemetry import trace
from prometheus_client import Counter, Histogram
import time

# Metrics
FLIGHT_REQUESTS = Counter(
    'flight_api_requests_total',
    'Total number of requests to the flight API',
    ['status', 'endpoint']
)
RESPONSE_TIME = Histogram(
    'flight_api_response_time_seconds',
    'Response time in seconds for flight API requests',
    ['endpoint']
)

router = APIRouter(prefix="/v1/flights", tags=["flights"])
tracer = trace.get_tracer(__name__)

@router.get(
    "/{flight_icao}",
    response_model=FlightDataResponseSchema,
    responses={
        200: {"model": FlightDataResponseSchema},
        404: {"model": ErrorResponseSchema},
        429: {"model": ErrorResponseSchema},
        503: {"model": ErrorResponseSchema}
    }
)
async def get_flight_data(
    flight_icao: str,
    response: Response,
    service: Annotated[FlightService, Depends(get_flight_service)],
    cache: Annotated[Cache, Depends(get_cache)],
    rate_limiter: Annotated[None, Depends(rate_limit)]
):
    """
    Fetch and format flight data for a specific flight.
    
    Parameters:
        flight_icao: ICAO flight identifier
        
    Returns:
        FlightDataResponseSchema: Formatted flight data
        
    Raises:
        HTTPException: For various error conditions with appropriate status codes
    """
    start_time = time.time()
    
    try:
        with tracer.start_as_current_span("get_flight_data") as span:
            span.set_attribute("flight.icao", flight_icao)
            
            # Check cache first
            cache_key = f"flight:{flight_icao}"
            cached_data = await cache.get(cache_key)
            if cached_data:
                FLIGHT_REQUESTS.labels(status="cache_hit", endpoint="get_flight_data").inc()
                response.headers["X-Cache"] = "HIT"
                return JSONResponse(content=json.loads(cached_data))

            # Validate ICAO format
            if not service.validate_flight_icao(flight_icao):
                FLIGHT_REQUESTS.labels(status="invalid_format", endpoint="get_flight_data").inc()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid ICAO flight identifier format"
                )

            raw_data = await service.fetch_flight_data(flight_icao)
            if raw_data is None:
                FLIGHT_REQUESTS.labels(status="not_found", endpoint="get_flight_data").inc()
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"detail": "Flight not found"}
                )

            formatted_data = await service.format_flight_data(raw_data)
            
            # Cache the result
            await cache.set(cache_key, json.dumps(formatted_data.dict()), expire=30)
            response.headers["X-Cache"] = "MISS"
            
            FLIGHT_REQUESTS.labels(status="success", endpoint="get_flight_data").inc()
            return formatted_data

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in get_flight_data")
        FLIGHT_REQUESTS.labels(status="error", endpoint="get_flight_data").inc()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable"
        )
    finally:
        RESPONSE_TIME.labels(endpoint="get_flight_data").observe(time.time() - start_time)