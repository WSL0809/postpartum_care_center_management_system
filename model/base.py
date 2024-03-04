from sqlalchemy import DECIMAL, Column, ForeignKey, Integer, String, Text, Date, Boolean

from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String)
    role = Column(String, default="admin")
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
# class BabyNurse(Base):
#     __tablename__ = "baby_nurse"
#
#     baby_nurse_id = Column(Integer, primary_key=True)
#     name = Column(String(255))
#     age = Column(Integer)
#     tel = Column(String(255))
#     address = Column(String(255))
#     id_number = Column(String(255))
#     photo = Column(String(255))
#
#
# class MealPlan(Base):
#     __tablename__ = "meal_plan"
#     meal_plan_id = Column(Integer, primary_key=True)
#     details = Column(Text)
#     duration = Column(Integer)
#
#
# class RecoveryPlan(Base):
#     __tablename__ = "recovery_plan"
#     recovery_plan_id = Column(Integer, primary_key=True)
#     details = Column(Text)
#     duration = Column(Integer)
