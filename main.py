from datetime import datetime, timedelta, timezone
from typing import Union

from fastapi import Depends, FastAPI, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.orm import Session

import crud
import schema.room
import utils
from schema import ClientBase, ClientCreate, ClientList, ClientModel
from auth_schema import UserCreate, User, TokenData
import models
from database import engine, SessionLocal
from utils import verify_password
from crud import create_user, get_user, get_clients_and_babies_by_name
from schema import RoomModel
from api import change_room_router, reserve_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(change_room_router)
app.include_router(reserve_router)

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


@app.get("/get_clients/")
async def get_clients(
    page: int = Query(default=1, alias="page"),
    page_size: int = Query(default=1000, alias="pageSize"),
    db: Session = Depends(get_db),
    client_name: str = None,
):
    # 使用提供的last_client_id和page_size进行查询
    clients = get_clients_and_babies_by_name(db, client_name, page, page_size)

    # 假设此处我们直接返回查询到的客户信息
    return clients


@app.post("/create_client/", response_model=ClientBase)
async def read_clients(client: ClientCreate, db: Session = Depends(get_db)):
    return crud.create_client(db, client)


@app.get("/get_room_by_id")
async def get_rooms(
    db: Session = Depends(get_db), room_id: int = Query(default=None, alias="room_id")
):
    # 获取 room join client
    return crud.get_room_by_id(db, room_id)
    #


@app.get("/get_all_rooms")
async def get_all_rooms_info(db: Session = Depends(get_db)):
    return crud.get_all_room_info(db)


@app.post("/set_room_client")
async def set_room_client(
    client: schema.room.RoomClientModel, db: Session = Depends(get_db)
):
    return crud.set_room_client(db, client)


@app.post("/check_out")
async def check_out(client: ClientCreate, db: Session = Depends(get_db)):
    return crud.set_room_client(db, client)


# @app.post("/book")
# async def check_in(client: ClientCreate, db: Session = Depends(get_db)):
#     return crud.set_room(db, client, "booked")
# @app.post("/repair")
# async def check_in(client: ClientCreate, db: Session = Depends(get_db)):
#     return crud.set_room(db, client, "under_maintenance")


@app.get("/hello")
async def hello():
    return {"hello"}
