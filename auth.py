import asyncio
import logging
from typing import Any, Callable
from jose import jwt, JWTError
from sqlalchemy.orm import Session

import model
import utils
from auth_schema import TokenData, User
from database import get_db

from functools import wraps
from fastapi import Depends, HTTPException, status

# 设置日志记录
logger = logging.getLogger(__name__)

def default_check_func(user_detail: dict, required_roles: list) -> bool:
    # 使用 isleader 字段进行权限验证
    # 如果 isleader 字段为 0 或在 required_roles 中，则允许访问
    return user_detail.get("isleader") == 0 or user_detail.get("isleader") in required_roles

def roles_required(*required_roles, check_func: Callable[[dict, list], bool] = None):
    if check_func is None:
        check_func = default_check_func

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, current_user: Any = Depends(get_current_active_user), db: Session = Depends(get_db), **kwargs):
            user_detail = current_user.user_detail
            if not check_func(user_detail, required_roles):
                logger.warning(f"User {current_user.username} with details {user_detail} attempted to access a restricted route.")
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
            return await func(*args, current_user=current_user, db=db, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, current_user: Any = Depends(get_current_active_user), db: Session = Depends(get_db), **kwargs):
            user_detail = current_user.user_detail
            if not check_func(user_detail, required_roles):
                logger.warning(f"User {current_user.username} with details {user_detail} attempted to access a restricted route.")
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
            return func(*args, current_user=current_user, db=db, **kwargs)
        
        # 根据函数是否是异步的选择合适的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
        
    return decorator
# def roles_required(*required_roles):
#     def decorator(func):
#         @wraps(func)
#         async def wrapper(*args, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db), **kwargs):
#             if current_user.role not in required_roles:
#                 raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
#             return await func(*args, current_user=current_user, db=db, **kwargs)
#         return wrapper
#     return decorator


def get_user(db: Session, user_name: str):
    return db.query(model.User).filter(model.User.username == user_name).first()


def get_current_user(
        token: str = Depends(utils.oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, utils.SECRET_KEY, algorithms=[utils.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user(db, token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user
