from typing import Union, List, Dict, Optional

from fastapi import Depends, APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from auth import get_current_active_user
from auth_schema import User
from database import get_db
from model import Client
from schema import ClientBase, Baby
import re

router = APIRouter()


class Pagination(BaseModel):
    page: int
    limit: int
    total: int


class ClientGet(BaseModel):
    id: int
    status: Union[None, str]
    name: str
    tel: str
    age: int
    scheduled_date: str
    check_in_date: Union[str, None]
    hospital_for_childbirth: str
    contact_name: str
    contact_tel: str
    babies: List[Baby]
    meal_plan_id: int
    recovery_plan_id: Optional[int] = None
    mode_of_delivery: str
    assigned_baby_nurse: Union[int, None]
    room: Union[str, None]
    due_date: Union[str, None]
    # class Config:
    #     from_attributes=True
    #     orm_mode = True


class GetAllClientsResp(BaseModel):
    status: Union[str, int]
    details: str
    clients: List[ClientGet]
    pagination: Pagination


def clean_input(input_string):
    cleaned = input_string.strip()

    cleaned = re.sub(r'\s+', '', cleaned)
    cleaned = cleaned.replace('\n', '').replace('\t', '').replace('%20', ' ')
    return cleaned


# def get_clients(db: Session, name: Optional[str], page: int, limit: int):
#     # 计算起始记录
#
#     offset = (page - 1) * limit
#
#     query = db.query(Client)
#     if name:
#         name = clean_input(name)
#         query = query.filter(Client.name.ilike(f"%{name}%"))
#
#     # 查询客户数据
#     clients = query.offset(offset).limit(limit).all()
#
#     clients_data = [ClientGet.from_orm(client) for client in clients]
#
#     # 计算总记录数
#     total = query.count()
#     print(total)
#     return total, clients_data


from sqlalchemy import text
from sqlalchemy.orm import Session


def get_clients(db: Session, name: Optional[str], page: int, limit: int):
    # 基础查询语句，始终包含 GROUP BY
    base_query = """
    SELECT c.id, c.status, c.name, c.tel, c.age, c.scheduled_date, c.check_in_date, c.hospital_for_childbirth, 
           c.contact_name, c.contact_tel, c.meal_plan_id, c.recovery_plan_id, c.mode_of_delivery, 
           c.assigned_baby_nurse, c.room, c.due_date, json_agg(b.*) as babies
    FROM client c
    LEFT JOIN baby b ON c.id = b.client_id
    """

    # 构建 WHERE 子句和完整的查询
    if name:
        where_clause = "WHERE c.name ILIKE :name"
        full_query = f"""
        {base_query}
        {where_clause}
        GROUP BY c.id
        ORDER BY c.id
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
        """
        count_query = f"SELECT COUNT(DISTINCT c.id) FROM clients c {where_clause}"
        params = {'name': f'%{name}%', 'offset': (page - 1) * limit, 'limit': limit}
    else:
        full_query = f"""
        {base_query}
        GROUP BY c.id
        ORDER BY c.id
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
        """
        count_query = "SELECT COUNT(DISTINCT c.id) FROM client c"
        params = {'offset': (page - 1) * limit, 'limit': limit}

    try:
        # 执行查询
        clients = db.execute(text(full_query), params).mappings().all()

        # 计算总数
        total = db.execute(text(count_query), {'name': f'%{name}%'} if name else {}).scalar()

        return total, clients
    except Exception as e:
        print(f"Error fetching clients: {e}")
        return 0, []


@router.get("/get_clients", response_model=GetAllClientsResp)
def get_clients_by_name(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db),
                        name: Optional[str] = Query(None), page: int = 1, limit: int = 10):
    if current_user.role != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")

    total, clients = get_clients(db, name, page, limit)
    if not clients:
        raise HTTPException(status_code=404, detail="Clients not found")

    pagination = {
        "page": page,
        "limit": limit,
        "total": total
    }

    return {
        "status": "success",
        "details": "Clients fetched successfully.",
        "clients": clients,
        "pagination": pagination
    }
