from typing import Union, List, Dict

from fastapi import Depends, APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import get_current_active_user
from auth_schema import User
from database import get_db
from schema import ClientBase

router = APIRouter()


class GetAllClientsResp(BaseModel):
    status: Union[str, int]
    details: str
    clients: List[ClientBase]
    pagination: Dict


def get_clients_info(db):
    pass


@router.get("/get_all_clients")
def get_all_clients(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return get_clients_info(db)
