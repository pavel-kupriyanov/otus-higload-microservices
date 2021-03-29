import asyncio

from social_network.db.managers import HobbiesManager
from social_network.db.db import DatabaseConnector

from social_network.settings import settings, Settings


class Counter:

    def __init__(self):
        self.counter = 0

    def inc(self):
        self.counter += 1


counter = Counter()


async def create_hobbies(conf: Settings, count: int = 1000, tasks: int = 10):
    connector = DatabaseConnector(conf.DATABASE.MASTER)
    await connector.start()
    manager = HobbiesManager(connector, conf=settings)
    counter = Counter()
    tasks = [create_hobbies_task(manager, i, counter, count // tasks)
             for i in range(tasks)]
    await asyncio.gather(*tasks)
    print('Final:', counter.counter)


async def create_hobbies_task(manager: HobbiesManager, num: int,
                              counter: Counter, count: int = 1000):
    try:
        for i in range(count):
            await manager.create(f'{num}:{i}')
            counter.inc()
    except:
        return


def main(conf: Settings):
    asyncio.run(create_hobbies(conf, 1000000, 10))


if __name__ == '__main__':
    main(settings)
