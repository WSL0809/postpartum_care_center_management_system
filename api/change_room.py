from typing import Union

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel
from starlette import status

from auth import get_current_active_user, roles_required
from auth_schema import User
from database import get_db
from config import RoomStatus
from sqlalchemy.exc import SQLAlchemyError

from model import Room
from .utils import exception_handler

router = APIRouter()
free = RoomStatus.Free.value
occupied = RoomStatus.Occupied.value


class ChangeRoomRecv(BaseModel):
    old_room_number: str
    new_room_number: str
    client_id: int


class ChangeRoomResp(BaseModel):
    status: Union[str, int]
    details: str


@exception_handler
def update_client_and_room(
    db, old_room_number: str, new_room_number: str, client_id: int
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
        UPDATE room SET client_id = :client_id WHERE room_number = :new_room_number;
        """
    )

    try:
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
                "client_id": client_id,
            },
        )

        db.commit()
    except Exception as e:
        # 遇到错误，回滚事务
        db.rollback()
        print(f"Transaction failed: {e}")


def get_room_status(db, room_number: str):
    result = db.query(Room).filter(Room.room_number == room_number).first().status
    return result


@router.post("/change_room", response_model=ChangeRoomResp)
@roles_required("admin")
async def change_room(
    change_room_recv: ChangeRoomRecv,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if (
        get_room_status(db, change_room_recv.old_room_number) == occupied
        and get_room_status(db, change_room_recv.new_room_number) == free
    ):
        try:
            update_client_and_room(
                db,
                change_room_recv.old_room_number,
                change_room_recv.new_room_number,
                change_room_recv.client_id,
            )
            return ChangeRoomResp(status=status.HTTP_200_OK, details="完成")
        except SQLAlchemyError as e:
            return ChangeRoomResp(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details=f"数据库发生错误: {e}",
            )
    else:
        return ChangeRoomResp(
            status=status.HTTP_400_BAD_REQUEST, details="不符合换房要求"
        )
