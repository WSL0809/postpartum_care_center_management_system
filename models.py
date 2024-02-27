from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, LargeBinary, Date
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

    id = Column(Integer, primary_key=True)  # id_card
    name = Column(String)
    age = Column(Integer)
    tel = Column(String)
    address = Column(String)
    picture = Column(String)

    rooms = relationship("Room", back_populates="baby_nurse")  # 维护与Room的反向关系


class Room(Base):
    __tablename__ = "room"

    id = Column(Integer, primary_key=True)
    assigned_nurse_id = Column(Integer, ForeignKey("baby_nurse.id"))
    status = Column(String)
    meal_plan_id = Column(Integer, ForeignKey("meal_plan.id"))
    recovery_plan_id = Column(Integer, ForeignKey("recovery_plan.id"))
    check_in_date = Column(Date)

    baby_nurse = relationship("BabyNurse", back_populates="rooms")
    meal_plan = relationship("MealPlan", back_populates="rooms")
    recovery_plan = relationship("RecoveryPlan", back_populates="rooms")


class MealPlan(Base):
    __tablename__ = "meal_plan"

    id = Column(Integer, primary_key=True)
    details = Column(String)


    # 反向关系
    rooms = relationship("Room", back_populates="meal_plan")


class RecoveryPlan(Base):
    __tablename__ = "recovery_plan"

    id = Column(Integer, primary_key=True)
    details = Column(String)

    # 反向关系
    rooms = relationship("Room", back_populates="recovery_plan")
