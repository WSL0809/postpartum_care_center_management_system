from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import model
from database import get_db

router = APIRouter()


@router.get("/get_meal_plan_by_id")
async def get_plan_by_id(meal_plan_id: int, db: Session = Depends(get_db)):
    return db.query(model.MealPlan).filter(model.MealPlan.meal_plan_id == meal_plan_id).first()


@router.get("/get_recovery_plan_by_id")
async def get_plan_by_id(recovery_plan_id: int, db: Session = Depends(get_db)):
    return db.query(model.RecoveryPlan).filter(model.RecoveryPlan.recovery_plan_id == recovery_plan_id).first()
