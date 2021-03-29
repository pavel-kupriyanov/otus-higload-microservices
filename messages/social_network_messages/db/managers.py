from itertools import cycle
from uuid import uuid4
from typing import (
    Any,
    Tuple,
    Optional,
    Iterable,
    Union,
    List,
)
from datetime import datetime

from async_lru import alru_cache
from zlib import crc32
from aiomysql import DatabaseError as RawDatabaseError

from social_network_messages.settings import (
    Settings, settings, DatabaseSettings
)

from .models import (
    M,
    S,
    Shard,
    ShardState,
    DatabaseInfo,
    Message,
    TIMESTAMP_FORMAT
)
from .db import (
    BaseDatabaseConnector,
    DatabaseResponse
)
from .exceptions import DatabaseError
from .connectors_storage import BaseConnectorsStorage
from .mixins import LimitMixin, OrderMixin


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


class BaseCRUDManager(BaseManager, LimitMixin, OrderMixin):
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
                    order: str = None,
                    limit: int = settings.BASE_PAGE_LIMIT,
                    offset: int = 0) -> List[M]:
        if order_by and order:
            query = self.add_order(query, order_by, order)
        query = self.add_limit(query, limit, offset)
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


class DatabaseInfoManager(CRUDManager):
    model = DatabaseInfo

    async def create(self, db_conf: DatabaseSettings) -> DatabaseInfo:
        params = (db_conf.HOST, db_conf.PORT, db_conf.USER,
                  db_conf.PASSWORD.get_secret_value(), db_conf.NAME)
        return await self._create(params)


GET_SHARDS_WITH_DATABASE_INFO = '''
    SELECT 
       database_info.id       as db_id,
       database_info.host     as db_host,
       database_info.port     as db_port,
       database_info.user     as db_user,
       database_info.password as db_password,
       database_info.name     as db_name,
       shards_info.id,
       shard_table,
       shard_key,
       state
FROM shards_info
         JOIN database_info ON db_info = database_info.id;

'''

CREATE_SHARD = '''
    INSERT INTO shards_info (db_info, shard_table, shard_key, state)
    VALUES (%s, %s, %s, %s);
'''


class ShardsManager(CRUDManager):
    model = Shard

    async def get_shards(self) -> List[Shard]:
        rows = await self.execute(GET_SHARDS_WITH_DATABASE_INFO, [],
                                  read_only=True, raise_if_empty=False)
        return [self.parse_shard(row) for row in rows]

    def parse_shard(self, raw_shard: tuple) -> Shard:
        db_info = DatabaseInfo.from_db(raw_shard[0:6])
        id, shard_table, shard_key, state = raw_shard[6:]
        return Shard(id=id, db_info=db_info, shard_table=shard_table,
                     shard_key=shard_key, state=state)

    async def create(self, db_info_id: int, shard_table: str, shard_key: str,
                     state: ShardState = ShardState.ADDING) -> Shard:
        params = (db_info_id, shard_table, shard_key, state)
        id = await self.execute(CREATE_SHARD, params, last_row_id=True)
        shards = await self.get_shards()
        return [shard for shard in shards if shard.id == id][0]


CREATE_MESSAGE = '''
    INSERT INTO messages (id, chat_key, author_id, text)
     VALUES (%s, %s, %s, %s);
'''

GET_MESSAGE = '''
    SELECT id, chat_key, author_id, text, created FROM messages
    WHERE id = %s;
'''

GET_MESSAGES = '''
    SELECT id, chat_key, author_id, text, created FROM messages
    WHERE chat_key = %s AND created > %s
    ORDER BY created DESC 
'''


class BaseShardingManager(BaseManager):
    model: S

    def __init__(self, connector_storage: BaseConnectorsStorage,
                 conf: Settings = settings):
        super(BaseShardingManager, self).__init__(connector_storage, conf)
        self.shards_manager = ShardsManager(connector_storage, conf=conf)

    async def execute(self,
                      query: str,
                      key: str = '',
                      params: Optional[Iterable[Any]] = None,
                      read_only=False,
                      last_row_id=False,
                      raise_if_empty=True,
                      execute_many=False) -> DatabaseResponse:
        conn = await self.get_shard_connector(key)
        try:
            return await conn.make_query(query, params,
                                         last_row_id=last_row_id,
                                         raise_if_empty=raise_if_empty,
                                         execute_many=execute_many)
        except RawDatabaseError as e:
            raise DatabaseError(e.args) from e

    async def get_shard_connector(self, key: str) -> BaseDatabaseConnector:
        shard_infos = await self.get_shard_infos()
        calculated_hash = self.calculate_hash(key, len(shard_infos))
        shard_info = [
            info for info in shard_infos if
            info.shard_key == calculated_hash
        ][0]
        conf = shard_info.db_info.as_settings()
        return await self.connector_storage.get_connector(conf)

    async def get_shard_infos(self) -> List[Shard]:
        shard_infos = await self.shards_manager.get_shards()
        filtered_shards = [
            shard_info for shard_info in shard_infos if
            shard_info.shard_table == self.model._table_name and
            shard_info.state == ShardState.READY
        ]
        if not filtered_shards:
            raise DatabaseError(f'Not shards for table {self.model._table}')
        return filtered_shards

    @staticmethod
    def calculate_hash(key: str, max_hash: int) -> int:
        return crc32(key.encode()) % max_hash


class MessagesManager(BaseShardingManager, LimitMixin):
    model = Message

    async def _get(self, id: str, key: str) -> Message:
        rows = await self.execute(GET_MESSAGE, key, (id,))
        return self.model.from_db(rows[0])

    async def create(self, chat_key: str, author_id: int, text: str) -> Message:
        id = str(uuid4())
        params = (id, chat_key, author_id, text)
        await self.execute(CREATE_MESSAGE, chat_key, params, last_row_id=True)
        return await self._get(id, chat_key)

    async def list(self,
                   chat_key: str,
                   after_timestamp: float = 0,
                   limit: int = settings.BASE_PAGE_LIMIT,
                   offset: int = 0) -> List[Message]:
        query = self.add_limit(GET_MESSAGES, limit, offset)
        after_timestamp = datetime.fromtimestamp(after_timestamp) \
            .strftime(TIMESTAMP_FORMAT)
        params = (chat_key, after_timestamp)
        rows = await self.execute(query, chat_key, params, read_only=True,
                                  raise_if_empty=False)
        return [self.model.from_db(row) for row in rows]
