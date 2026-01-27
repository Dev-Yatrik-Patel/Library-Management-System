from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import List

from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.controllers.auth_controller import get_current_user

from app.models.user import User

from app.core.roles import Roles
from app.core.dependencies import require_roles
from app.core.database import get_db
from app.core.response import success_response

from app.controllers.user_controller import (
    get_audit_logs_admin, 
    update_my_profile_user,
    delete_profile_user,
    create_user_admin,
    get_all_users_admin,
    get_user_by_id_admin,
    update_user_by_id_admin,
    delete_user_admin)

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/audit-logs")
def get_audit_logs(
    db: Session = Depends(get_db),
    _ = Depends(require_roles(Roles.ADMIN))
):
    data = get_audit_logs_admin(db = db)
    return success_response(data = jsonable_encoder(data))

@router.get("/me",response_model=UserResponse) 
def get_my_info(current_user: User = Depends(get_current_user)):
    return success_response(data = UserResponse.model_validate(current_user).model_dump(mode="json") )

@router.put("/me",response_model=UserResponse)
def update_my_profile(userupdateobj: UserUpdate, db: Session = Depends(get_db), current_user:User =  Depends(get_current_user)):
    user = update_my_profile_user(userupdateobj= userupdateobj,db = db, current_user = current_user)
    return success_response(data = UserResponse.model_validate(user).model_dump(mode="json") )

@router.delete("/me")
def delete_profile(
    db: Session = Depends(get_db),
    current_user: User =Depends(get_current_user)
):
    delete_profile_user(db = db,current_user = current_user)
    return success_response(message="Account deleted")

@router.post("/", 
             response_model=UserResponse, 
             status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user),_= Depends(require_roles(Roles.ADMIN,Roles.LIBRARIAN))):
    user = create_user_admin(user = user ,db = db,current_user = current_user)
    return success_response(data = UserResponse.model_validate(user).model_dump(mode="json"))

@router.get("/", 
             response_model=List[UserResponse], 
             status_code=status.HTTP_200_OK)
def get_all_users(db: Session = Depends(get_db),_= Depends(require_roles(Roles.ADMIN))):
    allUsers = get_all_users_admin(db = db)
    return success_response(
        data = [ UserResponse.model_validate(i).model_dump(mode="json") for i in allUsers]
    )

@router.get("/{userid}", 
             response_model=UserResponse, 
             status_code=status.HTTP_200_OK)
def get_user_by_id(userid: int, db:Session = Depends(get_db),_= Depends(require_roles(Roles.ADMIN))):
    user= get_user_by_id_admin(userid = userid,db = db)       
    return success_response(data = UserResponse.model_validate(user).model_dump(mode="json"))


@router.put("/{userid}", response_model=UserResponse)
def update_user_by_id(userid: int, 
                      updateuserobj: UserUpdate, 
                      db: Session = Depends(get_db), 
                      current_user: User = Depends(get_current_user),
                      _=Depends(require_roles(Roles.ADMIN))):
    user = update_user_by_id_admin(userid = userid, updateuserobj = updateuserobj, db = db,current_user = current_user)
    return success_response(data = UserResponse.model_validate(user).model_dump(mode="json"))

@router.delete("/{userid}")
def delete_user(userid: int, db:Session = Depends(get_db), current_user: User = Depends(get_current_user),_=Depends(require_roles(Roles.ADMIN))):
    delete_user_admin(userid = userid,db = db,current_user = current_user)
    return success_response(message="User Deleted!")
