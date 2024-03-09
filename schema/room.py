from typing import Optional

from pydantic import BaseModel

import model
import schema
from schema.client import ClientModel


class Room(BaseModel):
    id: int
    status: str
    recently_used: str
    notes: str


class RoomInDb(Room):
    client_id: int

    class Config:
        # orm_mode = True
        from_attributes = True


class RoomModel(BaseModel):
    room_number: str
    status: str
    client: ClientModel
    recently_used: Optional[str] = None
    notes: Optional[str] = None


class RoomClientModel(schema.ClientCreate):
    set_status: str


def client_to_client_base(room: model.Room):
    return RoomInDb(
        id=room.id,
        client_id=room.client_id,
        status=room.status,
        recently_used=room.recently_used,
        notes=room.notes,
    )
