from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from database import Base


class Room(Base):
    __tablename__ = "room"

    id = Column(Integer, primary_key=True)
    room_number = Column(String(255), unique=True, nullable=False, index=True)
    status = Column(String(255), default="0", nullable=False)
    client_id = Column(Integer, ForeignKey("client.id"))
    recently_used = Column(String(255))
    notes = Column(String(255))
    fault_list = Column(JSONB)
