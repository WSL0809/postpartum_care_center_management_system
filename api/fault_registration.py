from typing import Union

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from auth import get_current_active_user
from auth_schema import User
from config import RoomStatus, ClientStatus
from database import get_db
from datetime import datetime


router = APIRouter()

free = RoomStatus.Free.value

class FaultRegistrationRecv(BaseModel):
    room_number: str
