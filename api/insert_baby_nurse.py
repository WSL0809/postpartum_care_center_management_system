from typing import Optional, Union

from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from pydantic import BaseModel
from starlette import status
from model import BabyNurse

from auth import get_current_active_user
from auth_schema import User
from database import get_db

router = APIRouter()


class InsertBabyNurseRecv(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    tel: Optional[str] = None
    address: Optional[str] = None
    id_number: Optional[str] = None
    childcare_certificate: Optional[str] = None
    permanent_address: Optional[str] = None
    level: Optional[str] = None
    mark: Optional[str] = None
    work_status: Optional[str] = None

    class Config:
        orm_mode = True


class InsertBabyNurseResp(BaseModel):
    status: Union[str, int]
    details: str


@router.post("/insert_baby_nurse", response_model=InsertBabyNurseResp)
def insert_baby_nurse(baby_nurse_recv: InsertBabyNurseRecv, current_user: User = Depends(get_current_active_user),
                      db: Session = Depends(get_db)):
    if current_user.role != "admin":
        return InsertBabyNurseResp(status=status.HTTP_401_UNAUTHORIZED, details="only admin can insert baby_nurse")
    baby_nurse = BabyNurse(**dict(baby_nurse_recv))
    try:
        db.add(baby_nurse)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        return InsertBabyNurseResp(status=status.HTTP_500_INTERNAL_SERVER_ERROR, details=f"insert baby_nurse failed because: {e}")
    return InsertBabyNurseResp(status=status.HTTP_200_OK, details="insert baby_nurse success")
