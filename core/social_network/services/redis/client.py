from json import loads, dumps
from typing import Any
from aioredis import Redis, create_redis_pool

from social_network.settings import RedisSettings

from ..base import BaseService


class CommandMixin:
    redis: Redis

    async def hget(self, key: str, field: str) -> Any:
        raw = await self.redis.hget(key, field)
        if isinstance(raw, bytes):
            raw = loads(raw)
        return raw

    async def hset(self, key: str, field: str, value: Any):
        return await self.redis.hset(key, field, dumps(value))


class RedisService(BaseService, CommandMixin):
    redis: Redis

    def __init__(self, conf: RedisSettings):
        self.conf = conf

    async def start(self):
        self.redis = await create_redis_pool(
            f'redis://@{self.conf.HOST}:{self.conf.PORT}',
            password=None,
        )

    async def close(self):
        self.redis.close()
        await self.redis.wait_closed()

    def __getattr__(self, item: str):
        return getattr(self.redis, item)
