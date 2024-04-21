from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette import status

from auth import get_current_active_user
from auth_schema import User
from config import ClientStatus, RoomStatus
from database import get_db
from model import Client

router = APIRouter()


@router.post("/allocate_room_by_client_id")
async def allocate_room_by_client_id(client_id: int, room_number: str, current_user: User = Depends(get_current_active_user),
                                      db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    client = db.query(Client).filter(Client.id == client_id).first()
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )

    if client.status != ClientStatus.manual_create.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="此用户并非手动添加，无法分配房间",
        )

    if client.room is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="此用户已分配房间",
        )
    check_room_status = text(
        """
        SELECT status FROM room WHERE room_number = :room
        """
    )
    room_status = db.execute(check_room_status, {"room": room_number}).first()
    if room_status is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if room_status[0] == RoomStatus.Occupied.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="此房间已被占用",
        )
    update_client_sql = text(
        """
        UPDATE client
        SET room = :room
        WHERE id = :client_id
        """
    )
    db.execute(update_client_sql, {"room": room_number, "client_id": client_id})
    db.commit()

    return {"status_code": status.HTTP_200_OK, "detail": "分配成功"}