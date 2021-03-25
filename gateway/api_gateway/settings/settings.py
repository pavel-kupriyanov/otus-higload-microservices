import os.path

from .base import (
    BaseSettings,
    UvicornSettings,
    ServiceSettings
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_DIR, 'settings/_settings.json')


class Settings(BaseSettings):
    DEBUG: bool = True
    UVICORN: UvicornSettings = UvicornSettings()
    MONOLITH: ServiceSettings = ServiceSettings()


settings = Settings.from_json(CONFIG_PATH)
