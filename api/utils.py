import asyncio
from datetime import datetime, timedelta, timezone
import os
from typing import Union
import requests
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from jose import jwt
import utils

def exception_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as e:
            # 这里处理 SQLAlchemy 相关的异常
            print(f"Database error occurred: {e}")
            # 可以选择重新抛出异常或返回一个错误信息
            raise
        except Exception as e:
            # 处理其他异常
            print(f"An error occurred: {e}")
            raise

    return wrapper


# 从企业微信获取access_token


def get_qywx_access_token():
    global access_token, CORPID, CORPSECRET
    CORPID = os.getenv("CORPID")
    CORPSECRET = os.getenv("CORPSECRET")
    url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={CORPID}&corpsecret={CORPSECRET}'
    response = requests.get(url)
    data = response.json()
    if data['errcode'] == 0:
        access_token = data['access_token']
        os.environ["access_token"] = access_token
        return (f"Successfully obtained access_token: {access_token}")
    else:
        return(f"Failed to obtain access_token: {data['errmsg']}")
    
    
async def refresh_access_token():
    while True:
        print("refresh_access_token")
        await asyncio.sleep(7000)  # 提前刷新 access_token，避免因过期导致调用失败
        get_qywx_access_token()

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, utils.SECRET_KEY, algorithm=utils.ALGORITHM)
    return encoded_jwt
