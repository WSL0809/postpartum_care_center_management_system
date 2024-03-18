from typing import Union

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from pydantic import BaseModel
from starlette import status

from auth import get_current_active_user
from auth_schema import User
from database import get_db
from config import RoomStatus

router = APIRouter()
free = RoomStatus.Free.value
occupied = RoomStatus.Occupied.value


class BabyRecv(BaseModel):
    name: Union[str, None] = "0"
    gender: str
    birth_date: str
    birth_weight: str
    birth_height: str
    health_status: str
    birth_certificate: Union[str, None] = "0"
    remarks: str
    mom_id_number: Union[str, None] = "0"
    dad_id_number: Union[str, None] = "0"
    summary: Union[str, None] = "0"


class CheckInRecv(BaseModel):
    room_number: str
    baby: BabyRecv
    check_in_date: str


class CheckInResp(BaseModel):
    status: str
    details: str


def update_room_and_baby(db, check_in_recv: CheckInRecv):
    update_room_sql = text(
        """
        UPDATE room SET status = :occupied
        WHERE room_number = :room_number
        """
    )
    update_baby_sql = text(
        """
        INSERT INTO baby (
            name, gender, birth_date, birth_weight, birth_height, health_status, 
            birth_certificate, remarks, mom_id_number, dad_id_number, summary, client_id
        )
        VALUES (
            :name, :gender, :birth_date, :birth_weight, :birth_height, 
            :health_status, :birth_certificate, :remarks, :mom_id_number, :dad_id_number, 
            :summary, (SELECT client_id FROM room WHERE room_number = :room_number)
        )

        """
    )

    try:
        # 执行更新房间状态的操作
        db.execute(update_room_sql, {"room_number": check_in_recv.room_number, "occupied": occupied})
        # 插入婴儿信息
        baby_data = dict(check_in_recv.baby)
        baby_data["room_number"] = check_in_recv.room_number
        db.execute(update_baby_sql, baby_data)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


@router.post("/check_in")
def check_in_room(check_in_recv: CheckInRecv, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        update_room_and_baby(db, check_in_recv)
        return CheckInResp(status="success", details="入住成功")
    except Exception as e:
        return CheckInResp(status="error", details=str(e))
