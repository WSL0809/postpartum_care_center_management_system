from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from .baby import Baby


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
    meal_plan: int
    recovery_plan: Optional[int] = None
    mode_of_delivery: str
    assigned_baby_nurse: int


class ClientCreate(ClientBase):

    class Config:
        orm_mode = True
        from_attributes = True


class ClientList(BaseModel):
    clients: List[ClientBase]
    total: int
