from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel
from starlette import status

from auth import get_current_active_user
from auth_schema import User
from database import get_db
from model import Room, Client
from model.client import BabyNurse

router = APIRouter()


class MealPlan(BaseModel):
    details: str
    duration: int


class RecoveryPlan(BaseModel):
    details: str
    duration: int


class GetAllRoomsResp(BaseModel):
    room_number: str
    name: str
    baby_nurse_name: str
    meal_plan: MealPlan
    recovery_plan: RecoveryPlan
    status: str
    recently_used: str
    notes: str


@router.get("/get_all_rooms")
def get_all_room_info(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role == "admin":
        sql = text(
            """
            SELECT room_number,
            client.name,
            baby_nurse.name,
            meal_plan.details, meal_plan.duration,
            recovery_plan.details, recovery_plan.duration,
            room.status, room.recently_used, room.notes
            FROM room
            JOIN client ON room.client_id = client.id
            LEFT JOIN meal_plan ON client.meal_plan_id = meal_plan.meal_plan_id
            LEFT JOIN recovery_plan ON client.recovery_plan_id = recovery_plan.recovery_plan_id
            LEFT JOIN baby_nurse ON client.assigned_baby_nurse = baby_nurse.baby_nurse_id
            """
        )
        result = db.execute(sql).fetchall()
        print(result)
        rooms_info = [
            GetAllRoomsResp(
                room_number=row[0],
                name=row[1],
                baby_nurse_name=row[2],
                meal_plan=MealPlan(
                    details=row[3],
                    duration=row[4]
                ),
                recovery_plan=RecoveryPlan(
                    details=row[5],
                    duration=row[6]
                ),
                status=row[7],
                recently_used=row[8],
                notes=row[9]
            ) for row in result
        ]
        result = db.execute(sql).mappings().all()
        print(result)
        return rooms_info
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
