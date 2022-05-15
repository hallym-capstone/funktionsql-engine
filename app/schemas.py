from typing import Optional
from pydantic import BaseModel

from app.models import AuthType, ExecutionLanguage


class ExecuteQuerySchema(BaseModel):
    query_selector: str = ""
    query_target: str = ""
    database_id: Optional[int]
    parameters: Optional[dict] = []


class CreateDatabaseSchema(BaseModel):
    database_name: str


class CreateFunctionSchema(BaseModel):
    code: str
    language: ExecutionLanguage
    function_name: str


class AuthBasicLoginSchema(BaseModel):
    username: str
    password: str


class AuthSocialLoginSchema(BaseModel):
    username: str
    password: str
    auth_key: str
    auth_type: AuthType


class AuthBasicSignupSchema(BaseModel):
    username: str
    password: str
    confirm_password: str


class AuthSocialSignupSchema(BaseModel):
    username: str
    password: str
    auth_key: str
    auth_type: AuthType


class AuthRefreshTokenSchema(BaseModel):
    refresh_token: str


class AuthSignupResponse(BaseModel):
    id: int
    username: str
    type: AuthType

    @classmethod
    def load(cls, id: int, username: str, type: AuthType):
        return AuthSignupResponse(
            id=id,
            username=username,
            type=type,
        )


class AuthLoginResponse(BaseModel):
    id: int
    username: str
    type: AuthType
    access_token: str
    refresh_token: str

    @classmethod
    def load(cls, data: dict):
        return AuthLoginResponse(
            id=data["id"],
            username=data["username"],
            type=data["type"],
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
        )


class AuthTokenRefreshResponse(BaseModel):
    access_token: str
    refresh_token: str

    @classmethod
    def load(cls, data: dict):
        return AuthTokenRefreshResponse(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
        )
