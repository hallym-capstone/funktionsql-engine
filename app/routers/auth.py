from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

from app.database import get_db
from app.routers.modules.auth_module import AuthModule
from app.schemas import (
    AuthBasicSignupSchema, AuthBasicLoginSchema, AuthRefreshTokenSchema,
    AuthSocialLoginSchema, AuthSocialSignupSchema,
)


router = APIRouter()


# login api route for basic users
@router.post("/login/basic")
async def basic_login(
    data: AuthBasicLoginSchema,
    db: Session = Depends(get_db),
):
    return AuthModule.basic_login(data, db)


# login api route for social users
@router.post("/login/social")
async def social_login(
    data: AuthSocialLoginSchema,
    db: Session = Depends(get_db),
):
    return AuthModule.social_login(data, db)


# signup api route for basic users
@router.post("/signup/basic")
async def basic_signup(
    data: AuthBasicSignupSchema,
    db: Session = Depends(get_db),
):
    return AuthModule.basic_signup(data, db)


# signup api route for social users
@router.post("/signup/social")
async def social_signup(
    data: AuthSocialSignupSchema,
    db: Session = Depends(get_db),
):
    return AuthModule.social_signup(data, db)


# token refresh api route
@router.post("/tokens/refresh")
async def refresh_token(
    data: AuthRefreshTokenSchema,
    db: Session = Depends(get_db),
):
    return AuthModule.refresh_token(data, db)
