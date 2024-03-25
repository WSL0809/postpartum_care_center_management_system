from datetime import datetime
from typing import Union

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel
from starlette import status
from auth import get_current_active_user
from auth_schema import User
from database import get_db

router = APIRouter()


class ReminderResp(BaseModel):
    name: str
    age: Union[int, str]
    tel: str
    remind_content: str

    class Config:
        orm_mode = True


def pick_clients_by_birthday(db: Session):
    # 获取今天的日期，格式为 MMDD
    today = datetime.today().strftime('%m%d')

    query = text("SELECT name, age, tel FROM client WHERE SUBSTRING(id_number, 11, 4) = :today")

    clients_birthday_today = db.execute(query, {'today': today}).mappings().all()

    return clients_birthday_today


def pick_babies_by_birthday(db: Session):
    # 获取今天的日期，格式为 MMDD
    today = datetime.today().strftime('%Y-%m-%d')

    get_baby_mom = text("SELECT c.name, b.birth_date, c.tel FROM client c JOIN baby b ON c.id = b.client_id WHERE "
                        "SUBSTRING(b.birth_date, 6, 5) = :today")

    clients_birthday_today = db.execute(get_baby_mom, {'today': today}).mappings().all()

    return clients_birthday_today


@router.get("/get_reminder", response_model=list[ReminderResp])
async def get_reminder(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    resp = [ReminderResp(**dict(row), **{"remind_content": "宝妈生日"}) for row in pick_clients_by_birthday(db)]
    resp.extend([ReminderResp(**dict(row), **{"remind_content": "宝宝生日"}) for row in pick_babies_by_birthday(db)])
    return resp
