from functools import lru_cache
from datetime import datetime, timedelta
from random import choice
from string import ascii_letters, digits

from fastapi import FastAPI, Request, Depends, HTTPException

from pydantic import BaseModel

from social_network_auth.settings import settings
from social_network_auth.db.models import AccessToken
from social_network_auth.db.connectors_storage import ConnectorsStorage
from social_network_auth.db.managers import AccessTokenManager
from social_network_auth.db.exceptions import RowsNotFoundError

app = FastAPI()


@app.on_event('startup')
async def startup():
    storage = ConnectorsStorage()
    await storage.create_connector(settings.DATABASE.MASTER)

    for conf in settings.DATABASE.SLAVES:
        await storage.create_connector(conf)
    app.state.storage = storage


def get_connector_storage(request: Request) -> ConnectorsStorage:
    return request.app.state.storage


@lru_cache(1)
def get_access_token_manager(storage=Depends(get_connector_storage)) \
        -> AccessTokenManager:
    return AccessTokenManager(storage, settings)


def generate_token_value(length=255) -> str:
    alphabet = ascii_letters + digits
    return ''.join((choice(alphabet) for _ in range(length)))


class TokenPayload(BaseModel):
    value: str


@app.post(
    '/tokens/{user_id}/',
    status_code=201,
    response_model=AccessToken,
    responses={
        201: {'description': 'Success login'},
        400: {'description': 'Invalid email or password'}
    })
async def create_token(
        user_id: int,
        manager: AccessTokenManager = Depends(get_access_token_manager)
) -> AccessToken:
    expired_at = datetime.now() + timedelta(
        seconds=settings.TOKEN_EXPIRATION_TIME
    )
    tokens = await manager.list_user_active(user_id)
    if not tokens:
        return await manager.create(
            user_id=user_id,
            expired_at=expired_at,
            value=generate_token_value()
        )
    return await manager.update(
        token_id=tokens[0].id,
        new_expired_at=expired_at
    )


@app.put(
    '/tokens/',
    status_code=200,
    responses={
        200: {'description': 'Correct token'},
        400: {'description': 'Expired token'},
        401: {'description': 'Invalid token'},
    })
async def check_token(
        payload: TokenPayload,
        manager: AccessTokenManager = Depends(get_access_token_manager)
):
    try:
        access_token = await manager.get_by_value(payload.value)
    except RowsNotFoundError:
        raise HTTPException(status_code=401, detail='Invalid token')
    if datetime.fromtimestamp(access_token.expired_at) < datetime.now():
        raise HTTPException(status_code=400, detail='Expired token')
