from async_lru import alru_cache
from typing import Tuple, Any, List, Union

from social_network.settings import settings

from .base import BaseManager, M
from .mixins import LimitMixin, OrderMixin

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
