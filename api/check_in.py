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
from config import RoomStatus, BabyNurseWorkStatus, ClientTag

router = APIRouter()
free = RoomStatus.Free.value
occupied = RoomStatus.Occupied.value
booked = RoomStatus.Booked.value
working = BabyNurseWorkStatus.working.value

class BabyRecv(BaseModel):
    name: Union[str, None] = "未填写"
    gender: Union[str, None] = "未填写"
    birth_date: Union[str, None] = "未填写"
    birth_weight: Union[str, None] = "未填写"
    birth_height: Union[str, None] = "未填写"
    health_status: Union[str, None] = "未填写"
    birth_certificate: Union[str, None] = "未填写"
    remarks: Union[str, None] = "未填写"
    mom_id_number: Union[str, None] = "未填写"
    dad_id_number: Union[str, None] = "未填写"
    summary: Union[str, None] = "未填写"


class CheckInRecv(BaseModel):
    room_number: str
    baby: BabyRecv
    check_in_date: str
    assigned_baby_nurse_name: str


class CheckInResp(BaseModel):
    status: str
    details: str


def update_room_and_baby(db, check_in_recv: CheckInRecv):
    get_client_status_sql = text(
        """
        SELECT status FROM client WHERE id = (SELECT client_id FROM room WHERE room_number = :room_number AND status = :booked)
        """
    )
    client_status = db.execute(get_client_status_sql, {"room_number": check_in_recv.room_number, "booked": booked}).mappings().first()
    client_status = client_status["status"].split("-")[0]
    # update_client_status_sql = text(
    #     """
    #     UPDATE client SET status = :status
    #     WHERE id = (SELECT client_id FROM room WHERE room_number = :room_number AND status = :booked)
    #     """
    # )
    # db.execute(update_client_status_sql, {"status": f'{client_status}-{ClientTag.checked_in.value}', "room_number": check_in_recv.room_number, "booked": booked})

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
    update_client_sql = text(
        """
        UPDATE client SET status = :status ,check_in_date = :check_in_date, assigned_baby_nurse = (SELECT baby_nurse_id AS assigned_baby_nurse FROM baby_nurse WHERE name = :assigned_baby_nurse_name)
        WHERE id = (SELECT client_id FROM room WHERE room_number = :room_number)
        """
    )

    update_baby_nurse_work_status_sql = text(
        """
        UPDATE baby_nurse SET work_status = :working
        WHERE name = :assigned_baby_nurse_name
        """
    )

    try:
        # 执行更新房间状态的操作
        db.execute(update_room_sql, {"room_number": check_in_recv.room_number, "occupied": occupied})
        # 插入婴儿信息
        baby_data = dict(check_in_recv.baby)
        baby_data["room_number"] = check_in_recv.room_number
        db.execute(update_baby_sql, baby_data)
        db.execute(update_client_sql, {"room_number": check_in_recv.room_number, "check_in_date": check_in_recv.check_in_date, "assigned_baby_nurse_name": check_in_recv.assigned_baby_nurse_name, "status": f'{client_status}-{ClientTag.checked_in.value}'})
        db.execute(update_baby_nurse_work_status_sql, {"assigned_baby_nurse_name": check_in_recv.assigned_baby_nurse_name, "working": working})
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


@router.post("/check_in")
def check_in_room(check_in_recv: CheckInRecv, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):

    try:
        update_room_and_baby(db, check_in_recv)
        return CheckInResp(status="success", details="入住成功")
    except Exception as e:
        return CheckInResp(status="error", details=str(e))
