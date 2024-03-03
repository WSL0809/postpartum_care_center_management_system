from sqlalchemy.orm import Session, joinedload
from utils import get_password_hash, verify_password
import models
import schemas
from models import Client
from sqlalchemy.exc import NoResultFound
from typing import Tuple, List


def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_user(db: Session, user_name: str):
    return db.query(models.User).filter(models.User.username == user_name).first()


def is_user_exits(db: Session, user_name: str):
    if db.query(models.User).filter(models.User.username == user_name).first():
        return True
    else:
        return False


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username, email=user.email, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_clients_by_name(
    db: Session, name: str, page: int, page_size: int
) -> Tuple[List[Client], int]:
    """
    根据名字分页查询客户信息。

    :param name: 客户名字
    :param page: 页码，从1开始
    :param page_size: 每页大小
    :return: (客户列表, 总客户数)
    """
    try:
        # 计算跳过的记录数
        offset = (page - 1) * page_size

        # 查询总数
        total = db.query(Client).filter(Client.name == name).count()

        # 分页查询
        clients = (
            db.query(Client)
            .filter(Client.name == name)
            .order_by(Client.id)
            .offset(offset)
            .limit(page_size)
            .options(
                joinedload(Client.babies),
                joinedload(Client.meal_plan),
                joinedload(Client.recovery_plan),
            )
            .all()
        )

        return clients, total
    except NoResultFound:
        return [], 0
    finally:
        db.close()
