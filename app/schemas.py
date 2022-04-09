from pydantic import BaseModel

from app.models import AuthType


class ExecuteQuerySchema(BaseModel):
    query_selector: str
    function_name: str


class CreateDatabaseSchema(BaseModel):
    database_name: str
    api_key: str


class AuthLoginSchema(BaseModel):
    username: str
    password: str


class AuthBasicSignupSchema(BaseModel):
    username: str
    password: str


class AuthSocialSignupSchema(BaseModel):
    username: str
    password: str
    auth_key: str


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
