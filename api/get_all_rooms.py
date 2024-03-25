from typing import Optional, Union

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.engine import row
from sqlalchemy.orm import Session
from pydantic import BaseModel
from starlette import status

from auth import get_current_active_user
from auth_schema import User
from database import get_db
from model import Room, Client
from model.client import BabyNurse

router = APIRouter()


class GetAllRoomsResp(BaseModel):
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
    meal_plan_seller: Union[dict, None]
    recovery_plan_seller: Union[dict, None]
    maintenance_list: Union[dict, None]

@router.get("/get_all_rooms")
def get_all_room_info(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role == "admin":
        sql = text(
            """
            SELECT room_number,
            client.name AS name, client.meal_plan_seller AS meal_plan_seller, client.recovery_plan_seller AS recovery_plan_seller,
            baby_nurse.name AS baby_nurse_name,
            meal_plan.details AS meal_plan_details, meal_plan.duration AS meal_plan_duration,
            recovery_plan.details AS recovery_plan_details, recovery_plan.duration AS recovery_plan_duration,
            room.status AS status, room.recently_used AS recently_used, room.notes AS notes,room.fault_list AS maintenance_list
            FROM room
            LEFT JOIN client ON room.client_id = client.id
            LEFT JOIN meal_plan ON client.meal_plan_id = meal_plan.meal_plan_id
            LEFT JOIN recovery_plan ON client.recovery_plan_id = recovery_plan.recovery_plan_id
            LEFT JOIN baby_nurse ON client.assigned_baby_nurse = baby_nurse.baby_nurse_id
            WHERE client.status <> 1
            """
        )
        result = db.execute(sql).mappings().all()
        if result:
            return [GetAllRoomsResp(**dict(row)) for row in result]
        else:
            return [{"status": "fail", "details": "No rooms found"}]
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
