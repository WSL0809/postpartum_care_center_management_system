import json

from typing import Optional, Union, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from pydantic import BaseModel

from auth import get_current_active_user
from auth_schema import User
from database import get_db
from config import RoomStatus, ClientTag

router = APIRouter()

occupied = RoomStatus.Occupied.value


class InsertClientRecv(BaseModel):
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
    room: Union[str, None] = None
    meal_plan_seller: Union[Dict, None] = {}
    recovery_plan_seller: Union[Dict, None] = {}
    due_date: Union[str, None] = None
    status: str
    transaction_price: Union[float, None]

    class Config:
        orm_mode = True


def update_client_and_room(db, insert_client_recv: InsertClientRecv):
    reserve_recv_dict = dict(insert_client_recv)
    reserve_recv_dict["meal_plan_seller"] = json.dumps(insert_client_recv.meal_plan_seller)
    reserve_recv_dict["recovery_plan_seller"] = json.dumps(insert_client_recv.recovery_plan_seller)
    reserve_recv_dict["status"] = f'{reserve_recv_dict["status"]}-{ClientTag.wait_for_room.value}'
    if insert_client_recv.room:
        try:
            create_client_sql = text(
                """
                INSERT INTO client (name, tel, age, scheduled_date, check_in_date, hospital_for_childbirth, contact_name, contact_tel, mode_of_delivery, room, meal_plan_id, recovery_plan_id, assigned_baby_nurse, id_number, status, meal_plan_seller, recovery_plan_seller, due_date, transaction_price)
                VALUES (:name, :tel, :age, :scheduled_date, :check_in_date, :hospital_for_childbirth, :contact_name, :contact_tel, :mode_of_delivery, :room, :meal_plan_id, :recovery_plan_id, :assigned_baby_nurse, :id_number, :status, :meal_plan_seller, :recovery_plan_seller, :due_date, :transaction_price)
                """
            )
            db.execute(create_client_sql, reserve_recv_dict)
            db.flush()
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"检查房间{insert_client_recv.room}是否存在, ERROR: {e}")
    else:
        try:
            create_client_sql_without_room = text(
                """
                INSERT INTO client (name, tel, age, scheduled_date, check_in_date, hospital_for_childbirth, contact_name, contact_tel, mode_of_delivery, meal_plan_id, recovery_plan_id, assigned_baby_nurse, id_number, status, meal_plan_seller, recovery_plan_seller, due_date, transaction_price)
                VALUES (:name, :tel, :age, :scheduled_date, :check_in_date, :hospital_for_childbirth, :contact_name, :contact_tel, :mode_of_delivery, :meal_plan_id, :recovery_plan_id, :assigned_baby_nurse, :id_number, :status, :meal_plan_seller, :recovery_plan_seller, :due_date, :transaction_price)
                """
            )
            db.execute(create_client_sql_without_room, reserve_recv_dict)
            db.flush()
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"ERROR: {e}")


@router.post("/insert_client")
async def insert_client(insert_client_recv: InsertClientRecv, current_user: User = Depends(get_current_active_user),
                        db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=401, detail="only admin can insert client")

    update_client_and_room(db, insert_client_recv)

    return {
        "status": "success",
        "details": "insert client success"
    }
