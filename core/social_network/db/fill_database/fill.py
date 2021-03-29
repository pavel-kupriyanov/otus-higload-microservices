import asyncio
import copy
import random
import string
import itertools
from functools import lru_cache
from typing import Tuple, Union, Any, List, Iterator

from social_network.db.managers import AuthUserManager
from social_network.db.models import Gender
from social_network.db.db import DatabaseConnector

from social_network.utils.security import hash_password
from social_network.settings import settings, Settings

from social_network.db.fill_database.data import (
    POPULAR_FIRST_NAMES,
    COMMON_FIRST_NAMES,
    UNCOMMON_FIRST_NAMES,
    POPULAR_LAST_NAMES,
    COMMON_LAST_NAMES,
    UNCOMMON_LAST_NAMES,
    CITIES
)


@lru_cache()
def get_password_and_salt(password='secret_password'):
    return hash_password(password)


def random_str(n: int) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))


def generate_email() -> str:
    name, domain = random_str(13), random_str(4)
    return f'{name}@{domain}.com'


def prepare_sequence(seq: List[Any]) -> Iterator[Any]:
    copy_seq = copy.copy(seq)
    random.shuffle(copy_seq)
    return itertools.cycle(copy_seq)


def get_raw_user(first_name: str, last_name: str, city: str) \
        -> Tuple[Union[str, int], ...]:
    email = generate_email()
    hashed_password, salt = get_password_and_salt()
    age = random.randint(18, 60)
    gender = Gender.MALE
    return (email, hashed_password, salt, age, first_name, last_name,
            city, gender)


def get_raw_users(first_names: Iterator[str], last_names: Iterator[str],
                  cities: Iterator[str], count: int) -> List:
    users = []
    for first_name, last_name, city in zip(first_names, last_names, cities):
        users.append(get_raw_user(first_name, last_name, city))
        if len(users) >= count:
            break
    return users


async def fill_db(conf: Settings, count: int = 1000, batch_size: int = 100):
    connector = DatabaseConnector(conf.DATABASE.MASTER)
    await connector.start()
    user_manager = AuthUserManager(connector, conf=settings)
    first_names = prepare_sequence(
        list(POPULAR_FIRST_NAMES * 10 +
             COMMON_FIRST_NAMES * 5 +
             UNCOMMON_FIRST_NAMES)
    )
    last_names = prepare_sequence(
        list(POPULAR_LAST_NAMES * 10 +
             COMMON_LAST_NAMES * 5 +
             UNCOMMON_LAST_NAMES)
    )
    cities = prepare_sequence(
        list(itertools.chain(
            *[[name] * weight for name, weight in CITIES.items()]
        )))
    counter = 0
    for i in range(count // batch_size):
        users = get_raw_users(first_names, last_names, cities, batch_size)
        await user_manager.bulk_create(tuple(users))
        counter += len(users)
        print(f'{counter} users created.')


def main(conf: Settings):
    asyncio.run(fill_db(conf, 1000000, 100000))


if __name__ == '__main__':
    main(settings)
