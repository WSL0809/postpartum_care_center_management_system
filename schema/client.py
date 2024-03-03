from pydantic import BaseModel, date
from typing import List

class ClientBase(BaseModel):
    id: int
    name: str
    tel: str
    age: int
    scheduled_date: date
    check_in_date: date
    hospital_for_childbirth: str
    contact_name: str
    contact_tel: str
    summary: str
    babies: str
    meal_plan: str
    recovery_plan: str


class ClientList(BaseModel):
    clients: List[ClientBase]
    total: int


