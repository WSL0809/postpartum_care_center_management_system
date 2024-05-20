from jose import jwt, JWTError
from sqlalchemy.orm import Session

import model
import utils
from auth_schema import TokenData, User
from database import get_db

from functools import wraps
from fastapi import Depends, HTTPException, status


def roles_required(*required_roles):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db), **kwargs):
            if current_user.role not in required_roles:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
            return await func(*args, current_user=current_user, db=db, **kwargs)
        return wrapper
    return decorator


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
    if current_user.is_active:
        return current_user
    else:
        raise HTTPException(status_code=400, detail="Inactive user")
