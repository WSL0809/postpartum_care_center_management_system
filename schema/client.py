from pydantic import BaseModel
from typing import List, Optional, Dict, Union
from .baby import Baby
from .plan import MealPlanModel, RecoveryPlanModel
from .base import BabyNurseModel


class ClientBase(BaseModel):
    name: str
    tel: str
    age: int
    scheduled_date: str
    check_in_date: str
    hospital_for_childbirth: str
    contact_name: str
    contact_tel: str
    babies: List[Baby]
    meal_plan_id: int
    recovery_plan_id: Optional[int] = None
    mode_of_delivery: str
    assigned_baby_nurse: Union[int, None]
    room: str

    class Config:
        orm_mode = True
class ClientCreate(ClientBase):
    class Config:
        orm_mode = True
        from_attributes = True


class ClientList(BaseModel):
    clients: List[ClientBase]
    pagination: Dict


class ClientModel(BaseModel):
    id: int
    name: str
    tel: str
    age: int
    scheduled_date: str
    check_in_date: str
    hospital_for_childbirth: str
    contact_name: str
    contact_tel: str
    mode_of_delivery: str
    room: Optional[str] = None
    meal_plan: Optional[MealPlanModel] = None
    recovery_plan: Optional[RecoveryPlanModel] = None
    assigned_baby_nurse: Optional[BabyNurseModel] = None

    class Config:
        orm_mode = True
        from_attributes = True


def client_to_client_base(client):
    """将 Client 实体转换为 ClientBase 响应模型"""
    return ClientBase(
        name=client.name,
        tel=client.tel,
        age=client.age,
        scheduled_date=client.scheduled_date,
        check_in_date=client.check_in_date,
        hospital_for_childbirth=client.hospital_for_childbirth,
        contact_name=client.contact_name,
        contact_tel=client.contact_tel,
        babies=[baby_to_baby_base(baby) for baby in client.babies],
        meal_plan_id=client.meal_plan_id,
        recovery_plan_id=client.recovery_plan_id,
        mode_of_delivery=client.mode_of_delivery,
        assigned_baby_nurse=client.assigned_baby_nurse,
        room=client.room,
    )


def baby_to_baby_base(baby):
    """将 Baby 实体转换为 BabyBase 响应模型"""
    return Baby(
        name=baby.name,
        gender=baby.gender,
        birth_date=baby.birth_date,
        birth_weight=baby.birth_weight,
        birth_height=baby.birth_height,
        health_status=baby.health_status,
        birth_certificate=baby.birth_certificate,
        remarks=baby.remarks,
        mom_id_number=baby.mom_id_number,
        dad_id_number=baby.dad_id_number,
        summary=baby.summary,
    )
