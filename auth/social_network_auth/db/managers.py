from itertools import cycle
from datetime import datetime
from typing import Any, Optional, Iterable, TypeVar, List, Union, Tuple

from async_lru import alru_cache
from aiomysql import DatabaseError as RawDatabaseError

from social_network_auth.settings import Settings, settings

from .connector import (
    BaseDatabaseConnector,
    DatabaseResponse
)
from .models import AccessToken, TIMESTAMP_FORMAT
from .connectors_storage import BaseConnectorsStorage
from .exceptions import DatabaseError

M = TypeVar('M', bound='BaseModel', covariant=True)

Timestamp = float  # Alias


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


CREATE = '''
    INSERT INTO {table_name} ({fields}) VALUES ({values});
    SELECT LAST_INSERT_ID();
'''
BULK_CREATE = 'INSERT INTO {table_name} ({fields}) VALUES ({values});'
GET = 'SELECT {fields} FROM {table_name} WHERE id = %s;'
DELETE = 'DELETE FROM {table_name} WHERE id = %s;'


class BaseCRUDManager(BaseManager):
    auto_id: bool = True

    def _make_create_query(self, query=CREATE) -> str:
        fields = list(self.model._fields)
        if self.auto_id:
            fields.remove('id')
        return query.format(
            table_name=self.model._table_name,
            fields=", ".join(fields),
            values=", ".join('%s' for _ in fields)
        )

    async def _create(self, params: Tuple[Any, ...]) -> M:
        query = self._make_create_query()
        id = await self.execute(query, params, last_row_id=True)
        return await self._get(id, read_only=False)

    async def _bulk_create(self, params: Tuple[Tuple[Any, ...], ...]):
        query = self._make_create_query(BULK_CREATE)
        await self.execute(query, params,
                           raise_if_empty=False,
                           execute_many=True)

    async def _update(self, id: int, params: Tuple[Any, ...], query: str) -> M:
        await self.execute(query, params, raise_if_empty=False)
        return await self._get(id, read_only=False)

    async def _get(self, id: Union[int, str], read_only=True) -> M:
        query = GET.format(
            fields=", ".join(self.model._fields),
            table_name=self.model._table_name
        )
        rows = await self.execute(query, (id,), read_only=read_only)
        return self.model.from_db(rows[0])

    async def _list(self,
                    params: Tuple[Any, ...],
                    query: str,
                    order_by: str = None,
                    offset: int = 0) -> List[M]:
        rows = await self.execute(query, params, read_only=True,
                                  raise_if_empty=False)
        models = [self.model.from_db(row) for row in rows]
        return models

    async def _delete(self, id: int):
        query = DELETE.format(table_name=self.model._table_name)
        await self.execute(query, (id,), raise_if_empty=False)


class CRUDManager(BaseCRUDManager):
    model: M

    @alru_cache(maxsize=1000)
    async def get(self, id: int) -> M:
        return await self._get(id)

    async def delete(self, id: int):
        return await self._delete(id)

    async def bulk_create(self, params: Tuple[Tuple[Any, ...], ...]):
        return await self._bulk_create(params)


GET_USER_ACTIVE_TOKENS = '''
        SELECT id, value, user_id, expired_at FROM access_tokens
        WHERE user_id = %s and expired_at > NOW()
    '''

UPDATE_TOKEN = '''
        UPDATE access_tokens
        SET expired_at = %s
        WHERE id = %s
    '''

GET_TOKEN_BY_VALUE = '''
        SELECT id, value, user_id, expired_at FROM access_tokens
        WHERE value = %s
    '''


class AccessTokenManager(CRUDManager):
    model = AccessToken

    async def create(self, value: str, user_id: int, expired_at: datetime) \
            -> AccessToken:
        params = (value, user_id, expired_at.strftime(TIMESTAMP_FORMAT))
        return await self._create(params)

    async def update(self, token_id: int, new_expired_at: datetime) \
            -> AccessToken:
        params = (new_expired_at.strftime(TIMESTAMP_FORMAT), token_id)
        return await self._update(token_id, params, UPDATE_TOKEN)

    async def list_user_active(self, user_id: int) -> List[AccessToken]:
        return await self._list((user_id,), GET_USER_ACTIVE_TOKENS)

    @alru_cache(maxsize=100)
    async def get_by_value(self, value: str) -> AccessToken:
        tokens = await self.execute(GET_TOKEN_BY_VALUE, (value,),
                                    read_only=True)
        return AccessToken.from_db(tokens[0])
