from typing import List

from social_network.settings import settings

from ..crud import CRUDManager

from ..models import Hobby

GET_HOBBY_BY_NAME = '''
        SELECT id, name FROM hobbies
        WHERE (UPPER(name) = UPPER(%s));
'''

GET_HOBBIES = '''
         SELECT id, name FROM hobbies
         WHERE (UPPER(name) LIKE UPPER(CONCAT('%%', %s, '%%')))
    '''


class HobbiesManager(CRUDManager):
    model = Hobby

    async def get_by_name(self, name: str) -> Hobby:
        hobbies = await self.execute(GET_HOBBY_BY_NAME, (name,), read_only=True)
        return self.model.from_db(hobbies[0])

    async def create(self, name: str) -> Hobby:
        return await self._create((name.capitalize(),))

    async def list(self,
                   name='',
                   order='ASC',
                   limit=settings.BASE_PAGE_LIMIT,
                   offset=0) -> List[Hobby]:
        return await self._list((name,), order=order, limit=limit,
                                offset=offset, query=GET_HOBBIES)
