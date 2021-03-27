from typing import List
from fastapi import APIRouter, WebSocket
import websockets

from api_gateway.utils.core import generate_handler
from api_gateway.models.response import (
    AccessToken,
    AuthUser,
    FriendRequest,
    Friendship,
    Hobby,
    Message,
    New,
    User,
    UserHobby
)
from api_gateway.models.request import (
    LoginPayload,
    RegistrationPayload,
    HobbyCreatePayload,
    MessageCreatePayload,
    NewCreatePayload
)
from api_gateway.models.path_info import PathInfo
from api_gateway.settings import settings

router = APIRouter()
endpoints = []

MAPPING = {
    'login': PathInfo(
        path='/auth/login/',
        service_path='/auth/login/',
        request_model=LoginPayload,
        response_model=AccessToken,
        status_code=201,
        method='POST',
        responses={
            201: {'description': 'Success login'},
            400: {'description': 'Invalid email or password'}
        }
    ),
    'register': PathInfo(
        path='/auth/register/',
        service_path='/auth/register/',
        request_model=RegistrationPayload,
        response_model=AuthUser,
        status_code=201,
        method='POST',
        responses={
            201: {'description': 'User created'},
            400: {'description': 'Invalid email'}
        }
    ),
    'create_friendship': PathInfo(
        path='/friendships/{user_id}/',
        service_path='/friendships/{user_id}/',
        response_model=FriendRequest,
        status_code=201,
        method='POST',
        authorized=True,
        path_params={'user_id': int},
        responses={
            201: {'description': 'Friend request created.'},
            400: {'description': 'Already friends.'},
            401: {'description': 'Unauthorized.'},
            404: {'description': 'User not found.'}
        }
    ),
    'cancel_friendship': PathInfo(
        path='/friendships/{id}/',
        service_path='/friendships/{id}/',
        method='DELETE',
        authorized=True,
        path_params={'id': int},
        responses={
            204: {'description': 'Friend request cancelled.'},
            401: {'description': 'Unauthorized.'},
            403: {'description': 'Only request owner can cancel it'},
            404: {'description': 'Request not found.'}
        }
    ),
    'get_friendship': PathInfo(
        path='/friendships/{id}/',
        service_path='/friendships/{id}/',
        response_model=FriendRequest,
        status_code=200,
        method='GET',
        authorized=True,
        path_params={'id': int},
        responses={
            200: {'description': 'Success'},
            401: {'description': 'Unauthorized.'},
            403: {'description': 'Only participants can get it'},
            404: {'description': 'Request not found.'}
        }
    ),
    'decline_friend_request': PathInfo(
        path='/friendships/decline/{id}/',
        service_path='/friendships/decline/{id}/',
        method='PUT',
        authorized=True,
        path_params={'id': int},
        responses={
            204: {'description': 'Success'},
            401: {'description': 'Unauthorized.'},
            403: {'description': 'Only request target can decline it'},
            404: {'description': 'Request not found.'}
        }
    ),
    'accept_friend_request': PathInfo(
        path='/friendships/accept/{id}/',
        service_path='/friendships/accept/{id}/',
        method='PUT',
        response_model=Friendship,
        authorized=True,
        path_params={'id': int},
        status_code=201,
        responses={
            201: {'description': 'Success'},
            401: {'description': 'Unauthorized.'},
            403: {'description': 'Only request target can accept it'},
            404: {'description': 'Request not found.'}
        }
    ),
    'delete_friendship': PathInfo(
        path='/friendships/friendship/{friend_id}/',
        service_path='/friendships/friendship/{friend_id}/',
        method='DELETE',
        authorized=True,
        path_params={'friend_id': int},
        responses={
            204: {'description': 'Friendship cancelled.'},
            401: {'description': 'Unauthorized.'},
        }
    ),
    'friend_request_list': PathInfo(
        path='/friendships/',
        service_path='/friendships/',
        method='GET',
        response_model=List[FriendRequest],
        authorized=True,
        status_code=200,
        responses={
            200: {'description': 'List of friend requests'},
        }
    ),
    'create_hobby': PathInfo(
        path='/hobbies/',
        service_path='/hobbies/',
        request_model=HobbyCreatePayload,
        response_model=Hobby,
        status_code=201,
        method='POST',
        authorized=True,
        responses={
            201: {'description': 'Hobby created.'},
            401: {'description': 'Unauthorized.'},
        }
    ),
    'get_hobby': PathInfo(
        path='/hobbies/{id}/',
        service_path='/hobbies/{id}/',
        response_model=Hobby,
        status_code=200,
        method='GET',
        path_params={'id': int},
        responses={
            200: {'description': 'Success'},
            404: {'description': 'Hobby not found.'}
        }
    ),
    'get_hobbies': PathInfo(
        path='/hobbies/',
        service_path='/hobbies/',
        response_model=List[Hobby],
        status_code=200,
        method='GET',
        responses={
            200: {'description': 'List of hobbies.'},
        }
    ),
    'create_message': PathInfo(
        path='/messages/',
        service_path='/messages/',
        request_model=MessageCreatePayload,
        response_model=Message,
        status_code=201,
        method='POST',
        authorized=True,
        responses={
            201: {'description': 'Message created.'},
            401: {'description': 'Unauthorized.'},
            404: {'description': 'User not found'}
        }
    ),
    'get_messages': PathInfo(
        path='/messages/',
        service_path='/messages/',
        response_model=List[Message],
        status_code=200,
        method='GET',
        authorized=True,
        responses={
            200: {'description': 'List of messages.'},
        }
    ),
    'create_new': PathInfo(
        path='/news/',
        service_path='/news/',
        request_model=NewCreatePayload,
        response_model=New,
        status_code=201,
        method='POST',
        authorized=True,
        responses={
            201: {'description': 'Hobby created.'},
            401: {'description': 'Unauthorized.'},
        }
    ),
    'get_feed': PathInfo(
        path='/news/feed/',
        service_path='/news/feed/',
        response_model=List[New],
        status_code=200,
        method='GET',
        authorized=True,
        responses={
            200: {'description': 'User feed.'},
        }
    ),
    'get_user_news': PathInfo(
        path='/news/{user_id}/',
        service_path='/news/{user_id}/',
        response_model=List[New],
        status_code=200,
        method='GET',
        path_params={'user_id': int},
        responses={
            200: {'description': 'List of news for user.'},
        }
    ),
    'get_users': PathInfo(
        path='/users/',
        service_path='/users/',
        response_model=List[User],
        status_code=200,
        method='GET',
        responses={
            200: {'description': 'List of users.'},
        }
    ),
    'get_user': PathInfo(
        path='/users/{id}/',
        service_path='/users/{id}/',
        response_model=User,
        status_code=200,
        method='GET',
        path_params={'id': int},
        responses={
            200: {'description': 'User.'},
            404: {'description': 'User not found.'}
        }
    ),
    'add_hobby': PathInfo(
        path='/users/hobbies/{id}/',
        service_path='/users/hobbies/{id}/',
        response_model=UserHobby,
        status_code=200,
        method='PUT',
        path_params={'id': int},
        authorized=True,
        responses={
            200: {'description': 'Hobby added.'},
            400: {'description': 'Already added.'},
        }
    ),
    'remove_hobby': PathInfo(
        path='/users/hobbies/{id}/',
        service_path='/users/hobbies/{id}/',
        method='DELETE',
        path_params={'id': int},
        authorized=True,
        responses={
            204: {'description': 'Hobby removed.'},
        }
    )
}

for name, path_info in MAPPING.items():
    handler = generate_handler(name, path_info, router)
    endpoints.append(handler)


# todo: rewrite universal
@router.websocket('/news/ws')
async def feed_websocket_proxy(client_ws: WebSocket):
    host, port = settings.MONOLITH.HOST, settings.MONOLITH.PORT
    uri = f'ws://{host}:{port}/news/ws'
    await client_ws.accept()
    msg = await client_ws.receive_text()
    async with websockets.connect(uri) as server_ws:
        await server_ws.send(msg)
        while True:
            msg = await server_ws.recv()
            await client_ws.send_text(msg)
