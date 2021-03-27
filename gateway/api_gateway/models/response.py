from enum import Enum
from typing import Optional, List, Union

from pydantic import (
    Field,
    EmailStr,
    SecretStr,
    BaseModel as PydanticModel
)

TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'
Timestamp = float  # Alias


class FriendRequestStatus(str, Enum):
    WAITING = 'WAITING'
    DECLINED = 'DECLINED'


class Gender(str, Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    OTHER = 'OTHER'


class BaseModel(PydanticModel):
    id: int


class FriendRequest(BaseModel):
    from_user: int
    to_user: int
    status: FriendRequestStatus


class Friendship(BaseModel):
    user_id: int
    friend_id: int


class Hobby(BaseModel):
    name: str


class AccessToken(BaseModel):
    value: str
    user_id: int
    expired_at: Timestamp


class ShortUserInfo(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str]


class User(BaseModel):
    first_name: str
    last_name: Optional[str]
    city: Optional[str]
    gender: Optional[Gender]
    age: int = Field(..., ge=1, le=200)
    hobbies: List[Hobby] = Field(default_factory=list)


class AuthUser(User):
    email: EmailStr
    password: SecretStr
    salt: SecretStr


class UserHobby(BaseModel):
    user_id: int
    hobby_id: int


class NewsType(str, Enum):
    ADDED_FRIEND = 'ADDED_FRIEND'
    ADDED_HOBBY = 'ADDED_HOBBY'
    ADDED_POST = 'ADDED_POST'


class Payload(PydanticModel):
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


class New(BaseModel):
    id: str
    author_id: int
    type: NewsType
    payload: Union[
        AddedPostNewPayload,
        AddedHobbyNewPayload,
        AddedFriendNewPayload
    ]
    created: Timestamp


class Message(BaseModel):
    id: str
    chat_key: str
    author_id: int
    text: str
    created: Timestamp
