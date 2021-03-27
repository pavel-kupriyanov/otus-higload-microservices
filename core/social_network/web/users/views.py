from typing import List, Optional
from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from fastapi_utils.cbv import cbv

from social_network.db.models import (
    New,
    User,
    UserHobby,
    AddedHobbyNewPayload,
)
from social_network.db.managers import (
    UserManager,
    UsersHobbyManager
)
from social_network.db.exceptions import DatabaseError
from social_network.services.kafka import KafkaProducer, Topic

from .models import UsersQueryParams
from ..depends import (
    get_user,
    get_user_manager,
    get_user_hobby_manager,
    get_kafka_producer
)
from ..utils import authorize_only

router = APIRouter()


@cbv(router)
class UserViewSet:
    user_: Optional[User] = Depends(get_user)
    kafka_producer: KafkaProducer = Depends(get_kafka_producer)
    user_manager: UserManager = Depends(get_user_manager)
    user_hobby_manager: UsersHobbyManager = Depends(
        get_user_hobby_manager
    )

    @router.get('/', response_model=List[User], responses={
        200: {'description': 'List of users.'},
    })
    async def users(self, q: UsersQueryParams = Depends(UsersQueryParams)) \
            -> List[User]:
        users = await self.user_manager.list(first_name=q.first_name,
                                             last_name=q.last_name,
                                             friend_id=q.friends_of,
                                             ids=q.ids,
                                             order=q.order,
                                             order_by=q.order_by,
                                             limit=q.paginate_by,
                                             offset=q.offset)
        if not users:
            return []
        if q.with_hobbies:
            hobbies = await self.user_hobby_manager.get_hobby_for_users(
                [user.id for user in users]
            )
            for user in users:
                user.hobbies = hobbies[user.id]
        return users

    @router.get('/{id}/', response_model=User, responses={
        200: {'description': 'User.'},
        404: {'description': 'User not found.'}
    })
    async def user(self, id: int) -> User:
        user = await self.user_manager.get(id)
        hobbies = await self.user_hobby_manager.get_hobby_for_users(
            [user.id]
        )
        user.hobbies = hobbies[user.id]
        return user

    @router.put('/hobbies/{id}/', status_code=201, response_model=UserHobby,
                responses={
                    200: {'description': 'Hobby added.'},
                    400: {'description': 'Already added.'},
                })
    @authorize_only
    async def add_hobby(self, id: int) -> UserHobby:
        try:
            user_hobby = await self.user_hobby_manager.create(self.user_.id, id)

            new = self.prepare_new(user_hobby.hobby_id)
            await self.kafka_producer.send(new.json(), Topic.Populate)

            return user_hobby
        except DatabaseError:
            raise HTTPException(400, detail='Hobby not found or already added')

    @router.delete('/hobbies/{id}/', status_code=204, responses={
        204: {'description': 'Hobby removed.'},
    })
    @authorize_only
    async def remove_hobby(self, id: int):
        await self.user_hobby_manager.delete_by_id(self.user_.id, id)

    def prepare_new(self, hobby_id: int) -> New:
        payload = AddedHobbyNewPayload(
            author=self.user_.get_short(),
            hobby=hobby_id
        )
        return New.from_payload(payload)
