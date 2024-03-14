from typing import Union

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from config import RoomStatus


router = APIRouter()
free = RoomStatus.Free.value
occupied = RoomStatus.Occupied.value


class BabyRecv(BaseModel):
    name: Union[str, None]
    gender: str
    birth_date: str
    birth_weight: str
    birth_height: str
    health_status: str
    birth_certificate: str
    remarks: str
    mom_id_number: str
    dad_id_number: str
    summary: str

    class Config:
        orm_mode = True


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
        UPDATE room SET status = :occupied, client_id = :client_id
        WHERE room_number = :room_number
        """
    )
    update_baby_sql = text(
        """
        INSERT INTO baby (name, gender, birth_date, birth_weight, birth_height, 
        health_status, birth_certificate, remarks, mom_id_number, dad_id_number, summary, client_id)
        VALUES (:name, :gender, :birth_date, :birth_weight, :birth_height, 
        :health_status, :birth_certificate, :remarks, :mom_id_number, :dad_id_number, :summary, :client_id)
        """
    )
    try:
        with db.begin():
            db.execute(update_room_sql, dict(check_in_recv))
            db.execute(update_baby_sql, dict(check_in_recv))
    except SQLAlchemyError as e:
        return {"status": "fail", "details": str(e)}


@router.post("/check_in")
def check_in_room(check_in_recv: CheckInRecv, db: Session = Depends(get_db)):
    try:
        update_room_and_baby(db, check_in_recv)
        return CheckInResp(status="success", details="入住成功")
    except Exception as e:
        return CheckInResp(status="error", details=str(e))
