from typing import Optional

from pydantic import BaseModel


class PlanBase(BaseModel):
    plan_id: int
    details: str
    duration: str


class MealPlanModel(BaseModel):
    meal_plan_id: Optional[int] = None
    details: Optional[str] = None
    duration: Optional[int] = None


class RecoveryPlanModel(BaseModel):
    recovery_plan_id: Optional[int] = None
    details: Optional[str] = None
    duration: Optional[int] = None
