import pytest
from app.core.cache import Cache
import json
@pytest.mark.asyncio
async def test_cache_get(mock_redis, test_settings):
    """Test cache get operation."""
    cache = Cache(test_settings)
    cache.redis = mock_redis
    
    mock_redis.get.return_value = '{"key": "value"}'
    result = await cache.get("test_key")
    
    assert result == '{"key": "value"}'
    mock_redis.get.assert_called_once_with("test_key")

@pytest.mark.asyncio
async def test_cache_set(mock_redis, test_settings):
    """Test cache set operation."""
    cache = Cache(test_settings)
    cache.redis = mock_redis
    
    await cache.set("test_key", "test_value", 300)
    
    mock_redis.set.assert_called_once_with(
        "test_key",
        json.dumps("test_value"),
        ex=300
        )