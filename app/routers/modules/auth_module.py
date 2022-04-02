import os
import jwt

from pathlib import Path
from dotenv import load_dotenv

from fastapi import Request, status
from fastapi.exceptions import HTTPException


env_path = Path("config") / ".env"
load_dotenv(dotenv_path=env_path)


class AuthModule:

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
