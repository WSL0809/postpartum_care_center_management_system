from fastapi import FastAPI, Request
import requests
import asyncio
import logging

app = FastAPI()
logger = logging.getLogger("uvicorn.error")

CORPID = 'ww8447d69cc3208638'  # 企业ID
CORPSECRET = 'epiYFjQgMk9BnJem5rmGNMTQUTlnSK7SRm-uCIbHAPg'  # 应用的凭证密钥
access_token = ''


def get_access_token():
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
    get_access_token()
    asyncio.create_task(refresh_access_token())

async def refresh_access_token():
    while True:
        await asyncio.sleep(7000)  # 提前刷新 access_token，避免因过期导致调用失败
        get_access_token()

@app.get("/wechat/callback")
async def wechat_callback(request: Request):
    code = request.query_params.get('code')
    state = request.query_params.get('state')

    url = f'https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo?access_token={access_token}&code={code}'

    response = requests.get(url)
    user_info = response.json()

    return user_info

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)