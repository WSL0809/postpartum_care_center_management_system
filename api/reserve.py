import json

from datetime import datetime
from typing import Optional, Union, Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from pydantic import BaseModel
from starlette import status

from api.utils import exception_handler
from auth import get_current_active_user
from auth_schema import User
from database import get_db
from config import RoomStatus, ClientTag

router = APIRouter()
occupied = RoomStatus.Occupied.value
booked = RoomStatus.Booked.value


class ReserveRecv(BaseModel):
    id_number: str
    name: str
    tel: str
    age: int
    scheduled_date: str
    check_in_date: Union[str, None] = None
    hospital_for_childbirth: str
    contact_name: str
    contact_tel: str
    meal_plan_id: int
    recovery_plan_id: Optional[int] = None
    mode_of_delivery: str
    assigned_baby_nurse: Optional[int] = None
    room: str
    meal_plan_seller: Union[Dict, None] = {}
    recovery_plan_seller: Union[Dict, None] = {}
    due_date: Union[str, None] = None
    status: str
    transaction_price: Union[float, None]

    class Config:
        orm_mode = True


class ReserveResp(BaseModel):
    status: str
    details: str


@exception_handler
def update_client_and_room(db, reserve_recv: ReserveRecv):
    # 更新状态以反映客户端和房间的变更
    reserve_recv.status = f'{reserve_recv.status}-{ClientTag.reversed_room.value}'

    create_client_sql = text(
        """
        INSERT INTO client (name, tel, age, scheduled_date, check_in_date, hospital_for_childbirth, contact_name, contact_tel, mode_of_delivery, room, meal_plan_id, recovery_plan_id, assigned_baby_nurse, id_number, status, meal_plan_seller, recovery_plan_seller, due_date, transaction_price)
        VALUES (:name, :tel, :age, :scheduled_date, :check_in_date, :hospital_for_childbirth, :contact_name, :contact_tel, :mode_of_delivery, :room, :meal_plan_id, :recovery_plan_id, :assigned_baby_nurse, :id_number, :status, :meal_plan_seller, :recovery_plan_seller, :due_date, :transaction_price)
        RETURNING id
        """
    )

    update_room_sql = text(
        """
        UPDATE room SET status = :booked, client_id = :client_id WHERE room_number = :room;
        """
    )

    reserve_recv_dict = {
        "name": reserve_recv.name,
        "tel": reserve_recv.tel,
        "age": reserve_recv.age,
        "scheduled_date": reserve_recv.scheduled_date,
        "check_in_date": reserve_recv.check_in_date,
        "hospital_for_childbirth": reserve_recv.hospital_for_childbirth,
        "contact_name": reserve_recv.contact_name,
        "contact_tel": reserve_recv.contact_tel,
        "mode_of_delivery": reserve_recv.mode_of_delivery,
        "room": reserve_recv.room,
        "meal_plan_id": reserve_recv.meal_plan_id,
        "recovery_plan_id": reserve_recv.recovery_plan_id,
        "assigned_baby_nurse": reserve_recv.assigned_baby_nurse,
        "id_number": reserve_recv.id_number,
        "status": reserve_recv.status,
        "meal_plan_seller": json.dumps(reserve_recv.meal_plan_seller),
        "recovery_plan_seller": json.dumps(reserve_recv.recovery_plan_seller),
        "due_date": reserve_recv.due_date,
        "transaction_price": reserve_recv.transaction_price
    }

    try:
        client_id = db.execute(create_client_sql, reserve_recv_dict).fetchone()[0]
        db.flush()  # 确保客户ID可用
        db.execute(update_room_sql, {"room": reserve_recv.room, "booked": booked, "client_id": client_id})
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        print("发生错误，事务回滚:", e)
        raise e


@router.post("/reserve")
async def reserve_room(reserve_recv: ReserveRecv,
                       db: Session = Depends(get_db)):
    print(dict(reserve_recv))
    try:
        update_client_and_room(db, reserve_recv)
        return ReserveResp(status="success", details="预定成功")
    except Exception as e:
        return ReserveResp(status="error", details=str(e))


'''
the logic of reserve:
1. about room table: update room.status = booked, update room.client_id
2. about client table: add client
3. do not add baby in reservation
4. return ReserveResp
'''
