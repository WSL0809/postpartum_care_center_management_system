from sqlalchemy import Column, Integer, String, Boolean
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
    double_check_password = Column(String(255), default="88888888")

    log = relationship("Log", backref="users")