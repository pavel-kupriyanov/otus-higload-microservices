from uuid import uuid4
from typing import List
from datetime import datetime

from social_network.settings import settings

from ..models import Message
from ..base import BaseShardingManager
from ...mixins import LimitMixin
from ...models import TIMESTAMP_FORMAT

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
