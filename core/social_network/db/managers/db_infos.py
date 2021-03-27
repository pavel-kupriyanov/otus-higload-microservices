from social_network.settings import DatabaseSettings

from ..crud import CRUDManager
from ..models import DatabaseInfo


class DatabaseInfoManager(CRUDManager):
    model = DatabaseInfo

    async def create(self, db_conf: DatabaseSettings) -> DatabaseInfo:
        params = (db_conf.HOST, db_conf.PORT, db_conf.USER,
                  db_conf.PASSWORD.get_secret_value(), db_conf.NAME)
        return await self._create(params)
