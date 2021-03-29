from typing import List, Type

from social_network.settings import KafkaSettings, NewsCacheSettings
from social_network.db.connectors_storage import ConnectorsStorage

from .producer import KafkaProducer
from .consumers import (
    BaseKafkaConsumer,
    NewsDatabaseConsumer,
    NewsCacheAndRabbitConsumer,
    PopulateNewsConsumer
)
from ..redis import RedisService
from ..rabbitmq import RabbitMQProducer
from ..base import BaseService, BaseController


class KafkaConsumersService(BaseController):
    conf: KafkaSettings
    connectors_storage: ConnectorsStorage
    redis_service: RedisService
    kafka_producer: KafkaProducer
    rabbit_producer: RabbitMQProducer
    consumer_classes: List[Type[BaseKafkaConsumer]]
    consumers: List[BaseKafkaConsumer]

    def __init__(self,
                 conf: KafkaSettings,
                 news_conf: NewsCacheSettings,
                 kafka_producer: KafkaProducer,
                 rabbit_producer: RabbitMQProducer,
                 connectors_storage: ConnectorsStorage,
                 redis_service: RedisService):
        self.conf = conf
        self.news_conf = news_conf
        self.kafka_producer = kafka_producer
        self.rabbit_producer = rabbit_producer
        self.connectors_storage = connectors_storage
        self.redis_service = redis_service

        self.db_consumer = NewsDatabaseConsumer(conf, connectors_storage)
        self.cache_consumer = NewsCacheAndRabbitConsumer(conf, self.news_conf,
                                                         connectors_storage,
                                                         self.redis_service,
                                                         self.rabbit_producer)
        self.populate_consumer = PopulateNewsConsumer(
            conf, connectors_storage, kafka_producer
        )

    @property
    def services(self) -> List[BaseService]:
        return [
            self.db_consumer,
            self.cache_consumer,
            self.populate_consumer
        ]
