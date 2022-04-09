import os
import jwt

from pathlib import Path
from dotenv import load_dotenv

from fastapi import Request, status
from fastapi.exceptions import HTTPException

from app.schemas import AuthBasicSignupSchema, AuthLoginSchema, AuthRefreshTokenSchema, AuthSocialSignupSchema


env_path = Path("config") / ".env"
load_dotenv(dotenv_path=env_path)


class AuthModule:

    @classmethod
    def login(cls, data: AuthLoginSchema):
        username = data.username
        password = data.password

    @classmethod
    def basic_signup(cls, data: AuthBasicSignupSchema):
        pass

    @classmethod
    def social_signup(cls, data: AuthSocialSignupSchema):
        pass

    @classmethod
    def refresh_token(cls, data: AuthRefreshTokenSchema):
        pass

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
