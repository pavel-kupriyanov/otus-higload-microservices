from uuid import uuid4
from json import loads
from asyncio import create_task
from typing import Callable, Coroutine

from aio_pika import IncomingMessage, Queue

from social_network.settings import RabbitMQSettings

from .base import BaseRabbitMQ

Callback = Callable[[dict], Coroutine]


class FeedConsumer(BaseRabbitMQ):
    prefetch_count = 1000
    callback: Callback
    queue: Queue

    def __init__(self, conf: RabbitMQSettings, callback: Callback, key: str):
        super().__init__(conf)
        self.callback = callback
        self.routing_key = key
        self.queue_name = 'feed-' + str(uuid4())
        self.task = None

    async def start(self):
        await super().start()
        await self.channel.set_qos(prefetch_count=100)
        self.queue = await self.channel.declare_queue(
            self.queue_name,
            auto_delete=True
        )
        await self.queue.bind(self.exchange, routing_key=self.routing_key)
        self.task = create_task(self.queue.consume(self.process_message))

    async def close(self):
        await super().close()
        await self.queue.delete()
        self.task.cancel()

    async def process_message(self, message: IncomingMessage):
        async with message.process():
            await self.callback(loads(message.body.decode()))
