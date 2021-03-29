from json import dumps

from aio_pika import Message, Exchange

from .base import BaseRabbitMQ


class RabbitMQProducer(BaseRabbitMQ):
    exchange: Exchange

    async def send(self, data: dict, routing_key: str):
        await self.exchange.publish(
            Message(dumps(data).encode()),
            routing_key=routing_key
        )
