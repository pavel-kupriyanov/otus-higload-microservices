from typing import List
from fastapi import APIRouter, Request
from fastapi.responses import Response

import httpx

from api_gateway.settings import settings
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

router = APIRouter()
endpoints = []

MAPPING = {
    'login': PathInfo(
        path='/auth/login/',
        service_path='/api/v1/auth/login/',
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
        service_path='/api/v1/auth/register/',
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
        service_path='/api/v1/friendships/{user_id}/',
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
        service_path='/api/v1/friendships/{id}/',
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
        service_path='/api/v1/friendships/{id}/',
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
        service_path='/api/v1/friendships/decline/{id}/',
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
        service_path='/api/v1/friendships/accept/{id}/',
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
        service_path='/api/v1/friendships/friendship/{friend_id}/',
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
        service_path='/api/v1/friendships/',
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
        service_path='/api/v1/hobbies/',
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
        service_path='/api/v1/hobbies/{id}/',
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
        service_path='/api/v1/hobbies/',
        response_model=List[Hobby],
        status_code=200,
        method='GET',
        responses={
            200: {'description': 'List of hobbies.'},
        }
    ),
    'create_message': PathInfo(
        path='/messages/',
        service_path='/api/v1/messages/',
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
        service_path='/api/v1/messages/',
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
        service_path='/api/v1/news/',
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
        service_path='/api/v1/news/feed/',
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
        service_path='/api/v1/news/{user_id}/',
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
        service_path='/api/v1/users/',
        response_model=List[User],
        status_code=200,
        method='GET',
        responses={
            200: {'description': 'List of users.'},
        }
    ),
    'get_user': PathInfo(
        path='/users/{id}/',
        service_path='/api/v1/users/{id}/',
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
        service_path='/api/v1/users/hobbies/{id}/',
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
        service_path='/api/v1/users/hobbies/{id}/',
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


@router.get('{path:path}')
async def gateway(path: str, request: Request):
    monolith = settings.MONOLITH
    response = httpx.request(
        url=f'http://{monolith.HOST}:{monolith.PORT}{request.url.path}',
        method=request.method,
        params=request.query_params,
        content=await request.body(),
        headers=[(k, v) for k, v in request.headers.items()]
    )
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers
    )
