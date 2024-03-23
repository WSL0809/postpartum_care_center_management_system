from datetime import datetime, timedelta, timezone
from typing import Union

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.orm import Session

import crud
import utils
from schema import ClientBase, ClientCreate
from auth_schema import UserCreate, User, TokenData
import models
from database import engine, SessionLocal
from utils import verify_password
from crud import create_user, get_user
from api import (change_room_router, reserve_router, get_all_rooms_router, check_in_router,
                 check_out_router, get_room_by_room_name_router, get_all_clients_router,
                 fault_registration_router, get_baby_nurse_router, insert_baby_nurse_router,
                 reminder_router, get_client_by_room_number_router)
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(change_room_router)
app.include_router(reserve_router)
app.include_router(get_all_rooms_router)
app.include_router(check_in_router)
app.include_router(check_out_router)
app.include_router(get_room_by_room_name_router)
app.include_router(get_all_clients_router)
app.include_router(fault_registration_router)
app.include_router(get_baby_nurse_router)
app.include_router(insert_baby_nurse_router)
app.include_router(reminder_router)
app.include_router(get_client_by_room_number_router)

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许访问的源列表
    allow_credentials=True,  # 允许携带cookie
    allow_methods=["*"],  # 允许的HTTP方法
    allow_headers=["*"],  # 允许的HTTP请求头
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, utils.SECRET_KEY, algorithm=utils.ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: str = Depends(utils.oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, utils.SECRET_KEY, algorithms=[utils.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user(db, token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.is_active:
        return current_user
    else:
        raise HTTPException(status_code=400, detail="Inactive user")


@app.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = get_user(db, form_data.username)
    access_token_expires = timedelta(minutes=utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/register", response_model=User)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    return create_user(db, user)


@app.get("/get_users")
async def get_users(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    if current_user.role == "admin" and current_user.is_active:
        return crud.get_users(db)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.post("/create_client/", response_model=ClientBase)
async def read_clients(client: ClientCreate, db: Session = Depends(get_db)):
    return crud.create_client(db, client)


@app.get("/hello")
async def hello():
    return {"hello"}
