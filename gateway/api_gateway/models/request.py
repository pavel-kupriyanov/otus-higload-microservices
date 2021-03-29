from typing import Optional
from enum import Enum

from pydantic import (
    BaseModel,
    EmailStr,
    SecretStr,
    Field
)

from .response import Gender


class Order(str, Enum):
    DESC = 'DESC'
    ASC = 'ASC'


class LoginPayload(BaseModel):
    email: EmailStr
    password: SecretStr = Field(..., min_length=8, max_length=255)


class RegistrationPayload(BaseModel):
    email: EmailStr
    password: SecretStr = Field(..., min_length=8, max_length=255)
    first_name: str = Field(..., min_length=2, max_length=255)
    last_name: Optional[str] = Field(None, min_length=2, max_length=255)
    city: Optional[str] = Field(None, min_length=2, max_length=255)
    gender: Optional[Gender] = None
    age: int = Field(..., ge=1, le=200)


class HobbyCreatePayload(BaseModel):
    name: str


class MessageCreatePayload(BaseModel):
    to_user_id: int
    text: str


class NewCreatePayload(BaseModel):
    text: str
