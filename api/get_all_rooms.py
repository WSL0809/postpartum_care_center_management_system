from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db

router = APIRouter()


class GetAllRoomsResp(BaseModel):
    id: int
    status: str
    recently_used: str
    notes: str


@router.get("/get_all_rooms")
def get_all_room_info(db: Session = Depends(get_db)):
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