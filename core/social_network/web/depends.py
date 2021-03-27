from typing import Optional
from functools import lru_cache
from datetime import datetime

from fastapi import (
    Header,
    Depends,
    Request,
    WebSocket,
    HTTPException
)
from social_network.db.models import User
from social_network.db.managers import (
    AuthUserManager,
    AccessTokenManager,
    FriendRequestManager,
    UserManager,
    FriendshipManager,
    HobbiesManager,
    UsersHobbyManager,
    NewsManager,
)
from social_network.db.sharding.managers import MessagesManager
from social_network.db.exceptions import RowsNotFoundError
from social_network.services import (
    DependencyInjector,
    KafkaProducer,
    RedisService,
    FeedWebSocketService
)

from social_network.settings import settings


@lru_cache(1)
def get_settings_depends():
    return settings


def get_state(request: Request = None, ws: WebSocket = None):
    if request:
        return request.app.state
    return ws.app.state


def get_injector_depends(state=Depends(get_state)) -> DependencyInjector:
    return state.dependency_injector


@lru_cache(1)
def get_user_manager(injector=Depends(get_injector_depends)) -> UserManager:
    return injector.get_manager(UserManager)


@lru_cache(1)
def get_auth_user_manager(injector=Depends(get_injector_depends)) \
        -> AuthUserManager:
    return injector.get_manager(AuthUserManager)


@lru_cache(1)
def get_access_token_manager(injector=Depends(get_injector_depends)) \
        -> AccessTokenManager:
    return injector.get_manager(AccessTokenManager)


@lru_cache(1)
def get_friend_request_manager(injector=Depends(get_injector_depends)) \
        -> FriendRequestManager:
    return injector.get_manager(FriendRequestManager)


@lru_cache(1)
def get_friendship_manager(injector=Depends(get_injector_depends)) \
        -> FriendshipManager:
    return injector.get_manager(FriendshipManager)


@lru_cache(1)
def get_hobby_manager(injector=Depends(get_injector_depends)) \
        -> HobbiesManager:
    return injector.get_manager(HobbiesManager)


@lru_cache(1)
def get_user_hobby_manager(injector=Depends(get_injector_depends)) \
        -> UsersHobbyManager:
    return injector.get_manager(UsersHobbyManager)


@lru_cache(1)
def get_messages_manager(injector=Depends(get_injector_depends)) \
        -> MessagesManager:
    return injector.get_manager(MessagesManager)


@lru_cache(1)
def get_news_manager(injector=Depends(get_injector_depends)) \
        -> MessagesManager:
    return injector.get_manager(NewsManager)


@lru_cache(1)
def get_kafka_producer(injector=Depends(get_injector_depends)) \
        -> KafkaProducer:
    return injector.kafka_producer


@lru_cache(1)
def get_redis_client(injector=Depends(get_injector_depends)) -> RedisService:
    return injector.redis_service


@lru_cache(1)
def get_ws_service(injector=Depends(get_injector_depends)) -> FeedWebSocketService:
    return injector.ws_service


async def get_user_id(
        x_auth_token: Optional[str] = Header(None),
        access_token_manager: AccessTokenManager = Depends(
            get_access_token_manager),
) -> Optional[int]:
    if x_auth_token is None:
        return None
    try:
        access_token = await access_token_manager.get_by_value(x_auth_token)
    except RowsNotFoundError:
        raise HTTPException(status_code=401, detail='Invalid token header')
    if datetime.fromtimestamp(access_token.expired_at) < datetime.now():
        raise HTTPException(status_code=400,
                            detail='Expired token, please re-login')
    return access_token.user_id


async def get_user(
        user_id: int = Depends(get_user_id),
        user_manager: UserManager = Depends(get_user_manager)
) -> Optional[User]:
    if user_id is None:
        return None
    return await user_manager.get(user_id)


async def get_ws_user(ws: WebSocket, injector=Depends(get_injector_depends)) \
        -> Optional[User]:
    await ws.accept()
    auth = await ws.receive_json()
    token_manager = get_access_token_manager(injector)
    users_manager = get_user_manager(injector)
    user_id = await get_user_id(auth['value'], token_manager)
    return await get_user(user_id, users_manager)
