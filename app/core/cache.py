from typing import Any, Optional
import aioredis
from app.core.config import Settings
import json

class Cache:
    def __init__(self, settings: Settings):
        self.redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )

    async def get(self, key: str) -> Optional[Any]:
        return await self.redis.get(key)

    async def set(
        self,
        key: str,
        value: Any,
        expire: int = 300
    ) -> bool:
        value = json.dumps(value)
        return await self.redis.set(key, value, ex=expire)

    async def close(self):
        await self.redis.close()