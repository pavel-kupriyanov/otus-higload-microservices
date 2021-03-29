from typing import List

from ..crud import CRUDManager
from ..models import Shard, DatabaseInfo, ShardState

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
