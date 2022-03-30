import jwt
import pymysql

from fastapi import APIRouter
from datetime import datetime, timedelta
from starlette.responses import JSONResponse

from app.models import AuthType


router = APIRouter()
SECRET_KEY = 'secret_key'  # 임시


@router.get("/login", status_code=200)
async def login(auth_type: AuthType, username: str = None, password: str = None, token_id=None):
    if (username is None) or (password is None):  # 둘 중 하나라도 입력되지 않으면 400 반환
        return JSONResponse(status_code=400, content=dict(msg="ID or PW Not Provided"))

    try:
        conn = pymysql.connect(host='localhost', user='root', password='1234', db='funcktionsql', charset='utf8')  # 임시
        cur = conn.cursor(pymysql.cursors.DictCursor)

        sql = 'SELECT id, username, password FROM Users WHERE username=%s'
        cur.execute(sql, username)
        info = cur.fetchone()
        if info is None:  # 계정 존재 확인
            return JSONResponse(status_code=400, content=dict(msg = "NO MATCH USER"))
        if info['password'] != password:  # 비밀번호 일치여부 확인
            return JSONResponse(status_code=400, content=dict(msg = "NO MATCH USER"))
        if auth_type != AuthType.NON_SOCIAL:  # 소셜 로그인인 경우 auth_key 확인
            sql = 'SELECT auth_key FROM Auth WHERE user_id=%d'
            cur.execute(sql, info['id'])
            if token_id != cur.fetchone():
                return JSONResponse(status_code=400, content=dict(msg = "NO MATCH USER"))
    finally:
        cur.close()
        conn.close()

    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=2)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')  # 토큰생성
    return JSONResponse(status_code=200, content=token)  # 토큰 반환

