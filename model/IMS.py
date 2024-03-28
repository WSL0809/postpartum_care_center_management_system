from sqlalchemy import DECIMAL, Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from database import Base


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, index=True)
    quantity = Column(Integer)
    price = Column(DECIMAL(precision=10, scale=2))
    note = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Log(Base):
    __tablename__ = "log"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("product.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    operation = Column(String(255))
    quantity_changed = Column(Integer)
    timestamp = Column(DateTime, default=func.now())

    product = relationship("Product", backref="logs")
    user = relationship("User", backref="logs")
