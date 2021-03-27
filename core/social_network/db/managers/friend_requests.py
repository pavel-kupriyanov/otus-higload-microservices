from typing import List

from ..crud import CRUDManager

from ..models import FriendRequest, FriendRequestStatus

UPDATE_FRIEND_REQUEST = '''
        UPDATE friend_requests
        SET status = %s
        WHERE id = %s
    '''

GET_FRIEND_REQUESTS = '''
        SELECT id, from_user, to_user, status FROM friend_requests
        WHERE from_user = %s OR to_user = %s
    '''

GET_NON_STATUS_FRIEND_REQUESTS = '''
        SELECT (id, from_user, to_user, status) FROM friend_requests
        WHERE (from_user = %s OR to_user = %s) AND status != %s
    '''

GET_FRIEND_REQUEST_BY_USERS = '''
    SELECT (id, from_user, to_user, status) FROM friend_requests
    WHERE from_user = %s AND to_user = %s
    '''


class FriendRequestManager(CRUDManager):
    model = FriendRequest

    async def create(self, from_user: int, to_user: int,
                     base_status=FriendRequestStatus.WAITING) \
            -> FriendRequest:
        return await self._create((from_user, to_user, base_status))

    async def update(self, id: int, status: FriendRequestStatus) \
            -> FriendRequest:
        return await self._update(id, (status, id), UPDATE_FRIEND_REQUEST)

    async def list_for_user_exclude_status(self, user_id: int,
                                           status: FriendRequestStatus) \
            -> List[FriendRequest]:
        return await self._list((user_id, user_id, status),
                                GET_NON_STATUS_FRIEND_REQUESTS)

    async def list_for_user(self, user_id: int) -> List[FriendRequest]:
        return await self._list((user_id, user_id), GET_FRIEND_REQUESTS)
