from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import get_current_active_user
from auth_schema import User
from database import get_db
from model import Client


router = APIRouter()


@router.post("/update_client_status")
async def update_client_status(client_id: int, status: int, db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_active_user)):
    if current_user.role != "admin":
        return {"status": 401, "details": "only admin can update client status"}

    client = db.query(Client).filter(Client.id == client_id).first()
    if client is None:
        return {"status": 404, "details": "client not found"}

    client.status = status
    db.commit()
    return {"status": 200, "details": "client status updated"}
