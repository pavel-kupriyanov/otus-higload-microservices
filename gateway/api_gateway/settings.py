import os
import json
from copy import deepcopy

from pydantic import BaseModel, BaseSettings as PydanticSettings


class ServiceSettings(BaseModel):
    HOST: str = '0.0.0.0'
    PORT: int = 9999


class UvicornSettings(BaseModel):
    ASGI_PATH: str = 'main:app'
    HOST: str = '0.0.0.0'
    PORT: int = int(os.getenv('PORT') or 10000)
    WORKERS = 1


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
    UVICORN: UvicornSettings = UvicornSettings()
    MONOLITH: ServiceSettings = ServiceSettings()
    AUTH: ServiceSettings = ServiceSettings(PORT=9900)


settings = Settings.from_json(CONFIG_PATH)
