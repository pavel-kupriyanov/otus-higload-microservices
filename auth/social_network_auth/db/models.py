from collections import namedtuple
from datetime import datetime
from typing import Tuple, TypeVar, Type

from pydantic import BaseModel as PydanticBaseModel

M = TypeVar('M', bound='BaseModel', covariant=True)

Timestamp = float  # Alias
TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'


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


class AccessToken(BaseModel):
    _table_name = 'access_tokens'
    _fields = ('id', 'value', 'user_id', 'expired_at')
    _datetime_fields = ('expired_at',)

    value: str
    user_id: int
    expired_at: Timestamp
