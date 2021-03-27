from async_lru import alru_cache
from datetime import datetime
from typing import List

from ..crud import CRUDManager
from ..models import AccessToken, TIMESTAMP_FORMAT

GET_USER_ACTIVE_TOKENS = '''
        SELECT id, value, user_id, expired_at FROM access_tokens
        WHERE user_id = %s and expired_at > NOW()
    '''

UPDATE_TOKEN = '''
        UPDATE access_tokens
        SET expired_at = %s
        WHERE id = %s
    '''

GET_TOKEN_BY_VALUE = '''
        SELECT id, value, user_id, expired_at FROM access_tokens
        WHERE value = %s
    '''


class AccessTokenManager(CRUDManager):
    model = AccessToken

    async def create(self, value: str, user_id: int, expired_at: datetime) \
            -> AccessToken:
        params = (value, user_id, expired_at.strftime(TIMESTAMP_FORMAT))
        return await self._create(params)

    async def update(self, token_id: int, new_expired_at: datetime) \
            -> AccessToken:
        params = (new_expired_at.strftime(TIMESTAMP_FORMAT), token_id)
        return await self._update(token_id, params, UPDATE_TOKEN)

    async def list_user_active(self, user_id: int) -> List[AccessToken]:
        return await self._list((user_id,), GET_USER_ACTIVE_TOKENS)

    # todo: rewrite on redis cache  - this way insecure
    @alru_cache(maxsize=1000)
    async def get_by_value(self, value: str) -> AccessToken:
        tokens = await self.execute(GET_TOKEN_BY_VALUE, (value,),
                                    read_only=True)
        return AccessToken.from_db(tokens[0])
