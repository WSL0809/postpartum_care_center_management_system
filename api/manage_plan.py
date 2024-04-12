from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from auth import get_current_active_user
from auth_schema import User
from database import get_db

router = APIRouter()


class PlanRecvBase(BaseModel):
    id: int
    details: str
    duration: int


class PlanCreate(BaseModel):
    plan_category: str
    details: str
    duration: int


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
            "INSERT INTO meal_plan (details, duration) VALUES (:details, :duration)"
        )
    elif plan_create.plan_category == "recovery_plan":
        create_plan_sql = text(
            "INSERT INTO recovery_plan (details, duration) VALUES (:details, :duration)"
        )

    plan_info = dict(plan_create).copy()
    plan_info.pop("plan_category", None)
    try:
        db.execute(create_plan_sql, plan_info)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def delete_plan(db, plan_recv):
    delete_plan_sql = ''
    if plan_recv.plan_category == "meal_plan":
        delete_plan_sql = text(
            "DELETE FROM meal_plan WHERE meal_plan_id = :id"
        )
    elif plan_recv.plan_category == "recovery_plan":
        delete_plan_sql = text(
            "DELETE FROM recovery_plan WHERE recovery_plan_id = :id"
        )

    plan_info = dict(plan_recv).copy()
    plan_info.pop("plan_category", None)
    try:
        db.execute(delete_plan_sql, plan_recv)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def get_plans_in_db(db, plan_category):
    get_plans_sql = ''
    if plan_category == "meal_plan":
        get_plans_sql = text(
            "SELECT meal_plan_id AS id, details, duration FROM meal_plan"
        )
    elif plan_category == "recovery_plan":
        get_plans_sql = text(
            "SELECT recovery_plan_id AS id, details, duration FROM recovery_plan"
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
async def delete_plan(plan_recv: PlanRecv, current_user: User = Depends(get_current_active_user),
                      db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=401, detail="only admin can delete plan")
    delete_plan(db, plan_recv)

    return {
        "status": "success",
        "details": "delete plan success"
    }


@router.get("/get_plans", response_model=PlanResp)
async def get_plans(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=401, detail="only admin can get plans")
    meal_plan_res = get_plans_in_db(db, "meal_plan")
    recovery_plan_res = get_plans_in_db(db, "recovery_plan")
    return PlanResp(meal_plan=meal_plan_res, recovery_plan=recovery_plan_res)
