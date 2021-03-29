from enum import Enum
from functools import wraps
from datetime import datetime, timedelta

from fastapi import HTTPException

from social_network.settings import NewsCacheSettings
from social_network.db.managers import NewsManager
from social_network.db.models import TIMESTAMP_FORMAT
from social_network.services.kafka.producer import KafkaProducer


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


async def warmup_news(conf: NewsCacheSettings,
                      news_manager: NewsManager,
                      producer: KafkaProducer):
    timestamp = datetime.now() - timedelta(seconds=conf.WARMUP_CACHE_PERIOD)
    timestamp = timestamp.strftime(TIMESTAMP_FORMAT)
    news = await news_manager.list_after_timestamp(timestamp)
    for new in news:
        new.populated, new.stored = True, True
        await producer.send(new.json())
