from uuid import uuid4
from json import loads
from enum import Enum
from datetime import datetime
from typing import Optional, List, Union, Dict, Type, TypeVar

from pydantic import (
    Field,
    EmailStr,
    SecretStr,
    validator,
    BaseModel as PydanticBaseModel
)

from .base import BaseModel, Timestamp
from ..settings import DatabaseSettings


class FriendRequestStatus(str, Enum):
    WAITING = 'WAITING'
    DECLINED = 'DECLINED'


class FriendRequest(BaseModel):
    _table_name = 'friend_requests'
    _fields = ('id', 'from_user', 'to_user', 'status')

    from_user: int
    to_user: int
    status: FriendRequestStatus


class Friendship(BaseModel):
    _table_name = 'friendships'
    _fields = ('id', 'user_id', 'friend_id')

    user_id: int
    friend_id: int


class Hobby(BaseModel):
    _table_name = 'hobbies'
    _fields = ('id', 'name')

    name: str


TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'


class AccessToken(BaseModel):
    _table_name = 'access_tokens'
    _fields = ('id', 'value', 'user_id', 'expired_at')
    _datetime_fields = ('expired_at',)

    value: str
    user_id: int
    expired_at: Timestamp


class Gender(str, Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    OTHER = 'OTHER'


class ShortUserInfo(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str]


class User(BaseModel):
    _table_name = 'users'
    _fields = ('id', 'first_name', 'last_name', 'age', 'city', 'gender')

    first_name: str
    last_name: Optional[str]
    city: Optional[str]
    gender: Optional[Gender]
    age: int = Field(..., ge=1, le=200)
    hobbies: List[Hobby] = Field(default_factory=list)

    def get_short(self) -> ShortUserInfo:
        return ShortUserInfo(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name
        )


class AuthUser(User):
    _table_name = 'users'
    _fields = ('id', 'email', 'password', 'salt', 'age', 'first_name',
               'last_name', 'city', 'gender')

    email: EmailStr
    password: SecretStr
    salt: SecretStr


class UserHobby(BaseModel):
    _table_name = 'users_hobbies_mtm'
    _fields = ('id', 'user_id', 'hobby_id')

    user_id: int
    hobby_id: int


class DatabaseInfo(BaseModel):
    _table_name = 'database_info'
    _fields = ('id', 'host', 'port', 'user', 'password', 'name')

    host: str
    port: int
    user: str
    password: SecretStr
    name: str

    def as_settings(self) -> DatabaseSettings:
        return DatabaseSettings(
            HOST=self.host,
            PORT=self.port,
            USER=self.user,
            PASSWORD=self.password.get_secret_value(),
            NAME=self.name
        )


class ShardState(str, Enum):
    READY = 'READY'
    ADDING = 'ADDING'
    ERROR = 'ERROR'


class Shard(BaseModel):
    _table_name = 'shards_info'
    _fields = ('id', 'db_info', 'shard_table', 'shard_key', 'state')

    db_info: DatabaseInfo
    shard_table: str
    shard_key: int
    state: ShardState


class NewsType(str, Enum):
    ADDED_FRIEND = 'ADDED_FRIEND'
    ADDED_HOBBY = 'ADDED_HOBBY'
    ADDED_POST = 'ADDED_POST'


class Payload(PydanticBaseModel):
    author: Union[ShortUserInfo, int]


class AddedFriendNewPayload(Payload):
    """
    Model for fast displaying on frontend - no need additional queries
    """
    new_friend: Union[ShortUserInfo, int]


class AddedHobbyNewPayload(Payload):
    """
    Same as AddedFriendNewPayload for hobby
    """
    hobby: Union[Hobby, int]


class AddedPostNewPayload(Payload):
    text: str


N = TypeVar('N', bound='New')


class New(BaseModel):
    _table_name = 'news'
    _fields = ('id', 'author_id', 'type', 'payload', 'created')
    _datetime_fields = ('created',)
    _payload_mapping: Dict[NewsType, Type[Payload]] = {
        NewsType.ADDED_POST: AddedPostNewPayload,
        NewsType.ADDED_HOBBY: AddedHobbyNewPayload,
        NewsType.ADDED_FRIEND: AddedFriendNewPayload
    }
    _reversed_payload_mapping: Dict[Type[Payload], NewsType] = {
        v: k for k, v in _payload_mapping.items()
    }

    id: str
    author_id: int
    type: NewsType
    payload: Union[
        AddedPostNewPayload,
        AddedHobbyNewPayload,
        AddedFriendNewPayload
    ]
    created: Timestamp
    # non-db fields
    populated: bool = False
    stored: bool = False

    @validator('payload', pre=True)
    def json_tod_dict(cls, v):
        if isinstance(v, str):
            return loads(v)
        return v

    @classmethod
    def from_payload(cls: Type[N], payload: Payload) -> N:
        author_id = payload.author
        if not isinstance(author_id, int):
            author_id = author_id.id
        return cls(
            id=str(uuid4()),
            author_id=author_id,
            type=cls._reversed_payload_mapping[type(payload)],
            payload=payload,
            created=datetime.now().timestamp(),
        )
