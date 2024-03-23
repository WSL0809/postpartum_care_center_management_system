from typing import Union, List, Dict, Optional

from fastapi import Depends, APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from auth import get_current_active_user
from auth_schema import User
from database import get_db
from model import Client
from schema import ClientBase
import re

router = APIRouter()


class GetClientByRoomResp(BaseModel):
    status: Union[str, int]
    details: str
    clients: ClientBase


def do_get_client_in_room(db: Session, room_number: str):
    query = db.query(Client)
    if room_number:
        query = query.filter(Client.room_number == room_number)
    client = query.first()
    return client


@router.get("/get_client_in_room", response_model=GetClientByRoomResp)
async def get_client_in_room(room_number: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    client = do_get_client_in_room(db, room_number)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return GetClientByRoomResp(status="success", details="Client fetched successfully.",
                               clients=ClientBase.from_orm(client))
