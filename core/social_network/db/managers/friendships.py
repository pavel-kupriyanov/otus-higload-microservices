from ..crud import CRUDManager
from ..models import Friendship

GET_FRIENDSHIP = '''
       SELECT id, user_id, friend_id FROM friendships
       WHERE user_id = %s AND friend_id = %s
   '''


class FriendshipManager(CRUDManager):
    model = Friendship
    queries = {}

    async def create(self, user_id: int, friend_id: int) -> Friendship:
        await self._create((friend_id, user_id))
        return await self._create((user_id, friend_id))

    async def get_by_participants(self, user_id: int, friend_id: int) \
            -> Friendship:
        friendships = await self.execute(GET_FRIENDSHIP, (user_id, friend_id),
                                         read_only=True)
        return Friendship.from_db(friendships[0])
