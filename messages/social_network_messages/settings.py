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
    ASGI_PATH: str = 'web:app'
    HOST: str = '0.0.0.0'
    PORT: int = 10000
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


class BaseSettings(PydanticSettings):
    DEBUG: bool
    UVICORN: UvicornSettings
    DATABASE: MasterSlaveDatabaseSettings
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


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, '_settings.json')


class Settings(BaseSettings):
    DEBUG: bool = True
    UVICORN: UvicornSettings = UvicornSettings()
    DATABASE: MasterSlaveDatabaseSettings = MasterSlaveDatabaseSettings(
        MASTER=DatabaseSettings(
            PASSWORD='password',
            NAME='otus_highload'
        )
    )
    BASE_PAGE_LIMIT: int = 100


settings = Settings.from_json(CONFIG_PATH)
