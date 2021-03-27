import os.path

from social_network.settings.base import (
    BaseSettings,
    UvicornSettings,
    DatabaseSettings,
    KafkaSettings,
    RedisSettings,
    NewsCacheSettings,
    RabbitMQSettings,
    MasterSlaveDatabaseSettings
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_DIR, 'settings/settings.local.json')


class Settings(BaseSettings):
    DEBUG: bool = True
    UVICORN: UvicornSettings = UvicornSettings()
    DATABASE: MasterSlaveDatabaseSettings = MasterSlaveDatabaseSettings(
        MASTER=DatabaseSettings(
            PASSWORD='password',
            NAME='otus_highload'
        )
    )
    KAFKA: KafkaSettings = KafkaSettings()
    REDIS: RedisSettings = RedisSettings()
    RABBIT: RabbitMQSettings = RabbitMQSettings()
    NEWS_CACHE: NewsCacheSettings = NewsCacheSettings()
    TOKEN_EXPIRATION_TIME = 60 * 60 * 24 * 7
    BASE_PAGE_LIMIT = 10000

    class Config:
        fields = {
            'DATABASE': {
                'env': 'DATABASE_CONF',
            },
            'KAFKA': {
                'env': 'KAFKA_CONF'
            },
            'REDIS': {
                'env': 'REDIS_CONF'
            },
            'RABBIT': {
                'env': 'RABBIT_CONF'
            }
        }


if os.getenv('HEROKU', False):
    settings = Settings()
else:
    settings = Settings.from_json(CONFIG_PATH)
