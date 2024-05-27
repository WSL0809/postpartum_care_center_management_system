from typing import Union

from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from auth import roles_required, get_current_active_user
from auth_schema import User
from model import Room
from database import get_db
from pydantic import BaseModel

router = APIRouter()


class AddRoomRecv(BaseModel):
    room_number: str
    notes: Union[str, None]


class DeleteRoomRecv(BaseModel):
    room_number: str


class AddRoomResp(BaseModel):
    msg: str
    success: bool


@router.post("/add_room", response_model=AddRoomResp)
@roles_required("admin")
async def add_room(room_info: AddRoomRecv, current_user: User = Depends(get_current_active_user),
                   db: Session = Depends(get_db)):
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


@router.post("/delete_room")
@roles_required("admin")
async def delete_room(room: DeleteRoomRecv, db: Session = Depends(get_db)):
    try:
        db.query(Room).filter(Room.room_number == room.room_number).delete()
        db.commit()
        return AddRoomResp(msg="Room deleted successfully", success=True)
    except SQLAlchemyError as e:
        db.rollback()
        return AddRoomResp(msg=f"Database error: {str(e)}", success=False)
    except Exception as e:
        return AddRoomResp(msg=f"Unexpected error: {str(e)}", success=False)
