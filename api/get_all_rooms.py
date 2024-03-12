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
    name: str
    baby_nurse_name: str
    meal_plan_details: str
    meal_plan_duration: int
    recovery_plan_details: str
    recovery_plan_duration: int
    status: str
    recently_used: str
    notes: str

@router.get("/get_all_rooms")
def get_all_room_info(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role == "admin":
        sql = text(
            """
            SELECT room_number,
            client.name AS name,
            baby_nurse.name AS baby_nurse_name,
            meal_plan.details AS meal_plan_details, meal_plan.duration AS meal_plan_duration,
            recovery_plan.details AS recovery_plan_details, recovery_plan.duration AS recovery_plan_duration,
            room.status AS status, room.recently_used AS recently_used, room.notes AS notes
            FROM room
            JOIN client ON room.client_id = client.id
            LEFT JOIN meal_plan ON client.meal_plan_id = meal_plan.meal_plan_id
            LEFT JOIN recovery_plan ON client.recovery_plan_id = recovery_plan.recovery_plan_id
            LEFT JOIN baby_nurse ON client.assigned_baby_nurse = baby_nurse.baby_nurse_id
            """
        )
        result = db.execute(sql).mappings().all()
        if result:
            return [GetAllRoomsResp(**dict(row)) for row in result]
        else:
            return []
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

