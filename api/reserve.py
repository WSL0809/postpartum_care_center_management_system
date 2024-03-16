from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from pydantic import BaseModel
from starlette import status

import model
from api.utils import exception_handler
from auth import get_current_active_user
from auth_schema import User
from database import get_db
from config import RoomStatus

router = APIRouter()
occupied = RoomStatus.Occupied.value
booked = RoomStatus.Booked.value


class ReserveRecv(BaseModel):
    id_number: str
    name: str
    tel: str
    age: int
    scheduled_date: str
    check_in_date: str
    hospital_for_childbirth: str
    contact_name: str
    contact_tel: str
    meal_plan_id: int
    recovery_plan_id: Optional[int] = None
    mode_of_delivery: str
    assigned_baby_nurse: int
    room: str

    class Config:
        orm_mode = True


class ReserveResp(BaseModel):
    status: str
    details: str


@exception_handler
def update_client_and_room(db, reserve_recv: ReserveRecv):
    # db_client = model.Client(**reserve_recv.dict())
    create_client_sql = text(
        """
        INSERT INTO client (name, tel, age, scheduled_date, check_in_date, hospital_for_childbirth, contact_name, contact_tel, mode_of_delivery, room, meal_plan_id, recovery_plan_id, assigned_baby_nurse, id_number)
        VALUES (:name, :tel, :age, :scheduled_date, :check_in_date, :hospital_for_childbirth, :contact_name, :contact_tel, :mode_of_delivery, :room, :meal_plan_id, :recovery_plan_id, :assigned_baby_nurse, :id_number)
        RETURNING id
        """
    )
    update_room_sql = text(
        """
        UPDATE room SET status = :booked, client_id = :client_id WHERE room_number = :room;
        """
    )
    try:
        # 执行创建客户操作
        client_id = db.execute(create_client_sql, reserve_recv.dict()).fetchone()[0]
        db.flush()  # 确保客户ID可用
        # 使用新客户ID更新房间状态
        db.execute(update_room_sql,
                   {
                       "room": reserve_recv.room,
                       "booked": booked,
                       "client_id": client_id
                   }
                  )
        db.commit()  # 提交事务
    except SQLAlchemyError as e:
        db.rollback()  # 发生错误时回滚事务
        print("发生错误，事务回滚:", e)
        raise e

@router.post("/reserve")
async def reserve_room(reserve_recv: ReserveRecv, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role == "admin":
        try:
            update_client_and_room(db, reserve_recv)
            return ReserveResp(status="success", details="预定成功")
        except Exception as e:
            return ReserveResp(status="error", details=str(e))
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

'''
the logic of reserve:
1. about room table: update room.status = booked, update room.client_id
2. about client table: add client
3. do not add baby in reservation
4. return ReserveResp
'''
