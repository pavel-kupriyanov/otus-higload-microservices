from typing import Optional, List
from fastapi import (
    APIRouter,
    Depends,
)
from fastapi_utils.cbv import cbv

from social_network.db.models import Hobby
from social_network.db.managers import HobbiesManager
from social_network.db.exceptions import DatabaseError

from ..depends import (
    get_user_id,
    get_hobby_manager
)
from .models import HobbyCreatePayload, HobbyQueryParams

from ..utils import authorize_only

router = APIRouter()


@cbv(router)
class HobbiesViewSet:
    user_id: Optional[int] = Depends(get_user_id)
    hobby_manager: HobbiesManager = Depends(get_hobby_manager)

    @router.post('/', response_model=Hobby, status_code=201,
                 responses={
                     201: {'description': 'Hobby created.'},
                     401: {'description': 'Unauthorized.'},
                 })
    @authorize_only
    async def create(self, p: HobbyCreatePayload) -> Hobby:
        try:
            return await self.hobby_manager.create(p.name)
        except DatabaseError:
            return await self.hobby_manager.get_by_name(p.name)

    @router.get('/{id}/', responses={
        200: {'description': 'Success'},
        404: {'description': 'Hobby not found.'}
    })
    async def get(self, id: int) -> Hobby:
        return await self.hobby_manager.get(id)

    @router.get('/', response_model=List[Hobby], responses={
        200: {'description': 'List of hobbies.'},
    })
    async def list(self, q: HobbyQueryParams = Depends(HobbyQueryParams)) \
            -> List[Hobby]:
        return await self.hobby_manager.list(name=q.name,
                                             order=q.order,
                                             limit=q.paginate_by,
                                             offset=q.offset)
