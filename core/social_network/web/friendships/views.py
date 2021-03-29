from typing import Optional, List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from fastapi_utils.cbv import cbv

from social_network.db.models import (
    New,
    User,
    Friendship,
    FriendRequestStatus,
    FriendRequest,
    AddedFriendNewPayload
)
from social_network.db.managers import (
    FriendRequestManager,
    FriendshipManager
)
from social_network.db.exceptions import (
    DatabaseError,
    RowsNotFoundError
)
from social_network.services.kafka import KafkaProducer, Topic

from ..depends import (
    get_user,
    get_kafka_producer,
    get_friend_request_manager,
)

from ..depends import get_friendship_manager
from ..utils import authorize_only

router = APIRouter()


@cbv(router)
class FriendRequestViewSet:
    user_: Optional[User] = Depends(get_user)
    kafka_producer: KafkaProducer = Depends(get_kafka_producer)
    friend_request_manager: FriendRequestManager = Depends(
        get_friend_request_manager
    )
    friendship_manager: FriendshipManager = Depends(
        get_friendship_manager
    )

    @router.post('/{user_id}/', response_model=FriendRequest, status_code=201,
                 responses={
                     201: {'description': 'Friend request created.'},
                     400: {'description': 'Already friends.'},
                     401: {'description': 'Unauthorized.'},
                     404: {'description': 'User not found.'}
                 })
    @authorize_only
    async def create(self, user_id: int) -> FriendRequest:
        try:
            await self.friendship_manager \
                .get_by_participants(self.user_.id, user_id)
        except RowsNotFoundError:
            pass
        else:
            raise HTTPException(400, detail='Users already friends.')

        try:
            return await self.friend_request_manager \
                .create(self.user_.id, user_id)
        except DatabaseError:
            raise HTTPException(404, detail='User not found or request '
                                            'already exists.')

    @router.delete('/{id}/', status_code=204, responses={
        204: {'description': 'Friend request cancelled.'},
        401: {'description': 'Unauthorized.'},
        403: {'description': 'Only request owner can cancel it'},
        404: {'description': 'Request not found.'}
    })
    @authorize_only
    async def cancel(self, id: int):
        request = await self.friend_request_manager.get(id)
        if not is_request_creator(request, self.user_.id):
            raise HTTPException(403, detail='You are not allowed to delete'
                                            ' request')
        await self.friend_request_manager.delete(id)

    @router.get('/{id}/', status_code=200, responses={
        200: {'description': 'Success'},
        401: {'description': 'Unauthorized.'},
        403: {'description': 'Only participants can get it'},
        404: {'description': 'Request not found.'}
    })
    @authorize_only
    async def get(self, id: int) -> FriendRequest:
        request = await self.friend_request_manager.get(id)
        if not is_request_participant(request, self.user_.id):
            raise HTTPException(403, detail='Not allowed')
        return request

    @router.put('/decline/{id}/', status_code=204, responses={
        204: {'description': 'Success'},
        401: {'description': 'Unauthorized.'},
        403: {'description': 'Only request target can decline it'},
        404: {'description': 'Request not found.'}
    })
    @authorize_only
    async def decline(self, id: int):
        request = await self.friend_request_manager.get(id)
        if not is_request_target(request, self.user_.id):
            raise HTTPException(403, 'Not allowed')
        await self.friend_request_manager.update(id,
                                                 FriendRequestStatus.DECLINED)

    @router.put('/accept/{id}/', response_model=Friendship,
                status_code=201,
                responses={
                    201: {'description': 'Success'},
                    401: {'description': 'Unauthorized.'},
                    403: {'description': 'Only request target can accept it'},
                    404: {'description': 'Request not found.'}
                })
    @authorize_only
    async def accept(self, id: int) -> Friendship:
        request = await self.friend_request_manager.get(id)

        if not is_request_target(request, self.user_.id):
            raise HTTPException(403, detail='Not allowed')

        await self.friend_request_manager.delete(id)
        friendship = await self.friendship_manager.create(request.to_user,
                                                          request.from_user)

        author, friend = request.from_user, request.to_user

        for pair in ((author, friend), (friend, author)):
            payload = AddedFriendNewPayload(author=pair[0], new_friend=pair[1])
            new = New.from_payload(payload)
            await self.kafka_producer.send(new.json(), Topic.Populate)

        return friendship

    @router.delete('/friendship/{friend_id}/', status_code=204, responses={
        204: {'description': 'Friendship cancelled.'},
        401: {'description': 'Unauthorized.'},
    })
    @authorize_only
    async def delete_friendship(self, friend_id: int):
        friendship = await self.friendship_manager.get_by_participants(
            self.user_.id, friend_id)
        try:
            reverse_friendship = await self.friendship_manager \
                .get_by_participants(friend_id, self.user_.id)
            await self.friendship_manager.delete(reverse_friendship.id)
        except RowsNotFoundError:
            pass
        await self.friendship_manager.delete(friendship.id)

    @router.get('/', status_code=200, responses={
        200: {'description': 'List of friend requests'},
    })
    @authorize_only
    async def list(self) -> List[FriendRequest]:
        return await self.friend_request_manager.list_for_user(self.user_.id)


def is_request_creator(request: FriendRequest, user_id: int) -> bool:
    return request.from_user == user_id


def is_request_target(request: FriendRequest, user_id: int) -> bool:
    return request.to_user == user_id


def is_request_participant(request: FriendRequest, user_id: int) -> bool:
    return user_id in (request.from_user, request.to_user)
