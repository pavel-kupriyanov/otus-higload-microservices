from collections import defaultdict
from typing import List, Dict
from itertools import groupby

from ..crud import CRUDManager
from ..models import Hobby, UserHobby

DROP_USER_HOBBY = '''
        DELETE FROM users_hobbies_mtm
        WHERE user_id = %s AND hobby_id = %s;
    '''

GET_HOBBIES_FOR_USERS = '''
        SELECT user_id, h.id, h.name from users_hobbies_mtm
        JOIN hobbies h on h.id = users_hobbies_mtm.hobby_id
        WHERE user_id IN %s
        ORDER BY user_id;
    '''


class UsersHobbyManager(CRUDManager):
    model = UserHobby
    queries = {}

    async def create(self, user_id: int, hobby_id: int) -> UserHobby:
        return await self._create((user_id, hobby_id))

    async def delete_by_id(self, user_id: int, hobby_id: int):
        params = (user_id, hobby_id)
        return await self.execute(DROP_USER_HOBBY, params,
                                  raise_if_empty=False)

    async def get_hobby_for_users(self, user_ids: List[int]) \
            -> Dict[int, List[Hobby]]:
        params = (user_ids,)
        results = await self.execute(GET_HOBBIES_FOR_USERS, params,
                                     read_only=True, raise_if_empty=False)
        parsed_result: Dict[int, List[Hobby]] = defaultdict(list)
        for key, group in groupby(results, lambda x: x[0]):
            for item in group:
                parsed_result[key].append(Hobby(id=item[1], name=item[2]))
        return parsed_result
