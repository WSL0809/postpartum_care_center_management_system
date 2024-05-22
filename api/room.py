from typing import Union

from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from auth import roles_required
from model import Room
from database import get_db
from pydantic import BaseModel

router = APIRouter()


class AddRoomRecv(BaseModel):
    room_number: str
    notes: Union[str, None]


class AddRoomResp(BaseModel):
    msg: str
    success: bool


@router.post("/add_room", response_model=AddRoomResp)
@roles_required("admin")
async def add_room(room_info: AddRoomRecv, db: Session = Depends(get_db)):
    try:
        room = Room(room_number=room_info.room_number, notes=room_info.notes)
        db.add(room)
        db.commit()
        db.refresh(room)
        return AddRoomResp(msg="Room added successfully", success=True)
    except SQLAlchemyError as e:
        db.rollback()
        return AddRoomResp(msg=f"Database error: {str(e)}", success=False)
    except Exception as e:
        return AddRoomResp(msg=f"Unexpected error: {str(e)}", success=False)
