from datetime import datetime as dt
from typing import Dict, Type, Optional, List

from ..crud import CRUDManager
from ..models import (
    New,
    NewsType,
    Payload,
    TIMESTAMP_FORMAT,
    AddedPostNewPayload,
    AddedHobbyNewPayload,
    AddedFriendNewPayload
)

GET_USER_NEWS = '''
    SELECT id, author_id, type, payload, created FROM news
    WHERE author_id IN %s
'''

GET_NEWS = '''
    SELECT id, author_id, type, payload, created FROM news
'''

GET_NEWS_AFTER_TIMESTAMP = '''
    SELECT id, author_id, type, payload, created FROM news
    WHERE created > %s
'''


class NewsManager(CRUDManager):
    model = New
    auto_id = False

    payload_mapping: Dict[NewsType, Type[Payload]] = {
        NewsType.ADDED_POST: AddedPostNewPayload,
        NewsType.ADDED_HOBBY: AddedHobbyNewPayload,
        NewsType.ADDED_FRIEND: AddedFriendNewPayload
    }

    async def create(self, id: str, author_id: int, news_type: NewsType,
                     payload: Payload, created: str) -> New:
        params = (id, author_id, news_type, payload.json(), created)
        query = self._make_create_query()
        await self.execute(query, params, raise_if_empty=False)
        return await self._get(id, read_only=False)

    async def create_from_model(self, new: New) -> New:
        return await self.create(
            new.id,
            new.author_id,
            new.type,
            new.payload,
            dt.fromtimestamp(new.created).strftime(TIMESTAMP_FORMAT)
        )

    async def list(self, author_ids: Optional[List[int]] = None,
                   order_by='created', order='DESC', limit=None, offset=0):
        params, query = tuple(), GET_NEWS
        if author_ids is not None:
            params, query = (tuple(author_ids),), GET_USER_NEWS
        limit = limit or self.conf.BASE_PAGE_LIMIT
        return await self._list(params, query, order_by=order_by, order=order,
                                limit=limit, offset=offset)

    async def list_after_timestamp(self, timestamp: str, order_by='created',
                                   order='DESC', limit=None, offset=0):
        params, query = (timestamp,), GET_NEWS_AFTER_TIMESTAMP
        limit = limit or self.conf.BASE_PAGE_LIMIT
        return await self._list(params, query, order_by=order_by, order=order,
                                limit=limit, offset=offset)
