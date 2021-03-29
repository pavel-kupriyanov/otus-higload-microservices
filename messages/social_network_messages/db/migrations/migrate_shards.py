import asyncio
from typing import List

from social_network_messages.settings import settings, DatabaseSettings

from .main import migrate, SHARDS_PATH

from ..connectors_storage import ConnectorsStorage
from ..managers import ShardsManager
from ..models import Shard


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
