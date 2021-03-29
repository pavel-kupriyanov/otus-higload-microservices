from enum import Enum
from typing import Tuple, Type, TypeVar
from datetime import datetime
from collections import namedtuple

from pydantic import SecretStr, BaseModel as PydanticBaseModel

from ..settings import DatabaseSettings

TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'

Timestamp = float  # Alias

M = TypeVar('M', bound='BaseModel', covariant=True)
S = TypeVar('S', bound='BaseShardingModel', covariant=True)


class BaseModel(PydanticBaseModel):
    _table_name: str
    _fields: Tuple[str, ...]
    _datetime_fields: Tuple[str, ...] = tuple()

    id: int

    @classmethod
    def from_db(cls: Type[M], tpl: tuple) -> M:
        parsing_tuple = namedtuple('_', cls._fields)
        fields = parsing_tuple(*tpl)._asdict()

        # Special parsing for Timestamp field
        for name in cls._datetime_fields:
            if isinstance(fields[name], datetime):
                fields[name] = fields[name].timestamp()

        return cls(**fields)


class BaseShardingModel(BaseModel):
    id: str

    def get_sharding_key(self) -> str:
        return str(self.id)


class DatabaseInfo(BaseModel):
    _table_name = 'database_info'
    _fields = ('id', 'host', 'port', 'user', 'password', 'name')

    host: str
    port: int
    user: str
    password: SecretStr
    name: str

    def as_settings(self) -> DatabaseSettings:
        return DatabaseSettings(
            HOST=self.host,
            PORT=self.port,
            USER=self.user,
            PASSWORD=self.password.get_secret_value(),
            NAME=self.name
        )


class ShardState(str, Enum):
    READY = 'READY'
    ADDING = 'ADDING'
    ERROR = 'ERROR'


class Shard(BaseModel):
    _table_name = 'shards_info'
    _fields = ('id', 'db_info', 'shard_table', 'shard_key', 'state')

    db_info: DatabaseInfo
    shard_table: str
    shard_key: int
    state: ShardState


class Message(BaseShardingModel):
    _table_name = 'messages'
    _fields = ('id', 'chat_key', 'author_id', 'text', 'created')
    _datetime_fields = ('created',)

    chat_key: str
    author_id: int
    text: str
    created: Timestamp

    def get_sharding_key(self) -> str:
        return self.chat_key
