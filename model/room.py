from sqlalchemy import Column, ForeignKey, Integer, String

from database import Base


class Room(Base):
    __tablename__ = 'room'

    id = Column(Integer, primary_key=True)
    status = Column(String(255), default="0", nullable=False)
    client_id = Column(Integer, ForeignKey("client.id"), nullable=False)
    recently_used = Column(String(255))
    notes = Column(String(255))
