from zlib import crc32
from typing import TypeVar, List, Optional, Iterable, Any

from aiomysql import DatabaseError as RawDatabaseError

from social_network.settings import Settings, settings

from ..db import BaseDatabaseConnector, DatabaseResponse
from ..exceptions import DatabaseError
from ..base import BaseManager, BaseModel
from ..managers import ShardsManager
from ..connectors_storage import BaseConnectorsStorage
from ..models import ShardState, Shard

S = TypeVar('S', bound='BaseShardingModel', covariant=True)


class BaseShardingModel(BaseModel):
    id: str

    def get_sharding_key(self) -> str:
        return str(self.id)


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
