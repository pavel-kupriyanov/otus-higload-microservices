import os
import json
from copy import deepcopy
from typing import List

from pydantic import (
    BaseModel,
    BaseSettings as PydanticSettings,
    SecretStr
)


class UvicornSettings(BaseModel):
    ASGI_PATH: str = 'social_network:application'
    HOST: str = '0.0.0.0'
    PORT: int = int(os.getenv('PORT') or 8000)
    WORKERS = 1


class DatabaseSettings(BaseModel):
    DB: str = 'mysql'
    HOST: str = 'localhost'
    PORT: int = 3306
    USER: str = 'root'
    PASSWORD: SecretStr
    NAME: str
    MAX_CONNECTIONS = 1


class MasterSlaveDatabaseSettings(BaseModel):
    MASTER: DatabaseSettings
    SLAVES: List[DatabaseSettings] = []


class KafkaSSLSettings(BaseModel):
    CA: SecretStr = ''
    CERT: SecretStr = ''
    KEY: SecretStr = ''


class KafkaSettings(BaseModel):
    HOST: str = 'localhost'
    PORT: int = 9092
    USE_SSL: bool = False
    SSL: KafkaSSLSettings = KafkaSSLSettings()


class RedisSettings(BaseModel):
    HOST: str = 'localhost'
    PORT: int = 6379
    USER: str = ''
    PASSWORD: SecretStr = ''


class NewsCacheSettings(BaseModel):
    MAX_FOLLOWERS_PER_USERS: int = 100
    MAX_FEED_SIZE: int = 1000
    WARMUP_CACHE_PERIOD: int = 1 * 24 * 60 * 60


class RabbitMQSettings(BaseModel):
    HOST: str = 'localhost'
    PORT: int = 5672
    USERNAME: str = 'rabbit'
    PASSWORD: SecretStr = 'rabbit'
    EXCHANGE: str = 'feed'
    PATH: str = ''


class BaseSettings(PydanticSettings):
    DEBUG: bool
    UVICORN: UvicornSettings
    DATABASE: MasterSlaveDatabaseSettings
    KAFKA: KafkaSettings
    REDIS: RedisSettings
    RABBIT: RabbitMQSettings
    NEWS_CACHE: NewsCacheSettings
    TOKEN_EXPIRATION_TIME: int
    BASE_PAGE_LIMIT: int

    @classmethod
    def from_json(cls, path):
        with open(path) as fp:
            merged_settings = deep_merge(cls().dict(), json.load(fp))
        return cls.parse_obj(merged_settings)

    def __hash__(self):
        # For lru cache
        return hash(self.json())


def deep_merge(first: dict, second: dict) -> dict:
    res = deepcopy(first)
    for key, value in second.items():
        if key in res and isinstance(res[key], dict) \
                and isinstance(value, dict):
            res[key] = deep_merge(res[key], value)
        else:
            res[key] = value

    return res
