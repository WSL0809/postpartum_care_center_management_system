from pydantic import BaseModel


class PlanBase(BaseModel):
    plan_id: int
    details: str
    duration: str
