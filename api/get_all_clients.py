from typing import Union, List, Optional

from fastapi import Depends, APIRouter, HTTPException, Query
from pydantic import BaseModel

from auth import get_current_active_user
from auth_schema import User
from database import get_db
from schema import Baby
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
    babies: Union[List[Baby], None] = []
    meal_plan_id: int
    recovery_plan_id: Optional[int] = None
    mode_of_delivery: str
    assigned_baby_nurse: Union[int, None]
    room: Union[str, None]
    due_date: Union[str, None]
    transaction_price: Union[float, None]
    id_number: Union[str, None]


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


from sqlalchemy import text
from sqlalchemy.orm import Session


def get_clients(db: Session, name: Optional[str], page: int, limit: int):
    # 使用 COALESCE 函数确保 babies 字段至少为空数组
    base_query = """
    SELECT c.id, c.status, c.name, c.tel, c.age, c.scheduled_date, c.check_in_date, c.hospital_for_childbirth, 
           c.contact_name, c.contact_tel, c.meal_plan_id, c.recovery_plan_id, c.mode_of_delivery, 
           c.assigned_baby_nurse, c.room, c.due_date, c.transaction_price, c.id_number,
           COALESCE(json_agg(b.*) FILTER (WHERE b.baby_id IS NOT NULL), '[]') AS babies
    FROM client c
    LEFT JOIN baby b ON c.id = b.client_id
    """

    # 动态构建 WHERE 子句
    where_clause = "WHERE c.name ILIKE :name" if name else ""
    count_query = f"SELECT COUNT(DISTINCT c.id) FROM client c {where_clause}"

    # 分页和排序
    final_query = f"""
    {base_query}
    {where_clause}
    GROUP BY c.id
    ORDER BY c.id
    OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
    """

    try:
        params = {'name': f'%{name}%', 'offset': (page - 1) * limit, 'limit': limit} if name else {
            'offset': (page - 1) * limit, 'limit': limit}
        clients = db.execute(text(final_query), params).fetchall()
        total_params = {'name': f'%{name}%'} if name else {}
        total = db.execute(text(count_query), total_params).scalar()

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
