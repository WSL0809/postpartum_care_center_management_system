import os
from typing import Union
from pydantic import BaseModel
import requests
import hashlib
import hmac
import base64
import time
import json
from fastapi import APIRouter, Depends, HTTPException
from auth import get_current_active_user
from auth_schema import WxUser

router = APIRouter()
CORPID = os.getenv("CORPID")
CORPSECRET = os.getenv("CORPSECRET")
ROBOT_MANAGER_BASE_URL = "https://bot.yzys.cc/api"

"""
1. 从环境变量获取当前用户所属企业的 corp_id
2. 获取企业微信群机器人管理系统的access_token
"""

class MessageRecv(BaseModel):

    id: Union[int, str]
    content: Union[str, None]

async def get_robots_manager_access_token() -> dict:
    """
    获取企业微信群机器人管理系统的access_token
    :return:
    """
    # 获取企业微信群机器人管理系统的access_token
    apply_key_url = f"{ROBOT_MANAGER_BASE_URL}/open/apply"
    payload = {
        "name": "postpartum_care_center_management_system",
        "corpId": CORPID,
        "corpSecret": CORPSECRET,
    }
    
    _res = requests.post(apply_key_url, json=payload)
    
    # keys = requests.get(f'{apply_key_url}?corpId={CORPID}')
    keys_to_keep = ["openAccessKey", "openSecret"]
    keys_response = requests.get(f'{apply_key_url}?corpId={CORPID}')
    keys = keys_response.json()
    cleaned_data = {k: v for k, v in keys["data"].items() if k in keys_to_keep}
    return cleaned_data
    
def generate_signature(secret_key, string_to_sign):
    # 使用HMAC-SHA256生成签名
    signature = hmac.new(base64.b64decode(secret_key), string_to_sign.encode('utf-8'), hashlib.sha256).digest()
    return base64.b64encode(signature).decode('utf-8')

def build_headers(timestamp, access_key, secret, message):
    string_to_sign = f"{timestamp}\n{access_key}\n{ROBOT_MANAGER_BASE_URL}/open/send\n{json.dumps(message)}"
    signature = generate_signature(secret, string_to_sign)
    return {
        "Content-Type": "application/json",
        "AccessKey": access_key,
        "Authorization": signature,
        "Timestamp": timestamp,
        "Secret": secret
    }
@router.post("/send_message_to_robot")
async def send_message_to_robot(message: MessageRecv, current_user: WxUser = Depends(get_current_active_user)):
    if current_user.user_detail.get("enable") == 0:
        raise HTTPException(status_code=403, detail="User is disabled.")
    
    if not message:  # 检查消息内容是否为空
        raise ValueError("Message content cannot be empty.")
    
    try:
        token_dict = await get_robots_manager_access_token()
        access_key, secret = token_dict.values()  # 直接解构以获得更清晰的变量名
        print(access_key, secret)
        if not all([access_key, secret]):
            raise ValueError("Access key or secret is missing.")
        
        timestamp = str(int(time.perf_counter()))  # 使用更高精度的时间戳
        headers = build_headers(timestamp, access_key, secret, message.content)
        
        # 使用try-except处理requests可能抛出的异常
        response = requests.post(f"{ROBOT_MANAGER_BASE_URL}/open/bot/send", headers=headers, json=message.model_dump(mode='json'))
        response.raise_for_status()  # 检查响应状态码
        
    except requests.RequestException as e:
        # 这里可以记录日志或执行其他错误处理逻辑
        print(f"Failed to send message: {e}")
        return None  # 或者根据实际情况抛出异常或返回错误信息
    
    # 如果执行到这里，表示请求成功
    print("Message sent successfully.")
    return response.json()  # 假设API返回的是JSON格式的数据
