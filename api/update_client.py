from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import get_current_active_user, roles_required
from auth_schema import User
from database import get_db
from model import Client

router = APIRouter()


class UpdateClientStatusRecv(BaseModel):
    client_id: int
    status: int


@router.post("/update_client_status")
async def update_client_status(recv: UpdateClientStatusRecv, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == recv.client_id).first()
    if client is None:
        return {"status": 404, "details": "client not found"}

    client.status = recv.status
    db.commit()
    return {"status": 200, "details": "client status updated"}


@router.post("/update_client_meal_plan")
async def update_client_meal_plan(recv: UpdateClientStatusRecv, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == recv.client_id).first()
    if client is None:
        return {"status": 404, "details": "client not found"}

    client.meal_plan = recv.status
    db.commit()
    return {"status": 200, "details": "client meal plan updated"}
