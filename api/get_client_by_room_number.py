from typing import Union, List, Dict, Optional

from fastapi import Depends, APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette import status

from auth import get_current_active_user
from auth_schema import User
from database import get_db
from model import Client
from schema import ClientBase, Baby

router = APIRouter()


class ClientResp(BaseModel):
    name: str
    tel: str
    age: int
    scheduled_date: str
    check_in_date: Union[str, None]
    hospital_for_childbirth: str
    contact_name: str
    contact_tel: str
    babies: List[Baby]
    meal_plan_details: str
    recovery_plan_details: Optional[str] = None
    mode_of_delivery: str
    assigned_baby_nurse_name: Union[str, None]
    room: Union[str, None]


class GetClientByRoomResp(BaseModel):
    status: Union[str, int]
    details: str
    clients: ClientResp


def do_get_client_in_room(db: Session, room_number: str):
    if not room_number:
        return None
    query_sql = text("""
        SELECT 
        client.name AS name, 
        client.tel AS tel, 
        client.age AS age, 
        client.scheduled_date,
        client.check_in_date, 
        client.hospital_for_childbirth, 
        client.contact_name, 
        client.contact_tel, 
        meal_plan.details AS meal_plan_details, 
        recovery_plan.details AS recovery_plan_details, 
        mode_of_delivery, 
        room, 
        baby_nurse.name AS assigned_baby_nurse_name,
        json_agg(
            json_build_object(
                'name', baby.name, 
                'birth_date', baby.birth_date, 
                'gender', baby.gender, 
                'birth_weight', baby.birth_weight,
                'birth_height', baby.birth_height,
                'health_status', baby.health_status,
                'birth_certificate', baby.birth_certificate,
                'remarks', baby.remarks,
                'mom_id_number', baby.mom_id_number,
                'dad_id_number', baby.dad_id_number,
                'summary', baby.summary
            )
        ) AS babies
        FROM client 
        LEFT JOIN baby ON client.id = baby.client_id 
        LEFT JOIN meal_plan ON client.meal_plan_id = meal_plan.meal_plan_id 
        LEFT JOIN recovery_plan ON client.recovery_plan_id = recovery_plan.recovery_plan_id 
        LEFT JOIN baby_nurse ON client.assigned_baby_nurse = baby_nurse.baby_nurse_id 
        WHERE room = :room_number
        GROUP BY client.id, meal_plan.meal_plan_id, recovery_plan.recovery_plan_id, baby_nurse.baby_nurse_id;

    """)
    client = db.execute(query_sql, {"room_number": room_number}).mappings().all()
    if len(client) > 1:
        raise HTTPException(status_code=400, detail="Multiple clients found in the same room")
    return dict(client[0])


@router.get("/get_client_in_room", response_model=GetClientByRoomResp)
async def get_client_in_room(room_number: str, current_user: User = Depends(get_current_active_user),
                             db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    client = do_get_client_in_room(db, room_number)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return GetClientByRoomResp(status="success", details="Client fetched successfully.",
                               clients=ClientResp(**client))
