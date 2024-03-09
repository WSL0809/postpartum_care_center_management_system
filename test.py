from sqlalchemy import select
from sqlalchemy.orm import Session

import model
import models
import schema
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

db = SessionLocal()


def get_room_by_id(db: Session, room_id: int):
    query = select(
        model.Room.id, model.Room.status, model.Room.recently_used, model.Room.notes
    ).where(model.Room.id == room_id)
    id, status, recently_used, notes = db.execute(query).first()
    return schema.Room(id=id, status=status, recently_used=recently_used, notes=notes)


result = get_room_by_id(db, 0)
print(result)
