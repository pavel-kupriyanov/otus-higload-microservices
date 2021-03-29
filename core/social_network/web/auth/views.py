from pydantic import BaseModel
from fastapi import (
    APIRouter,
    Depends,
    status,
    HTTPException
)
from fastapi_utils.cbv import cbv
from httpx import AsyncClient

from social_network.settings import settings
from social_network.db.models import AuthUser, Timestamp
from social_network.db.managers import (
    AuthUserManager,
    AccessTokenManager
)
from social_network.db.exceptions import RowsNotFoundError
from social_network.utils.security import hash_password

from .utils import is_valid_password

from .models import (
    LoginPayload,
    RegistrationPayload
)

from ..depends import (
    get_access_token_manager,
    get_auth_user_manager
)


class AccessToken(BaseModel):
    id: int
    value: str
    user_id: int
    expired_at: Timestamp


router = APIRouter()


@cbv(router)
class AuthViewSet:
    user_manager: AuthUserManager = Depends(get_auth_user_manager)
    access_token_manager: AccessTokenManager = Depends(
        get_access_token_manager
    )

    @router.post('/login/', status_code=201, response_model=AccessToken,
                 responses={
                     201: {'description': 'Success login'},
                     400: {'description': 'Invalid email or password'}
                 })
    async def login(self, p: LoginPayload) -> AccessToken:
        user = await self.user_manager.get_by_email(email=p.email)
        if not is_valid_password(user, p.password.get_secret_value()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid email or password'
            )

        return await self.create_token(user.id)

    @router.post('/register/', status_code=201, response_model=AuthUser,
                 responses={
                     201: {'description': 'User created'},
                     400: {'description': 'Invalid email'}
                 })
    async def register(self, p: RegistrationPayload) -> AuthUser:
        try:
            await self.user_manager.get_by_email(p.email)
        except RowsNotFoundError:
            pass
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='User with this email already exists'
            )

        hashed_password, salt = hash_password(p.password.get_secret_value())
        return await self.user_manager.create(email=p.email,
                                              hashed_password=hashed_password,
                                              salt=salt,
                                              age=p.age,
                                              first_name=p.first_name,
                                              last_name=p.last_name,
                                              city=p.city,
                                              gender=p.gender)

    @staticmethod
    async def create_token(user_id: int) -> AccessToken:
        auth_conf = settings.AuthServiceSettings
        url = f'http://{auth_conf.HOST}:{auth_conf.PORT}'
        async with AsyncClient(base_url=url) as client:
            response = await client.post(f'/tokens/{user_id}/')
        return AccessToken(**response.json())
