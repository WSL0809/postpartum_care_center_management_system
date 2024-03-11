from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel
from starlette import status

from auth_schema import User
from database import get_db
from main import get_current_active_user

router = APIRouter()


class GetAllRoomsResp(BaseModel):
    id: int
    status: str
    recently_used: str
    notes: str


@router.get("/get_all_rooms")
def get_all_room_info(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role == "admin":
        sql = text(
            """
            SELECT *
            FROM room
            JOIN client ON room.client_id = client.id
            LEFT JOIN meal_plan ON client.meal_plan_id = meal_plan.meal_plan_id
            LEFT JOIN recovery_plan ON client.recovery_plan_id = recovery_plan.recovery_plan_id
            LEFT JOIN baby_nurse ON client.assigned_baby_nurse = baby_nurse.baby_nurse_id
            """
        )
        result = db.execute(sql)
        rooms_info = [dict(row) for row in result.mappings()]
        return rooms_info
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )