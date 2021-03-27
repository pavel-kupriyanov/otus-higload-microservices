from typing import Optional
from dataclasses import dataclass

from pydantic import BaseModel
from fastapi import Query

from social_network.settings import settings


class MessageCreatePayload(BaseModel):
    to_user_id: int
    text: str


@dataclass
class MessageQueryParams:
    to_user_id: int
    after_timestamp: float = Query(0)
    page: int = Query(1, ge=1)
    paginate_by: int = Query(settings.BASE_PAGE_LIMIT,
                             le=settings.BASE_PAGE_LIMIT)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.paginate_by
