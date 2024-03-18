from typing import Optional, Union

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel
from starlette import status

from auth import get_current_active_user
from auth_schema import User
from database import get_db


router = APIRouter()


class GetRoomByRoomNameResp(BaseModel):
    room_number: str
    name: Union[str, None]
    baby_nurse_name: Union[str, None]
    meal_plan_details: Union[str, None]
    meal_plan_duration: Union[int, None]
    recovery_plan_details: Union[str, None]
    recovery_plan_duration: Union[int, None]
    status: str
    recently_used: Union[str, None]
    notes: Union[str, None]


class GetRoomByRoomNameRecv(BaseModel):
    room_number: str


@router.get("/get_room_by_room_name", response_model=GetRoomByRoomNameResp)
def get_all_room_info(room_number: str, current_user: User = Depends(get_current_active_user),
                      db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be an admin to access this information."
        )

    sql = text(
        """
        SELECT room_number,
        client.name AS name,
        baby_nurse.name AS baby_nurse_name,
        meal_plan.details AS meal_plan_details, meal_plan.duration AS meal_plan_duration,
        recovery_plan.details AS recovery_plan_details, recovery_plan.duration AS recovery_plan_duration,
        room.status AS status, room.recently_used AS recently_used, room.notes AS notes
        FROM room
        LEFT JOIN client ON room.client_id = client.id
        LEFT JOIN meal_plan ON client.meal_plan_id = meal_plan.meal_plan_id
        LEFT JOIN recovery_plan ON client.recovery_plan_id = recovery_plan.recovery_plan_id
        LEFT JOIN baby_nurse ON client.assigned_baby_nurse = baby_nurse.baby_nurse_id
        WHERE room.room_number = :room_number
        """
    )
    result = db.execute(sql, {"room_number": room_number}).mappings().first()

    if result is None:
        return {"message": "No room found with the specified room number."}
    else:
        # 将结果转换为字典，以便返回
        return dict(result)
