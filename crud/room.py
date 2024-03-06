from sqlalchemy import select
from sqlalchemy.orm import Session

import model
import schema


def get_all_rooms(db: Session):
    return db.query(model.Room).all()


def get_room_by_id(db: Session, room_id: int):
    query = select(model.Room.id, model.Room.status, model.Room.recently_used, model.Room.notes).where(model.Room.id == room_id)
    res = db.execute(query).first()
    if res is not None:
        id, status, recently_used, notes = db.execute(query).first()
    else:
        id, status, recently_used, notes = (-1, 'None', 'None', 'None')
    return schema.Room(id=id, status=status, recently_used=recently_used, notes=notes)
