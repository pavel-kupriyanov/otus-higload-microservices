from enum import Enum
from functools import wraps

from fastapi import HTTPException


class Order(str, Enum):
    DESC = 'DESC'
    ASC = 'ASC'


def authorize_only(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        u_id, u = getattr(self, 'user_id', None), getattr(self, 'user_', None)
        if not (u_id or u):
            raise HTTPException(401, detail='Authorized user only.')
        return await func(self, *args, **kwargs)

    return wrapper
