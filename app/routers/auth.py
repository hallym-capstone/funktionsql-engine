from fastapi import APIRouter, Depends
from app.models import AuthType
from datetime import datetime, timedelta
import jwt
from starlette.responses import JSONResponse
import pymysql


router = APIRouter()
SECRET_KEY = 'secret_key' #임시


@router.get("/login", status_code=200)
async def login(auth_type: AuthType, username: str = None, password: str = None, auth_key = None):
    if (username is None) or (password is None): #둘 중 하나라도 입력되지 않으면 400 반환
        return JSONResponse(status_code=400, content=dict(msg="ID or PW Not Provided"))
    is_exist = await is_info_check(username, password) #해당 계정이 존재하는지 확인
    if not is_exist: #존재하지 않는다면 400 반환
        return JSONResponse(status_code=400, content=dict(msg="NO MATCH USER"))
    payload = {
        'username':username,
        'exp': datetime.utcnow() + timedelta(hours= 2)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8') #토큰생성
    return JSONResponse(status_code=200, content = token) #토큰 반환

async def is_info_check(auth_type: AuthType, username: str,password: str,auth_key):
    try:
        conn = pymysql.connect(host='localhost', user='root', password='1234', db='funcktionsql', charset='utf8') #임시
        cur = conn.cursor(pymysql.cursors.DictCursor)

        sql = 'SELECT id, username, password FROM Users WHERE username=%s'
        cur.execute(sql, username)
        info = cur.fetchone()
        if info['username'] is None: #계정 존재 확인
            return False
        if info['password'] != password: #비밀번호 일치여부 확인
            return False
        if auth_type != AuthType.NON_SOCIAL: #소셜 로그인인 경우 auth_key 확인
            sql = 'SELECT auth_key FROM Auth WHERE user_id=%d'
            cur.execute(sql,info['id'])
            if auth_key != cur.fetchone():
                return False
        return True
    finally:
        cur.close()
        conn.close()
