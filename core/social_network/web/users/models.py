from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

from fastapi import Query

from social_network.settings import settings
from ..utils import Order


class OrderBy(str, Enum):
    ID = 'id'
    FIRST_NAME = 'first_name'
    LAST_NAME = 'last_name'


@dataclass
class UsersQueryParams:
    order: Order = Query(Order.ASC)
    page: int = Query(1, ge=1)
    paginate_by: int = Query(settings.BASE_PAGE_LIMIT,
                             le=settings.BASE_PAGE_LIMIT)
    first_name: str = Query('')
    last_name: str = Query('')
    friends_of: Optional[int] = Query(None)
    ids: Optional[List[int]] = Query(None)
    order_by: OrderBy = Query(OrderBy.FIRST_NAME)
    with_hobbies: bool = Query(True)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.paginate_by
