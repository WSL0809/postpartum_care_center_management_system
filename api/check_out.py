"""
the logic of check_out
1. about room table: update room.status = free, update room.client_id = NULL,update room.recently_used = today
2. about client table: delete client
3. return CheckOutResp
"""
from datetime import datetime
from typing import Union

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from config import RoomStatus, ClientStatus
from database import get_db
from datetime import datetime


router = APIRouter()

free = RoomStatus.Free.value


class CheckOutRecv(BaseModel):
    room_number: str
    recently_used: Union[str, None]


class CheckOutResp(BaseModel):
    status: str
    details: str


def update_room_and_client(db, check_out_recv):
    update_room_sql = text(
        """
        UPDATE room SET status = :status, client_id = NULL, recently_used = :recently_used
        WHERE room_number = :room_number
        """
    )

    update_client_sql = text(
        """
        UPDATE client SET status = :status, room = NULL WHERE id = (SELECT client_id FROM room WHERE room_number = :room_number)
        """
    )

    try:
        db.execute(update_client_sql, {"status": ClientStatus.out.value, "room_number": check_out_recv.room_number})
        db.execute(update_room_sql, {"room_number": check_out_recv.room_number, "recently_used": datetime.now().strftime('%Y-%m-%d'), "status": free})
        db.commit()
    except ValueError as ve:
        # 如果没有找到对应的client_id，可以在这里处理异常
        db.rollback()
        raise ve
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(str(e))


@router.post("/check_out")
async def check_out_room(check_out_recv: CheckOutRecv, db: Session = Depends(get_db)):
    try:
        update_room_and_client(db, check_out_recv)
        return CheckOutResp(status="success", details="退房成功")
    except Exception as e:
        return CheckOutResp(status="error", details=str(e))
