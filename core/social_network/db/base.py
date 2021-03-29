from itertools import cycle
from collections import namedtuple
from datetime import datetime
from typing import Any, Tuple, Optional, Iterable, TypeVar, Type

from pydantic import BaseModel as PydanticBaseModel

from aiomysql import DatabaseError as RawDatabaseError

from social_network.settings import Settings, settings

from .db import (
    BaseDatabaseConnector,
    DatabaseResponse
)
from .exceptions import DatabaseError
from .connectors_storage import BaseConnectorsStorage

M = TypeVar('M', bound='BaseModel', covariant=True)

Timestamp = float  # Alias


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


class BaseManager:
    model: M

    def __init__(self, connector_storage: BaseConnectorsStorage,
                 conf: Settings = settings):
        db_slaves = conf.DATABASE.SLAVES

        self.connector_storage = connector_storage
        self.conf = conf
        self.read_only_confs = cycle(db_slaves) if db_slaves else None

    async def get_connector(self, read_only=False) -> BaseDatabaseConnector:
        connector_storage = self.connector_storage
        if read_only and self.read_only_confs:
            slave_conf = next(self.read_only_confs)
            return await connector_storage.get_connector(slave_conf)
        return await connector_storage.get_connector(self.conf.DATABASE.MASTER)

    async def execute(self,
                      query: str,
                      params: Optional[Iterable[Any]] = None,
                      read_only=False,
                      last_row_id=False,
                      raise_if_empty=True,
                      execute_many=False) -> DatabaseResponse:
        conn = await self.get_connector(read_only=read_only)
        try:
            return await conn.make_query(query, params,
                                         last_row_id=last_row_id,
                                         raise_if_empty=raise_if_empty,
                                         execute_many=execute_many)
        except RawDatabaseError as e:
            raise DatabaseError(e.args) from e
