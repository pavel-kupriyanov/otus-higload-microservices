import asyncio
from typing import List

from social_network.db.connectors_storage import ConnectorsStorage
from social_network.db.migrations import migrate, SHARDS_PATH
from social_network.db.managers import ShardsManager
from social_network.db.models import Shard

from social_network.settings import settings, DatabaseSettings


async def get_shards_info(conf: DatabaseSettings) -> List[Shard]:
    storage = ConnectorsStorage()
    await storage.create_connector(conf)
    manager = ShardsManager(storage, conf=settings)
    return await manager.get_shards()


async def main(conf: DatabaseSettings):
    infos = await get_shards_info(conf)
    shard_configs = [info.db_info.as_settings() for info in infos]
    for shard_conf in shard_configs:
        migrate(shard_conf, SHARDS_PATH)


if __name__ == '__main__':
    asyncio.run(main(settings.DATABASE.MASTER))
