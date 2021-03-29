from .producer import KafkaProducer
from .consumers import (
    NewsDatabaseConsumer,
    PopulateNewsConsumer,
    NewsCacheConsumer
)
from .service import KafkaConsumersService
from .consts import Topic
