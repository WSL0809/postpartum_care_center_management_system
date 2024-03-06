from pydantic import BaseModel

import model


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

def client_to_client_base(room: model.Room):
    return RoomInDb(
        id=room.id,
        client_id=room.client_id,
        status=room.status,
        recently_used=room.recently_used,
        notes=room.notes
    )
