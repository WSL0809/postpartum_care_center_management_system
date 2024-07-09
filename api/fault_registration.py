import json
from typing import Union, Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from auth import get_current_active_user
from auth_schema import User
from config import RoomStatus
from database import get_db

router = APIRouter()

free = RoomStatus.Free.value
repair = RoomStatus.Repair.value


class FaultRegistrationRecv(BaseModel):
    room_number: str
    fault_list: Union[Dict, None]


class FaultRegistrationResp(BaseModel):
    status: Union[str, int]
    details: Union[str, None]


def repair_complete(room_number: str, db: Session):
    sql = text(
        """
        UPDATE room SET status = :status, fault_list = NULL WHERE room_number = :room_number;
        
        """
    )
    try:
        db.execute(sql, {"room_number": room_number, "status": free})
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        return FaultRegistrationResp(status=status.HTTP_500_INTERNAL_SERVER_ERROR, details="修理失败")


@router.post("/fault_registration")
def fault_registration(fault_registration: FaultRegistrationRecv, current_user: User = Depends(get_current_active_user),
                       db: Session = Depends(get_db)):

    if len(fault_registration.fault_list) == 0 or fault_registration.fault_list is None:
        repair_complete(fault_registration.room_number, db)
        return FaultRegistrationResp(status=status.HTTP_200_OK, details="修理完成")

    is_room_free = text(
        """
        SELECT room_number
        FROM room
        WHERE room_number = :room_number
        AND status = :status
        """
    )
    try:
        result = db.execute(is_room_free, {"room_number": fault_registration.room_number, "status": free}).first()
        db.commit()
    except SQLAlchemyError:
        return FaultRegistrationResp(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                     details="未找到该房间或房间不在空闲状态")
    if result:
        sql = text(
            """
            UPDATE room SET status = :status, fault_list = :fault_list WHERE room_number = :room_number;
            
            """
        )
        try:
            db.execute(sql, {"status": repair, "room_number": fault_registration.room_number,
                             "fault_list": json.dumps(fault_registration.fault_list)})
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            return FaultRegistrationResp(status=status.HTTP_500_INTERNAL_SERVER_ERROR, details=f"故障登记失败: {e}")
        return FaultRegistrationResp(status=status.HTTP_200_OK, details="故障登记成功")
    else:

        return FaultRegistrationResp(status=status.HTTP_400_BAD_REQUEST, details="房间不在空闲状态")
