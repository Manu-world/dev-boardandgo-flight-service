# Flight Tracking API

A robust, production-ready REST API for tracking flight information using FastAPI. This service provides real-time flight data including status, location, and schedule information.

## Features

- **Real-time Flight Tracking**: Get live flight data including location, speed, and altitude
- **Comprehensive Data**: Access departure/arrival info, delays, gate assignments, and more
- **Production Ready**:
  - Async support for high performance
  - Redis caching for fast responses
  - Rate limiting protection
  - Comprehensive error handling
  - Full monitoring suite

## Tech Stack

- FastAPI for API framework
- Redis for caching and rate limiting
- OpenTelemetry for distributed tracing
- Prometheus for metrics
- Docker & Docker Compose for containerization(being worked on)

## Prerequisites

- Python 3.11+
- Docker and Docker Compose
- An Aviation Stack API key

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/BoardAndGo/boardandgo-flight-service.git
cd boardandgo-flight-service
```

2. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Create a `.env` file:
```bash
mv .env.example .env
```

4. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

5. Start the services:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000/api/docs`

## API Endpoints

### Get Flight Data

```http
GET /api/v1/flights/{flight_icao}
```

Parameters:
- `flight_icao`: ICAO flight identifier (e.g., "AA1234")

Response:
```json
{
  "flight_number": "AA123",
  "airline": "American Airlines",
  "departure_airport": "JFK",
  "arrival_airport": "LAX",
  "flight_status": "ACTIVE",
  "departure_time": "2025-01-04T10:00:00Z",
  "arrival_time": "2025-01-04T13:00:00Z",
  "live": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "altitude": 35000,
    "speed_horizontal": 500
  }
}
```

## Development

1. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
pytest --cov=app tests/
```

3. Start development server:
```bash
uvicorn app.main:app --reload
```

## Monitoring

- Prometheus: `http://localhost:9090`
- Jaeger: `http://localhost:16686`

## Project Structure

```
flight-tracking-api/
├── app/
│   ├── api/
│   │   └── routes/
│   ├── core/
│   │   ├── config.py
│   │   ├── cache.py
│   │   └── monitoring.py
│   ├── services/
│   │   └── flight_service.py
│   └── schemas/
│       └── flight.py
├── tests/
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```


## Testing

Run the test suite:
```bash
pytest
```

With coverage:
```bash
pytest --cov=app tests/
```

## Error Handling

The API uses standard HTTP status codes:
- 200: Success
- 400: Bad Request
- 404: Flight Not Found
- 429: Rate Limit Exceeded
- 503: Service Unavailable

## Rate Limiting

- 100 requests per minute per IP
- Configurable via environment variables
- Uses Redis for tracking

## Caching

- Redis-based caching
- 30-seconds default cache duration
- Cache headers included in responses

## Authors

BoardAndGo Engineers - [contact.boardandgo@gmail.com](mailto:contact.boardandgo@gmail.com)