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
