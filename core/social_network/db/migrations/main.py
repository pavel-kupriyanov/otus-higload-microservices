import os

from yoyo import read_migrations
from yoyo import get_backend

from social_network.settings import DatabaseSettings

MASTER_PATH = '/'.join([os.path.dirname(__file__), 'sql'])
SHARDS_PATH = '/'.join([os.path.dirname(__file__), 'shards_sql'])


def get_db_str(s: DatabaseSettings):
    return f'{s.DB}://{s.USER}:{s.PASSWORD.get_secret_value()}' \
           f'@{s.HOST}:{s.PORT}/{s.NAME}'


def migrate(conf: DatabaseSettings, path: str = MASTER_PATH):
    backend = get_backend(get_db_str(conf))
    migrations = read_migrations(path)

    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))
