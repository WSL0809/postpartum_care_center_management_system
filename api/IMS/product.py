from datetime import datetime
from typing import Union, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

import model
from database import get_db

router = APIRouter()


class ProductCreate(BaseModel):
    name: str
    quantity: int
    price: float
    note: Union[str, None] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    quantity: int
    price: float
    note: Union[str, None] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class LogResponse(BaseModel):
    id: int
    product_id: int
    user_id: int
    operation: str
    quantity_changed: int
    timestamp: datetime

    class Config:
        orm_mode = True


def update_product_quantity(db, product_id, quantity):
    db_product = db.query(model.Product).filter(model.Product.id == product_id).first()
    db_product.quantity = quantity
    db.commit()
    db.refresh(db_product)
    return db_product


def do_get_all_products(db):
    return db.query(model.Product).all()


@router.post("/IMS/create_product", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = model.Product(name=product.name, quantity=product.quantity, price=product.price, note=product.note)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/IMS/get_all_products", response_model=List[ProductResponse])
async def get_all_products(db: Session = Depends(get_db)):
    return do_get_all_products(db)


@router.post("/IMS/update_product_quantity", response_model=ProductResponse)
async def update_product(product_id: int, quantity: int, db: Session = Depends(get_db)):
    return update_product_quantity(db, product_id, quantity)
