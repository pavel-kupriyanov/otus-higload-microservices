from .base import BaseShardingModel
from ..models import Timestamp


class Message(BaseShardingModel):
    _table_name = 'messages'
    _fields = ('id', 'chat_key', 'author_id', 'text', 'created')
    _datetime_fields = ('created',)

    chat_key: str
    author_id: int
    text: str
    created: Timestamp

    def get_sharding_key(self) -> str:
        return self.chat_key
