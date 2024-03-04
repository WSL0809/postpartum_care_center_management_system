from pydantic import BaseModel


class BabyNurse(BaseModel):
    baby_nurse_id: int
    name: str
    age: str
    tel: str
    address: str
    id_number: str
    photo: str


class Plan(BaseModel):
    meal_plan_id: int
    details: str
    duration: str
