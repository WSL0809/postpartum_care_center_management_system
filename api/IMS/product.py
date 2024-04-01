from datetime import datetime
from functools import wraps
from typing import Union, List, Dict

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

import model
from auth import get_current_active_user
from auth_schema import User
from database import get_db
from model import Log

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
    product_name: str
    user_name: str
    user_role: str
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


def log_user_activity(action: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            print("Log user activity")
            db = kwargs.get('db', None) or next((arg for arg in args if isinstance(arg, Session)), None)
            current_user: User = kwargs.get('current_user', None) or next(
                (arg for arg in args if isinstance(arg, User)), None)

            # 在函数调用之前，product_id是未知的
            product_id = None
            quantity_changed = 0
            if db is None or current_user is None:
                raise ValueError("DB session or current user not provided")

            result = await func(*args, **kwargs)

            if isinstance(result, model.Product):
                product_id = result.id
                quantity_changed = result.quantity

            if db and current_user and product_id is not None:
                log_entry = Log(
                    product_id=product_id,
                    user_id=current_user.id,
                    operation=action,
                    quantity_changed=quantity_changed,
                    timestamp=datetime.now()
                )
                db.add(log_entry)
                db.commit()

            return result

        return wrapper

    return decorator


@router.post("/IMS/create_product", response_model=ProductResponse)
@log_user_activity("创建新货物")
async def create_product(product: ProductCreate, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_active_user)):
    if current_user.role != "admin":
        raise ValueError("Only admins are allowed to create products")
    db_product = model.Product(name=product.name, quantity=product.quantity, price=product.price, note=product.note)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/IMS/get_all_products", response_model=List[ProductResponse])
async def get_all_products(db: Session = Depends(get_db)):
    return do_get_all_products(db)


@router.post("/IMS/update_product_quantity", response_model=ProductResponse)
@log_user_activity("更新货物数量")
async def update_product(product_id: int, quantity: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    if current_user.role != "admin":
        raise ValueError("Only admins are allowed to update products")
    return update_product_quantity(db, product_id, quantity)


@router.get("/IMS/get_all_logs")
async def get_all_logs(
    db: Session = Depends(get_db),
    page: int = Query(1, description="Page number starting from 1"),
    page_size: int = Query(10, description="Number of items per page")
):
    skip = (page - 1) * page_size

    query_log_sql = text(
        """
        select log.operation, log.quantity_changed, log.timestamp, 
        p.name as product_name, u.username as user_name, u.role as user_role
        from log
        left join public.users u on log.user_id = u.id
        left join public.product p on log.product_id = p.id
        offset :skip limit :page_size
        """
    )
    logs = db.execute(query_log_sql, {"skip": skip, "page_size": page_size}).mappings().all()
    logs_query = db.query(model.Log)

    total_items = logs_query.count()
    total_pages = (total_items + page_size - 1) // page_size
    return {
        "logs": logs,
        "total_items": total_items,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
    }
