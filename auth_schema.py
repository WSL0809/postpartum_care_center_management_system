from pydantic import BaseModel
from typing import Dict, Union


class UserBase(BaseModel):
    id: int
    username: str
    email: str
    double_check_password: Union[str, None]


class User(UserBase):
    is_active: bool
    role: str


    class Config:
        orm_mode = True

class WxUser(BaseModel):
    id: int
    username: str
    user_detail: Dict
    double_check_password: Union[str, None]
    
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
