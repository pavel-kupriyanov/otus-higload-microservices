from typing import Optional, List
from functools import lru_cache

from fastapi import (
    APIRouter,
    Depends,
    Header,
    Request,
    HTTPException
)
from httpx import AsyncClient
from fastapi_utils.cbv import cbv

from social_network_messages.settings import settings
from social_network_messages.db.connectors_storage import ConnectorsStorage
from social_network_messages.db.managers import MessagesManager
from social_network_messages.db.models import Message

from .models import MessageQueryParams, MessageCreatePayload

from .utils import authorize_only

router = APIRouter()


def get_connector_storage(request: Request) -> ConnectorsStorage:
    return request.app.state.storage


@lru_cache(1)
def get_messages_manager(storage=Depends(get_connector_storage)) \
        -> MessagesManager:
    return MessagesManager(storage, settings)


async def get_user_id(x_user_id: Optional[int] = Header(None)) -> Optional[int]:
    return x_user_id


async def is_user_exists(user_id: int) -> bool:
    gateway = settings.API_GATEWAY
    url = f'http://{gateway.HOST}:{gateway.PORT}'
    async with AsyncClient(base_url=url) as client:
        response = await client.get(f'/api/vi/{user_id}/')
    return not response.is_error


@cbv(router)
class MessagesViewSet:
    user_id: Optional[int] = Depends(get_user_id)
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
        if not (await is_user_exists(p.to_user_id)):
            raise HTTPException(status_code=404)
        key = self.get_key(p.to_user_id)
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
