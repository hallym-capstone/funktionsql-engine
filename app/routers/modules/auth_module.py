import os
import jwt

from pathlib import Path
from dotenv import load_dotenv

from fastapi import Request, status
from fastapi.exceptions import HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm.session import Session
from app.crud import create_auth, create_user, get_user_by_username
from app.models import AuthType

from app.schemas import AuthBasicSignupSchema, AuthLoginSchema, AuthRefreshTokenSchema, AuthSignupResponse, AuthSocialSignupSchema


env_path = Path("config") / ".env"
load_dotenv(dotenv_path=env_path)


class AuthModule:

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def login(cls, data: AuthLoginSchema, db: Session):
        username = data.username
        password = data.password

        query_user = get_user_by_username(db, username)
        if not query_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="unauthorized user credentials")

        if not cls.verify_password(password, query_user.password):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="unauthorized user credentials")

    @classmethod
    def basic_signup(cls, data: AuthBasicSignupSchema, db: Session):
        # TODO: password policy
        username = data.username
        password = data.password

        query_user = get_user_by_username(db, username)
        if query_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"username `{username}` is already used")

        try:
            inserted_user = create_user(db, username, cls.get_password_hash(password))
            inserted_auth = create_auth(db, inserted_user.id, AuthType.BASIC.value, None)
            db.commit()

            return AuthSignupResponse.load(inserted_user.id, username, inserted_auth.type)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"unhandled error triggered: {str(e)}")

    @classmethod
    def social_signup(cls, data: AuthSocialSignupSchema, db: Session):
        username = data.username
        password = data.password
        auth_key = data.auth_key
        auth_type = data.auth_type

        query_user = get_user_by_username(db, username)
        if query_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"username `{username}` is already used")

        try:
            inserted_user = create_user(db, username, cls.get_password_hash(password))
            inserted_auth = create_auth(db, inserted_user.id, auth_type.value, auth_key)
            db.commit()

            return AuthSignupResponse.load(inserted_user.id, username, inserted_auth.type)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"unhandled error triggered: {str(e)}")

    @classmethod
    def refresh_token(cls, data: AuthRefreshTokenSchema):
        pass

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str):
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, plain_password: str):
        return cls.pwd_context.hash(plain_password)

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

        decoded_token = cls.decode_jwt(token[1])
        return decoded_token["user_id"]

    @classmethod
    def decode_jwt(cls, token: str):
        decoded_token = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM")])
        return decoded_token
