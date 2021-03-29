from typing import Optional

from pydantic import (
    BaseModel,
    EmailStr,
    SecretStr,
    Field
)

from social_network.db.models import Gender


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
