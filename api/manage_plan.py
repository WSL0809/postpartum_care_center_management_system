import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session

from auth import get_current_active_user
from auth_schema import User
from database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


class PlanRecvBase(BaseModel):
    id: int
    name: str
    details: str
    duration: int
    price: float


class PlanCreate(BaseModel):
    plan_category: str
    name: str = 'none'
    details: str = 'none'
    duration: int = 0
    price: float


class PlanDel(BaseModel):
    id: int
    plan_category: str


class PlanRecv(PlanRecvBase):
    plan_category: str

    class Config:
        orm_mode = True


class PlanResp(BaseModel):
    meal_plan: List[PlanRecvBase]
    recovery_plan: List[PlanRecvBase]


def create_plan_in_db(db, plan_create):
    create_plan_sql = ''
    if plan_create.plan_category == "meal_plan":
        create_plan_sql = text(
            "INSERT INTO meal_plan (details, duration, name, price) VALUES (:details, :duration, :name, :price)"
        )
    elif plan_create.plan_category == "recovery_plan":
        create_plan_sql = text(
            "INSERT INTO recovery_plan (details, duration, name, price) VALUES (:details, :duration, :name, :price)"
        )

    plan_info = dict(plan_create).copy()
    plan_info.pop("plan_category", None)
    try:
        db.execute(create_plan_sql, plan_info)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def delete_plan_in_db(db, plan_del):
    delete_plan_sql = ''
    query_client_meal_plan = ''
    if plan_del.plan_category == "meal_plan":
        query_client_meal_plan = text(
            "SELECT id, name FROM client WHERE meal_plan_id = :id"
        )
        delete_plan_sql = text(
            "DELETE FROM meal_plan WHERE meal_plan_id = :id"
        )
    elif plan_del.plan_category == "recovery_plan":
        delete_plan_sql = text(
            "DELETE FROM recovery_plan WHERE recovery_plan_id = :id"
        )

    plan_info = dict(plan_del).copy()
    plan_info.pop("plan_category", None)
    try:
        client_with_meal_plan = db.execute(query_client_meal_plan, plan_info).mappings().all()
        if client_with_meal_plan:
            raise HTTPException(status_code=400, detail="套餐正被使用")
        db.execute(delete_plan_sql, plan_info)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database error occurred: {e}")
        if "ForeignKeyViolation" in str(e.orig):
            raise HTTPException(status_code=400, detail="套餐正被使用")
        else:
            raise HTTPException(status_code=500, detail="Database operation failed")

    except Exception as e:
        db.rollback()
        logger.error(f"Unhandled exception: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


def get_plans_in_db(db, plan_category):
    get_plans_sql = ''
    if plan_category == "meal_plan":
        get_plans_sql = text(
            "SELECT meal_plan_id AS id, details, duration, name, price FROM meal_plan"
        )
    elif plan_category == "recovery_plan":
        get_plans_sql = text(
            "SELECT recovery_plan_id AS id, details, duration, name, price FROM recovery_plan"
        )

    try:
        res = db.execute(get_plans_sql).mappings().all()
        return [PlanRecvBase(**dict(row)) for row in res]
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# add new plan
@router.post("/create_plan")
async def create_plan(plan_create: PlanCreate, current_user: User = Depends(get_current_active_user),
                      db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=401, detail="only admin can add new plan")
    create_plan_in_db(db, plan_create)

    return {
        "status": "success",
        "details": "add new plan success"
    }


# edit plan
# @router.post("/edit_plan")
# async def edit_plan():
#     pass


# delete plan
@router.post("/delete_plan")
async def delete_plan(plan_del: PlanDel, current_user: User = Depends(get_current_active_user),
                      db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=401, detail="only admin can delete plan")
    try:
        delete_plan_in_db(db, plan_del)
        return {
            "status": "success",
            "details": "delete plan success"
        }
    except HTTPException as e:
        return {"status": "failed", "details": str(e)}


@router.get("/get_plans", response_model=PlanResp)
async def get_plans(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=401, detail="only admin can get plans")
    meal_plan_res = get_plans_in_db(db, "meal_plan")
    recovery_plan_res = get_plans_in_db(db, "recovery_plan")
    return PlanResp(meal_plan=meal_plan_res, recovery_plan=recovery_plan_res)
