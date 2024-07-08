from datetime import timedelta
import os
from fastapi import APIRouter, Depends, Request
import requests

from api.utils import create_access_token
from database import get_db
from sqlalchemy.orm import Session

from model.base import User


router = APIRouter()

@router.post("/qy_wechat_callback")
async def qy_wechat_callback(request: Request, db: Session = Depends(get_db)):
    global access_token
    access_token = os.getenv("access_token")
    data = await request.json()
    code = data.get('code')
    print(code)
    get_user_info_url = f'https://qyapi.weixin.qq.com/cgi-bin/auth/getuserinfo?access_token={access_token}&code={code}'
    user_info = requests.get(get_user_info_url).json()
    print(f'user_info: {user_info}')
    user_id = user_info['userid']
    # user_name = user_info.get('name', '')  # 获取用户名
    get_user_detail_url = f'https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token={access_token}&userid={user_id}'
    user_detail = requests.get(get_user_detail_url).json()
    print(f'user_detail: {user_detail}')
    user = db.query(User).filter(User.username == user_id).first()
    if user:
        user.user_detail = user_detail
        db.commit()
        db.refresh(user)
    else:
        user = User(username=user_id, user_detail=user_detail)
        db.add(user)
        db.commit()
        db.refresh(user)
    username = user.user_detail.get('name', '')
    access_token_expires = timedelta(minutes=7 * 60)
    access_token_resp = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"UserId": user_id, "Name": username, "Token": access_token_resp}
