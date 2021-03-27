from dataclasses import dataclass
from pydantic import BaseModel

from fastapi import Query

from social_network.settings import settings

from ..utils import Order


class HobbyCreatePayload(BaseModel):
    name: str


@dataclass
class HobbyQueryParams:
    name: str = Query('')
    order: Order = Query(Order.ASC)
    page: int = Query(1, ge=1)
    paginate_by: int = Query(settings.BASE_PAGE_LIMIT,
                             le=settings.BASE_PAGE_LIMIT)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.paginate_by
