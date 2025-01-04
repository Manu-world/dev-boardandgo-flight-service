from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Flight Tracking API"
    VERSION: str = "1.0.0"
    
    # External API Configuration
    AVIATION_STACK_API_KEY: str
    AVIATION_API_URL: str = "https://api.aviationstack.com/v1/flights"
    API_TIMEOUT: int = 10
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    class Config:
        env_file = ".env"