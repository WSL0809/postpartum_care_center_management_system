"""
the logic of check_out
1. about room table: update room.status = free, update room.client_id = NULL,update room.recently_used = today
2. about client table: delete client
3. return CheckOutResp
"""
from typing import Union

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from auth import get_current_active_user, roles_required
from auth_schema import User
from config import RoomStatus, BabyNurseWorkStatus, ClientTag
from database import get_db
from datetime import datetime

standby = BabyNurseWorkStatus.standby.value

router = APIRouter()

free = RoomStatus.Free.value


class TerminateRecv(BaseModel):
    room_number: str
    recently_used: Union[str, None]
    double_check_password: str


class CheckOutRecv(BaseModel):
    room_number: str
    recently_used: Union[str, None]


class CheckOutResp(BaseModel):
    status: Union[str, int]
    details: str


def update_room_and_client(db, check_out_recv):
    # 把房间状态改为空闲，房间客户改为空，最近使用改为今天
    update_room_sql = text(
        """
        UPDATE room SET status = :status, client_id = NULL, recently_used = :recently_used
        WHERE room_number = :room_number
        """
    )

    get_client_status_sql = text(
        """
        SELECT status FROM client WHERE id = (SELECT client_id FROM room WHERE room_number = :room_number)
        """
    )
    result = db.execute(get_client_status_sql, {"room_number": check_out_recv.room_number})
    client_result = result.mappings().first()

    if client_result is None:
        raise ValueError("没有找到指定房间的客户信息。")

    client_status = client_result["status"].split("-")[0]
    # 把客户状态改为已离店，客户房间改为空
    update_client_sql = text(
        """
        UPDATE client
        SET status = :status,
            room = NULL
        WHERE id = (SELECT client_id FROM room WHERE room_number = :room_number)
        """
    )

    # 把宝妈护工状态改为待命
    update_baby_nurse_work_status_sql = text(
        """
        UPDATE baby_nurse SET work_status = :standby WHERE baby_nurse_id = (SELECT assigned_baby_nurse FROM client WHERE room = :room_number)
        """
    )

    try:
        db.execute(update_baby_nurse_work_status_sql, {"room_number": check_out_recv.room_number, "standby": standby})

        db.execute(update_client_sql, {"status": f'{client_status}-{ClientTag.terminate.value}',
                                       "room_number": check_out_recv.room_number})
        db.execute(update_room_sql,
                   {"room_number": check_out_recv.room_number, "recently_used": datetime.now().strftime('%Y-%m-%d'),
                    "status": free})
        db.commit()
    except ValueError as ve:
        # 如果没有找到对应的client_id，可以在这里处理异常
        db.rollback()
        raise ve
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(str(e))


def client_check_out(db, check_out_recv):
    update_room_sql = text(
        """
        UPDATE room SET status = :status, client_id = NULL, recently_used = :recently_used
        WHERE room_number = :room_number
        """
    )

    get_client_status_sql = text(
        """
        SELECT status FROM client WHERE id = (SELECT client_id FROM room WHERE room_number = :room_number)
        """
    )
    result = db.execute(get_client_status_sql, {"room_number": check_out_recv.room_number})
    client_result = result.mappings().first()

    if client_result is None:
        raise ValueError("没有找到指定房间的客户信息。")

    try:
        client_status = client_result["status"].split("-")[0]
    except IndexError:
        raise ValueError("获取客户状态失败。")
    # 把客户状态改为已离店，客户房间改为空
    update_client_sql = text(
        """
        UPDATE client
        SET status = :status,
            room = NULL
        WHERE id = (SELECT client_id FROM room WHERE room_number = :room_number)
        """
    )

    # 把宝妈护工状态改为待命
    update_baby_nurse_work_status_sql = text(
        """
        UPDATE baby_nurse SET work_status = :standby WHERE baby_nurse_id = (SELECT assigned_baby_nurse FROM client WHERE room = :room_number)
        """
    )

    try:
        db.execute(update_baby_nurse_work_status_sql, {"room_number": check_out_recv.room_number, "standby": standby})

        db.execute(update_client_sql, {"status": f'{client_status}-{ClientTag.checked_out.value}',
                                       "room_number": check_out_recv.room_number})
        db.execute(update_room_sql,
                   {"room_number": check_out_recv.room_number, "recently_used": datetime.now().strftime('%Y-%m-%d'),
                    "status": free})
        db.commit()
    except ValueError as ve:
        # 如果没有找到对应的client_id，可以在这里处理异常
        db.rollback()
        raise ve
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(str(e))


@router.post("/terminate")
@roles_required("admin")
async def terminate_service(check_out_recv: TerminateRecv, current_user: User = Depends(get_current_active_user),
                            db: Session = Depends(get_db)):
    if current_user.double_check_password != check_out_recv.double_check_password:
        return CheckOutResp(status=status.HTTP_401_UNAUTHORIZED, details="密码错误")

    try:
        update_room_and_client(db, check_out_recv)
        return CheckOutResp(status=status.HTTP_200_OK, details="强制退房成功")
    except Exception as e:
        return CheckOutResp(status=status.HTTP_500_INTERNAL_SERVER_ERROR, details=str(e))


@router.post("/check_out")
@roles_required("admin")
async def check_out_service(check_out_recv: CheckOutRecv, current_user: User = Depends(get_current_active_user),
                            db: Session = Depends(get_db)):
    try:
        client_check_out(db, check_out_recv)
        return CheckOutResp(status=status.HTTP_200_OK, details="退房成功")
    except Exception as e:
        return CheckOutResp(status=status.HTTP_500_INTERNAL_SERVER_ERROR, details=str(e))
