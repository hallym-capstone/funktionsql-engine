import os
import jwt

from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta
from sqlalchemy.orm.session import Session
from fastapi import Request, status
from fastapi.exceptions import HTTPException
from passlib.context import CryptContext

from app.models import AuthType
from app.crud import create_auth, create_user, get_auth_by_user_id, get_user_by_username, update_auth_refresh_token_by_user_id
from app.schemas import (
    AuthBasicSignupSchema, AuthLoginResponse, AuthBasicLoginSchema, AuthRefreshTokenSchema,
    AuthSignupResponse, AuthSocialLoginSchema, AuthSocialSignupSchema, AuthTokenRefreshResponse,
)


env_path = Path("config") / ".env"
load_dotenv(dotenv_path=env_path)

ACCESS_TOKEN_EXP = 24 * 7
REFRESH_TOKEN_EXP = 24 * 30


class AuthModule:

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # login logic for basic users
    @classmethod
    def basic_login(cls, data: AuthBasicLoginSchema, db: Session):
        username = data.username
        password = data.password

        # search if user exists
        query_user = get_user_by_username(db, username)
        if not query_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="unauthorized user credentials")

        # verify if auth type is BASIC
        query_auth = get_auth_by_user_id(db, query_user.id)
        if query_auth.type != AuthType.BASIC.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="unauthorized user credentials")

        # verify if password matches
        if not cls.verify_password_hash(password, query_user.password):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="unauthorized user credentials")

        return AuthLoginResponse.load({
            "id": query_user.id,
            "username": query_user.username,
            "type": query_auth.type,
            "access_token": cls.generate_jwt_token(query_user.id, query_user.username, ACCESS_TOKEN_EXP),
            "refresh_token": cls.verify_exp_and_get_refresh_token(db, query_auth.refresh_token, query_user.id, query_user.username),
        })

    # login logic for social users
    @classmethod
    def social_login(cls, data: AuthSocialLoginSchema, db: Session):
        username = data.username
        auth_key = data.auth_key
        auth_type = data.auth_type

        # search if user exists
        query_user = get_user_by_username(db, username)
        if not query_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="unauthorized user credentials")

        # verify if auth credential matches
        query_auth = get_auth_by_user_id(db, query_user.id)
        if query_auth.type != auth_type or query_auth.auth_key != auth_key:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="unauthorized user credentials")

        return AuthLoginResponse.load({
            "id": query_user.id,
            "username": query_user.username,
            "type": query_auth.type,
            "access_token": cls.generate_jwt_token(query_user.id, query_user.username, ACCESS_TOKEN_EXP),
            "refresh_token": cls.verify_exp_and_get_refresh_token(db, query_auth.refresh_token, query_user.id, query_user.username),
        })

    # signup logic for basic users
    @classmethod
    def basic_signup(cls, data: AuthBasicSignupSchema, db: Session):
        # TODO: password policy
        username = data.username
        password = data.password
        confirm_password = data.confirm_password

        # search if user exists
        query_user = get_user_by_username(db, username)
        if query_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"username `{username}` is already used")

        # verify if password confirms
        if not cls.verify_password_confirmation(password, confirm_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"password confirmation does not match")

        try:
            # insert new user
            inserted_user = create_user(db, username, cls.get_password_hash(password))
            inserted_auth = create_auth(db, inserted_user.id, AuthType.BASIC.value, None, cls.generate_jwt_token(inserted_user.id, username, REFRESH_TOKEN_EXP))
            db.commit()

            return AuthSignupResponse.load(inserted_user.id, username, inserted_auth.type)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"unhandled error triggered: {str(e)}")

    # signup logic for social users
    @classmethod
    def social_signup(cls, data: AuthSocialSignupSchema, db: Session):
        username = data.username
        auth_key = data.auth_key
        auth_type = data.auth_type

        # search if user exists
        query_user = get_user_by_username(db, username)
        if query_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"username `{username}` is already used")

        try:
            # insert new user
            inserted_user = create_user(db, username, "")
            inserted_auth = create_auth(db, inserted_user.id, auth_type.value, auth_key, cls.generate_jwt_token(inserted_user.id, username, REFRESH_TOKEN_EXP))
            db.commit()

            return AuthSignupResponse.load(inserted_user.id, username, inserted_auth.type)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"unhandled error triggered: {str(e)}")

    # renew access token and refresh token
    @classmethod
    def refresh_token(cls, data: AuthRefreshTokenSchema, db: Session):
        try:
            decoded_token = cls.decode_jwt_token(data.refresh_token)

            user_id = decoded_token["user_id"]
            username = decoded_token["username"]

            return AuthTokenRefreshResponse.load({
                "access_token": cls.generate_jwt_token(user_id, username, ACCESS_TOKEN_EXP),
                "refresh_token": cls.verify_exp_and_get_refresh_token(db, data.refresh_token, user_id, username),
            })
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"invalid refresh token received: {str(e)}")

    # verify if plain password matches to hashed password
    @classmethod
    def verify_password_hash(cls, plain_password: str, hashed_password: str):
        return cls.pwd_context.verify(plain_password, hashed_password)

    # verify if password and confirm password matches
    @classmethod
    def verify_password_confirmation(cls, password: str, confirm_password: str):
        if password == confirm_password:
            return True
        return False

    # convert password to brypt hashed password and return
    @classmethod
    def get_password_hash(cls, plain_password: str):
        return cls.pwd_context.hash(plain_password)

    # generate a new jwt token
    @classmethod
    def generate_jwt_token(cls, user_id: int, username: str, time_delta: int):
        payload = {
            "user_id": user_id,
            "username": username,
            "exp": datetime.utcnow() + timedelta(hours=time_delta),
        }
        return jwt.encode(payload, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM"))

    # decode the jwt token and return payload
    @classmethod
    def decode_jwt_token(cls, token: str):
        try:
            return jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM")])
        except Exception as e:
            raise e

    # verify refresh token expiration
    # if expired generate new refresh token
    @classmethod
    def verify_exp_and_get_refresh_token(cls, db: Session, token: str, user_id: int, username: str):
        try:
            jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM")])
            return token
        except jwt.ExpiredSignatureError:
            refresh_token = cls.generate_jwt_token(user_id, username, REFRESH_TOKEN_EXP)
            update_auth_refresh_token_by_user_id(db, user_id, refresh_token)
            return refresh_token

    @classmethod
    def validate_token(cls, req: Request):
        if "Authorization" not in req.headers:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized user")

        token = req.headers["Authorization"]
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized user")

        token = token.split(" ")
        if token[0] != "Bearer":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized user")

        try:
            decoded_token = cls.decode_jwt(token[1])
            return decoded_token["user_id"]
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized user")

    @classmethod
    def decode_jwt(cls, token: str):
        try:
            decoded_token = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM")])
            return decoded_token
        except Exception as e:
            raise e
