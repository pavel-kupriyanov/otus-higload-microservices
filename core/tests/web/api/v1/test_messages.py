from time import sleep

import pytest
from fastapi.testclient import TestClient

from social_network.settings import DatabaseSettings
from social_network.db.models import AccessToken, User, ShardState
from social_network.services import DependencyInjector
from social_network.db.sharding.models import Message

BASE_PATH = '/messages/'

SHARD_0_CONF = DatabaseSettings(
    HOST="localhost",
    PORT=3370,
    USER="otus",
    PASSWORD="otus",
    NAME="otus"
)

SHARD_1_CONF = DatabaseSettings(
    HOST="localhost",
    PORT=3371,
    USER="otus",
    PASSWORD="otus",
    NAME="otus"
)


@pytest.fixture(name='message_shards')
async def add_message_shards_into_db(factory, cursor):
    db_0 = await factory.add_db(SHARD_0_CONF)
    db_1 = await factory.add_db(SHARD_1_CONF)
    await factory.add_shard(db_0, 'messages', 0, ShardState.READY)
    await factory.add_shard(db_1, 'messages', 1, ShardState.READY)
    yield
    await cursor.execute('DELETE FROM shards_info')
    await cursor.execute('DELETE FROM database_info')


@pytest.fixture(name='clear_messages_after')
async def clear_messages(injector: DependencyInjector):
    connector_0 = await injector.connectors_storage.get_connector(SHARD_0_CONF)
    connector_1 = await injector.connectors_storage.get_connector(SHARD_1_CONF)
    yield
    await connector_0.make_query('DELETE FROM messages', raise_if_empty=False)
    await connector_1.make_query('DELETE FROM messages', raise_if_empty=False)


@pytest.fixture(name='message1')
async def add_message_1(factory, user1, user2, message_shards,
                        clear_messages_after):
    return await factory.add_message(user1.id, user2.id, 'foo')


def test_create_message(app: TestClient, message_shards, token1: AccessToken,
                        user2: User):
    msg = {'to_user_id': user2.id, 'text': 'Hi!'}
    response = app.post(BASE_PATH, json=msg,
                        headers={'x-auth-token': token1.value})
    assert response.status_code == 201
    assert response.json()['text'] == msg['text']


def test_get_messages(app: TestClient, token1: AccessToken, message1: Message,
                      user2):
    response = app.get(BASE_PATH,
                       params={'to_user_id': user2.id},
                       headers={'x-auth-token': token1.value})
    assert response.status_code == 200
    msg = response.json()[0]
    assert msg['text'] == message1.text


def test_get_messages_from_timestamp(app: TestClient, token1: AccessToken,
                                     message1: Message, user2):
    sleep(2)  # sleep to get pause between 1 and 2 message
    msg = {'to_user_id': user2.id, 'text': 'Hi!'}
    headers = {'x-auth-token': token1.value}
    response = app.post(BASE_PATH, json=msg, headers=headers)
    timestamp = float(response.json()['created'])

    params = {'to_user_id': user2.id}
    response = app.get(BASE_PATH, params=params, headers=headers)
    assert len(response.json()) == 2

    params['after_timestamp'] = timestamp - 1
    response = app.get(BASE_PATH, params=params, headers=headers)
    assert len(response.json()) == 1
    assert response.json()[0]['text'] == msg['text']
