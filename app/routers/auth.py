import jwt
import pymysql

from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from sqlalchemy.orm.session import Session
from starlette.responses import JSONResponse

from app.database import get_db
from app.models import AuthType
from app.routers.modules.auth_module import AuthModule
from app.schemas import AuthBasicSignupSchema, AuthLoginSchema, AuthRefreshTokenSchema, AuthSocialSignupSchema


router = APIRouter()
SECRET_KEY = 'secret_key'  # 임시


@router.post("/login/basic")
async def login_temp(
    data: AuthLoginSchema,
    db: Session = Depends(get_db),
):
    return AuthModule.basic_login(data, db)


@router.post("/signup/basic")
async def basic_signup(
    data: AuthBasicSignupSchema,
    db: Session = Depends(get_db),
):
    return AuthModule.basic_signup(data, db)


@router.post("/signup/social")
async def social_signup(
    data: AuthSocialSignupSchema,
    db: Session = Depends(get_db),
):
    return AuthModule.social_signup(data, db)


@router.post("/tokens/refresh")
async def refresh_token(
    data: AuthRefreshTokenSchema,
    db: Session = Depends(get_db),
):
    pass


@router.get("/login", status_code=200)
async def login(auth_type: AuthType, username: str = None, password: str = None, token_id: str = None):

    if (username is None) or (password is None):  # 둘 중 하나라도 입력되지 않으면 400 반환
        return JSONResponse(status_code=400, content=dict(msg="ID or PW Not Provided"))

    try:
        conn = pymysql.connect(host='localhost', user='root', password='1234!', db='funcktionsql', charset='utf8')  # 임시
        cur = conn.cursor(pymysql.cursors.DictCursor)

        cur.execute('SELECT id, username, password FROM Users WHERE username = %s', username)
        info = cur.fetchone()

        if info is None:  # 계정 존재여부 확인
            return JSONResponse(status_code=400, content=dict(msg="NO MATCH USER"))
        else:
            if info['password'] != password:  # 비밀번호 일치여부 확인
                return JSONResponse(status_code=400, content=dict(msg="NO MATCH USER"))
            if auth_type != AuthType.BASIC:  # 소셜 로그인인 경우 auth_key 확인
                cur.execute('SELECT auth_key FROM Auth WHERE user_id = %s', int(info['id']))
                if token_id != cur.fetchone()['auth_key']:
                    return JSONResponse(status_code=400, content=dict(msg="NO MATCH USER3"))

    finally:
        cur.close()
        conn.close()

    token = create_access_token(username, int(info['id']))
    create_refresh_token(username, int(info['id']))
    return JSONResponse(status_code=200, content=token)  # token 반환


@router.get("/register", status_code=200)
async def register(username, password, auth_type: AuthType, token_id: str = None):
    try:
        conn = pymysql.connect(host='localhost', user='root', password='1234', db='funcktionsql', charset='utf8')  # 임시
        cur = conn.cursor(pymysql.cursors.DictCursor)

        cur.execute('SELECT * FROM Users WHERE username=%s', username)
        exist = cur.fetchone()
        if exist is not None:
            return JSONResponse(status_code=400, content=dict(msg="Unavailable ID"))

        cur.execute('INSERT INTO Users (username, password) VALUES (%s,%s)', (username, password))
        conn.commit()
        cur.execute('SELECT id FROM Users WHERE username=%s', username)
        user_id = cur.fetchone()['id']
        cur.execute('INSERT INTO Auth (user_id, type, auth_key) VALUES (%s, %s, %s)', (user_id, int(auth_type), token_id))
        conn.commit()

    finally:
        cur.close()
        conn.close()

    return JSONResponse(status_code=200, content=dict(msg="Success"))


def create_access_token(username, user_id):
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=2)
    }
    access_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return access_token


def create_refresh_token(username, user_id):
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=24*7)
    }
    refresh_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    try:
        conn = pymysql.connect(host='localhost', user='root', password='1234', db='funcktionsql', charset='utf8')  # 임시
        cur = conn.cursor(pymysql.cursors.DictCursor)

        cur.execute('UPDATE Auth SET refresh_token = %s WHERE user_id = %s', (refresh_token, user_id))
        conn.commit()
    finally:
        cur.close()
        conn.close()
