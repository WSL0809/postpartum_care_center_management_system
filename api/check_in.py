from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from database import engine
from config import RoomStatus
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from .utils import exception_handler




router = APIRouter()
free = RoomStatus.Free.value
occupied = RoomStatus.Occupied.value


class ChangeRoomRecv(BaseModel):
    old_room_number: str
    new_room_number: str
    client_name: str


class ChangeRoomResp(BaseModel):
    status: str
    details: str

@exception_handler
def update_client_and_room(
    db, old_room_number: str, new_room_number: str, client_name: str
):
    """
    Update the room number for a client in the database.

    Args:
    - db: Session: The database session
    - old_room_number: str: The old room number
    - new_room_number: str: The new room number
    """
    sql_update_client = text(
        """
        UPDATE client SET room = :new_room_number WHERE room = :old_room_number
        """
    )

    sql_update_room = text(
        """
        UPDATE room SET status = :free WHERE room_number = :old_room_number;
        UPDATE room SET client_id = NULL WHERE room_number = :old_room_number;
        UPDATE room SET status = :occupied WHERE room_number = :new_room_number;
        UPDATE room SET client_id = (SELECT id FROM client WHERE name = :client_name) WHERE room_number = :new_room_number;
        """
    )

    with db.begin():
        db.execute(
            sql_update_client,
            {"new_room_number": new_room_number, "old_room_number": old_room_number},
        )
        db.execute(
            sql_update_room,
            {
                "free": free,
                "occupied": occupied,
                "new_room_number": new_room_number,
                "old_room_number": old_room_number,
                "client_name": client_name,
            },
        )


@router.post("/change_room", response_model=ChangeRoomResp)
async def change_room(change_room_recv: ChangeRoomRecv, db: Session = Depends(get_db)):
    update_client_and_room(
        db,
        change_room_recv.old_room_number,
        change_room_recv.new_room_number,
        change_room_recv.client_name,
    )
    return ChangeRoomResp(status="success", details="success")