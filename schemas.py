from pydantic import BaseModel
from typing import Union


class UserBase(BaseModel):
    id: int
    username: str
    email: str


class User(UserBase):
    is_active: bool
    role: str

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None
