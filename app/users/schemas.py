from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from .models import UserType

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    hashed_password: str = Field(min_length=8)
    is_active: bool
    user_type: UserType
    first_name: str
    last_name: str
    phone: str
    gender: bool
    bio: str
    avatar_url: str
    language: str
    time_zone: str
    currency: str
    last_ip: str
    created_at: datetime
    updated_at: datetime
    created_by: str

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    is_active: bool | None = None
    user_type: UserType | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    gender: bool | None = None
    bio: str | None = None
    avatar_url: str | None = None
    language: str | None = None
    time_zone: str | None = None
    currency: str | None = None

    created_by: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    user_type: UserType
    first_name: str
    last_name: str
    phone: str
    gender: bool
    bio: str
    avatar_url: str
    language: str
    time_zone: str
    currency: str
    last_login_at: datetime
    last_ip: str
    created_at: datetime
    updated_at: datetime
    created_by: str

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class SetupPasswordRequest(BaseModel):
    token: str
    new_password: str