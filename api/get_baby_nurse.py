from typing import Union, List, Dict, Optional

from fastapi import Depends, APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import get_current_active_user
from auth_schema import User
from database import get_db
from model import Client
from model.client import BabyNurse
from schema import ClientBase
from starlette import status
import re

router = APIRouter()


class BabyNurseModel(BaseModel):
    baby_nurse_id: Optional[int] = None
    name: Optional[str] = None
    age: Union[None, int] = None
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
        from_attributes = True


class Pagination(BaseModel):
    page: int
    limit: int
    total: int


class GetBabyNurseResp(BaseModel):
    status: Union[str, int]
    details: str
    clients: Union[List[BabyNurseModel], None]
    pagination: Union[Pagination, None]


def clean_input(input_string):
    cleaned = input_string.strip()
    cleaned = re.sub(r'\s+', '', cleaned)
    cleaned = cleaned.replace('\n', '').replace('\t', '').replace('%20', ' ')
    return cleaned


def get_baby_nurses(db: Session, name: Optional[str], page: int, limit: int):
    # 计算起始记录
    offset = (page - 1) * limit
    query = db.query(BabyNurse)
    if name:
        name = clean_input(name)
        query = query.filter(BabyNurse.name.ilike(f"%{name}%"))
    # 查询客户数据
    baby_nurses = query.offset(offset).limit(limit).all()
    baby_nurse_data = [BabyNurseModel.from_orm(baby_nurse) for baby_nurse in baby_nurses]
    total = query.count()
    return total, baby_nurse_data


@router.get("/get_baby_nurse", response_model=GetBabyNurseResp)
def get_clients_by_name(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db),
                        name: Optional[str] = Query(None),
                        page: int = 1,
                        limit: int = 10):
    if current_user.role != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")

    total, baby_nurses = get_baby_nurses(db, name, page, limit)
    if not baby_nurses:
        return GetBabyNurseResp(
            status=status.HTTP_404_NOT_FOUND, details="BayNurse not found", clients=None, pagination=None
        )

    pagination = {
        "page": page,
        "limit": limit,
        "total": total
    }
    return GetBabyNurseResp(
        status=status.HTTP_200_OK, details="Clients fetched successfully.", clients=baby_nurses, pagination=pagination
    )
