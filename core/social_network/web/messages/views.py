from typing import Optional, List
from fastapi import (
    APIRouter,
    Depends,
)
from fastapi_utils.cbv import cbv

from social_network.db.managers import UserManager
from social_network.db.sharding.managers import MessagesManager
from social_network.db.sharding.models import Message

from ..depends import (
    get_user_id,
    get_messages_manager,
    get_user_manager
)
from .models import MessageQueryParams, MessageCreatePayload

from ..utils import authorize_only

router = APIRouter()


@cbv(router)
class MessagesViewSet:
    user_id: Optional[int] = Depends(get_user_id)
    user_manager: UserManager = Depends(get_user_manager)
    messages_manager: MessagesManager = Depends(get_messages_manager)

    def get_key(self, target_user_id: int):
        min_id, max_id = sorted([self.user_id, target_user_id])
        return f'{min_id}:{max_id}'

    @router.post('/', response_model=Message, status_code=201,
                 responses={
                     201: {'description': 'Message created.'},
                     401: {'description': 'Unauthorized.'},
                     404: {'description': 'User not found'}
                 })
    @authorize_only
    async def create(self, p: MessageCreatePayload) -> Message:
        target_user = await self.user_manager.get(p.to_user_id)
        key = self.get_key(target_user.id)
        return await self.messages_manager.create(key, self.user_id, p.text)

    @router.get('/', response_model=List[Message], responses={
        200: {'description': 'List of messages.'},
    })
    async def list(self, q: MessageQueryParams = Depends(MessageQueryParams)) \
            -> List[Message]:
        return await self.messages_manager.list(
            chat_key=self.get_key(q.to_user_id),
            after_timestamp=q.after_timestamp,
            limit=q.paginate_by,
            offset=q.offset
        )
