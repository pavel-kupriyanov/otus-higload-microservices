import os
import json
from typing import List
from copy import deepcopy

from pydantic import (
    BaseModel,
    SecretStr,
    BaseSettings as PydanticSettings
)


class UvicornSettings(BaseModel):
    ASGI_PATH: str = 'app:app'
    HOST: str = '0.0.0.0'
    PORT: int = 9900
    WORKERS = 1


class DatabaseSettings(BaseModel):
    DB: str = 'mysql'
    HOST: str = 'localhost'
    PORT: int = 3306
    USER: str = 'root'
    PASSWORD: SecretStr = ''
    NAME: str = ''
    MAX_CONNECTIONS = 1


class MasterSlaveDatabaseSettings(BaseModel):
    MASTER: DatabaseSettings = DatabaseSettings()
    SLAVES: List[DatabaseSettings] = []


class BaseSettings(PydanticSettings):

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


ROOT_DIR = os.path.dirname((os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_DIR, '_settings.json')


class Settings(BaseSettings):
    DEBUG: bool = True
    TOKEN_EXPIRATION_TIME: int = 60 * 60 * 24 * 7
    DATABASE: MasterSlaveDatabaseSettings = MasterSlaveDatabaseSettings()
    UVICORN: UvicornSettings = UvicornSettings()


settings = Settings.from_json(CONFIG_PATH)
