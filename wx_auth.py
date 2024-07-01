from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from typing import Any
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import declarative_base
import requests
import asyncio
import logging
import uvicorn
import datetime

# 初始化FastAPI应用
app = FastAPI()
logger = logging.getLogger("uvicorn.error")

# 企业微信配置
CORPID = 'ww8447d69cc3208638'  # 企业ID
CORPSECRET = 'epiYFjQgMk9BnJem5rmGNMTQUTlnSK7SRm-uCIbHAPg'  # 应用的凭证密钥
access_token = ''

# JWT配置
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
Base = declarative_base()
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 加密工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 可以根据需要限制特定来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 用户模型
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)  # 对于企业微信登录，可以为空
    user_details = Column(JSON, default={})  # 新增字段

Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# 获取企业微信 access_token
def get_qywx_access_token():
    global access_token
    url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={CORPID}&corpsecret={CORPSECRET}'
    response = requests.get(url)
    data = response.json()
    if data['errcode'] == 0:
        access_token = data['access_token']
        logger.info(f"Successfully obtained access_token: {access_token}")
    else:
        logger.error(f"Failed to obtain access_token: {data['errmsg']}")

@app.on_event("startup")
async def startup_event():
    get_qywx_access_token()
    asyncio.create_task(refresh_access_token())

async def refresh_access_token():
    while True:
        await asyncio.sleep(7000)  # 提前刷新 access_token，避免因过期导致调用失败
        get_qywx_access_token()

# 生成JWT token
def create_access_token(data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 获取当前用户
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# 企业微信用户信息回调
@app.post("/qw/user")
async def wechat_callback(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    code = data.get('code')
    get_user_info_url = f'https://qyapi.weixin.qq.com/cgi-bin/auth/getuserinfo?access_token={access_token}&code={code}'
    user_info = requests.get(get_user_info_url).json()
    user_id = user_info['userid']
    # user_name = user_info.get('name', '')  # 获取用户名
    get_user_detail_url = f'https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token={access_token}&userid={user_id}'
    user_detail = requests.get(get_user_detail_url).json()
    
    # 更新用户详情到数据库
    user = db.query(User).filter(User.username == user_id).first()
    if user:
        user.user_details = user_detail
        db.commit()
        db.refresh(user)
    else:
        user = User(username=user_id, user_details=user_detail)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # 生成JWT token
    user_name = user.user_details.get('name', '')
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"UserId": user_id, "Name": user_name, "Token": token}

# 受保护的端点
@app.get("/protected-endpoint")
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.username}! This is a protected endpoint."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=45628, ssl_keyfile="/etc/nginx/ssl/db.yun.store.key", ssl_certfile="/etc/nginx/ssl/db.yun.store.pem", log_level="debug")
