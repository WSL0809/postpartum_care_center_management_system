from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, LargeBinary
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String)
    role = Column(String, default="admin")
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)


class BabyNurse(Base):
    __tablename__ = "baby_nurse"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    tel = Column(String)
    address = Column(String)
    picture = Column(LargeBinary)

    rooms = relationship("Room", back_populates="baby_nurse")


class Room(Base):
    __tablename__ = "room"

    id = Column(Integer, primary_key=True)
    assigned_nurse_id = Column(Integer, ForeignKey("baby_nurse.id"))
    status = Column(String)

    baby_nurse = relationship("BabyNurse", back_populates="rooms")
