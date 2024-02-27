from sqlalchemy.orm import Session
from utils import get_password_hash, verify_password
import models
import schemas


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
