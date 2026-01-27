from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.core.audit import log_audit
from app.core.response import success_response

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.audit_log import AuditLog

from app.utils.security import verify_password, create_access_token, create_refresh_token, refresh_token_expiry, decode_access_token
from app.schemas.auth import RefreshTokenRequest, LogoutRequest
from app.schemas.audit_logs import AuditAction
from app.schemas.user import UserResponse

from app.exceptions.auth import AuthenticationError,AuthorizationError

import os
from dotenv import load_dotenv, find_dotenv
from datetime import datetime

from app.controllers.auth_controller import (
    login_user,
    get_current_user,
    refresh_access_token_user,
    logout_user
)

router = APIRouter(prefix='/auth', tags=["Auth"])

@router.post("/login")
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    tokenPayLoad = login_user(form_data = form_data, db = db)
    return tokenPayLoad

@router.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return success_response(
        data = {
            "id" : current_user.id,
            "name" : current_user.name,
            "email" : current_user.email,
            "role_id" : current_user.role_id
        }
    )

@router.post("/refresh")
@limiter.limit("10/minute")
def refresh_access_token(
    request: Request,
    data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    tokenRefreshPayLoad = refresh_access_token_user(data = data, db = db)
    return success_response(
        data = tokenRefreshPayLoad
    )

@router.post("/logout")
def logout(
    data: LogoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logout_user(data = data, db = db, current_user = current_user)
    return success_response(
     message="Logout Successfully"   
    )

