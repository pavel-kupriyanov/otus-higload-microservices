from asyncio import get_running_loop

from aio_pika import Connection, Channel, connect_robust, Exchange

from social_network.settings import RabbitMQSettings

from ..base import BaseService


class BaseRabbitMQ(BaseService):
    connection: Connection
    channel: Channel
    exchange: Exchange

    def __init__(self, conf: RabbitMQSettings):
        self.conf = conf

    async def start(self):
        c = self.conf
        password = c.PASSWORD.get_secret_value()
        self.connection = await connect_robust(
            f'amqp://{c.USERNAME}:{password}@{c.HOST}:{c.PORT}/{c.PATH}',
            loop=get_running_loop()
        )
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.get_exchange(self.conf.EXCHANGE)

    async def close(self):
        await self.channel.close()
        await self.connection.close()
