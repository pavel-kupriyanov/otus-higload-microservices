from typing import Optional, Tuple, Any, Union

import aiomysql

from social_network.settings import DatabaseSettings

from .exceptions import RowsNotFoundError

Rows = Tuple[Tuple[Any, ...]]
DatabaseResponse = Union[Rows, int, str]


class BaseDatabaseConnector:

    async def make_query(self,
                         query_template: str,
                         params: Optional[Tuple[Any, ...]] = None,
                         max_rows: Optional[int] = None,
                         only_count=False,
                         last_row_id=False,
                         raise_if_empty=True,
                         execute_many=False) \
            -> DatabaseResponse:
        raise NotImplementedError

    async def close(self):
        raise NotImplementedError


class DatabaseConnector(BaseDatabaseConnector):

    def __init__(self, conf: DatabaseSettings):
        self.conf = conf
        self.pool = None

    async def make_query(self,
                         query_template: str,
                         params: Optional[Tuple[Any, ...]] = None,
                         max_rows: Optional[int] = None,
                         only_count=False,
                         last_row_id=False,
                         raise_if_empty=True,
                         execute_many=False) \
            -> DatabaseResponse:
        async with self.pool.acquire() as conn:  # type: aiomysql.Connection
            async with conn.cursor() as cursor:  # type: aiomysql.Cursor
                if execute_many:
                    rowcount = await cursor.executemany(query_template, params)
                else:
                    rowcount = await cursor.execute(query_template, params)

                if only_count:
                    return rowcount
                if last_row_id:
                    return cursor.lastrowid
                data = await cursor.fetchmany(max_rows or rowcount)

                if raise_if_empty and not data:
                    raise RowsNotFoundError
                return data

    async def start(self):
        await  self._create_pool()

    async def _create_pool(self):
        c = self.conf
        password = c.PASSWORD.get_secret_value()
        self.pool = await aiomysql.create_pool(host=c.HOST, port=c.PORT,
                                               user=c.USER, password=password,
                                               db=c.NAME,
                                               minsize=c.MAX_CONNECTIONS,
                                               maxsize=c.MAX_CONNECTIONS,
                                               autocommit=True)

    async def close(self):
        self.pool.close()
        await self.pool.wait_closed()


async def get_connector(conf: DatabaseSettings) -> BaseDatabaseConnector:
    connector = DatabaseConnector(conf)
    await connector.start()
    return connector
