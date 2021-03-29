from aiokafka import AIOKafkaProducer

from social_network.settings import KafkaSettings

from .consts import Topic, Protocol
from .utils import prepare_ssl_context
from ..base import BaseService


class KafkaProducer(BaseService):
    producer: AIOKafkaProducer

    def __init__(self, conf: KafkaSettings):
        self.conf = conf

    async def start(self):
        protocol = Protocol.SSL if self.conf.USE_SSL else Protocol.PLAIN
        self.producer = AIOKafkaProducer(
            bootstrap_servers=f'{self.conf.HOST}:{self.conf.PORT}',
            security_protocol=protocol,
            ssl_context=prepare_ssl_context(self.conf),
        )
        await self.producer.start()

    async def close(self):
        await self.producer.stop()

    async def send(self, data: str, topic: str = Topic.News):
        await self.producer.send(topic, data.encode())
