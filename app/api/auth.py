from fastapi import APIRouter, HTTPException, Depends, status 
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.core.database import get_db
from app.models.user import User
from app.utils.security import verify_password, hash_password, create_access_token

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
SECRET_KEY = os.getenv("SECRET_KEY","secret")


router = APIRouter(prefix='/auth', tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
ALGORITHM = "HS256"


# Helper Function
def get_current_user(
    token : str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Cound not validate Credentials",
        headers = {"WWW-Authenticated" : "Bearer"}
    )
    
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id : str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if user is None: 
        raise credentials_exception
    
    return user
    
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # form_data.password => test1234
    # user.password_hash => $2b$12$kIVsVg78Su98CQn41An5KOdazXgL2JO283il7fXZOayX44VmH.PPO
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid email or password"
        )
    
    access_token = create_access_token(
        data = {"sub": str(user.id)}
    )
    
    return{
        "access_token" : access_token,
        "token_type": "bearer"
    }

@router.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return {
        "id" : current_user.id,
        "name" : current_user.name,
        "email" : current_user.email,
        "role_id" : current_user.role_id
    }


