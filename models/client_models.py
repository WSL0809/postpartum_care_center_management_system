from sqlalchemy import DECIMAL, Column, ForeignKey, Integer, String, Text, Date
from sqlalchemy.orm import relationship

from database import Base


class Client(Base):
    __tablename__ = "client"

    id = Column(Integer, primary_key=True)
    meal_plan_id = Column(Integer, ForeignKey("meal_plan.meal_plan_id"))
    recovery_plan_id = Column(Integer, ForeignKey("recovery_plan.recovery_plan_id"))
    assigned_baby_nurse = Column(Integer, ForeignKey("baby_nurse.baby_nurse_id"))
    name = Column(String(255), nullable=False)
    tel = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    scheduled_date = Column(Date, nullable=False)
    check_in_date = Column(Date, nullable=False)
    hospital_for_childbirth = Column(String(255), nullable=False)
    contact_name = Column(String(255), nullable=False)
    contact_tel = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    
    babies = relationship("Baby", backref="client")
    nurses = relationship("ClientBabyNurse", backref="client")
    meal_plan = relationship("MealPlan", back_populates="clients")
    recovery_plan = relationship("RecoveryPlan", back_populates="clients")
    baby_nurses = relationship(
        "BabyNurse", secondary="client_baby_nurse", back_populates="clients"
    )


class BabyNurse(Base):
    __tablename__ = "baby_nurse"

    baby_nurse_id = Column(Integer, primary_key=True)
    name = Column(String(255))
    age = Column(Integer)
    tel = Column(String(255))
    address = Column(String(255))
    id_number = Column(String(255))
    photo = Column(String(255))

    clients = relationship(
        "Client", secondary="client_baby_nurse", back_populates="baby_nurses"
    )


class MealPlan(Base):
    __tablename__ = "meal_plan"
    meal_plan_id = Column(Integer, primary_key=True)
    details = Column(Text)
    duration = Column(Integer)

    clients = relationship("Client", back_populates="meal_plan")


class RecoveryPlan(Base):
    __tablename__ = "recovery_plan"
    recovery_plan_id = Column(Integer, primary_key=True)
    details = Column(Text)
    duration = Column(Integer)

    clients = relationship("Client", back_populates="recovery_plan")


class Baby(Base):
    __tablename__ = "baby"
    baby_id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("client.id"))
    name = Column(String(255), nullable=False)
    gender = Column(String(1), nullable=False)
    birth_date = Column(Date, nullable=False)
    birth_weight = Column(DECIMAL(5, 2), nullable=False)
    birth_height = Column(DECIMAL(5, 2), nullable=False)
    health_status = Column(String(255), nullable=False)
    birth_certificate = Column(String(255), nullable=False)
    remarks = Column(Text)
    mom_id_number = Column(Text, nullable=False)
    dad_id_number = Column(Text, nullable=False)


class ClientBabyNurse(Base):
    __tablename__ = "client_baby_nurse"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("client.id"))
    baby_nurse_id = Column(Integer, ForeignKey("baby_nurse.baby_nurse_id"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(255), nullable=False)

    client = relationship("Client", backref="client_baby_nurse")
    baby_nurse = relationship("BabyNurse", backref="client_baby_nurse")
