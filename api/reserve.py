from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from config import RoomStatus

router = APIRouter()
occupied = RoomStatus.Occupied.value


class ReserveRecv(BaseModel):
    client_name: str
    room_number: str


class ReserveResp(BaseModel):
    status: str
    details: str


def update_client_and_room(
        db, client_name: str, room_number: str
):
    # 更新 client 表里的 room 字段
    sql_update_client = text(
        """
        UPDATE client SET room = :room_number WHERE name = :client_name;
        """
    )
    sql_update_room = text(
        """
        UPDATE room SET status = :occupied WHERE room_number = :room_number;
        UPDATE room SET client_id = (SELECT id FROM client WHERE name = :client_name) WHERE room_number = :room_number;
        """
    )

    with db.begin():
        db.execute(sql_update_client, {"room_number": room_number, "client_name": client_name})
        db.execute(sql_update_room, {"room_number": room_number})


@router.post("/reserve")
async def reserve_room(reserve_recv: ReserveRecv, db: Session = Depends(get_db)):
    update_client_and_room(db, reserve_recv.client_name, reserve_recv.room_number)
    return ReserveResp(status="success", details="预定成功")
