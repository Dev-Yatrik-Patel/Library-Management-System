from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.audit_logs import AuditAction
from app.utils.security import hash_password
from app.api.auth import get_current_user

from app.models.user import User
from app.models.role import Role
from app.models.loan import Loan
from app.models.refresh_token import RefreshToken
from app.models.audit_log import AuditLog

from app.core.roles import Roles
from app.core.dependencies import require_roles
from app.core.database import get_db
from app.core.audit import log_audit
from app.core.response import success_response

from app.exceptions.auth import AuthenticationError, AuthorizationError
from app.exceptions.user import UserNotFound,UserLoanPending,UserEmailAlreadyExists


router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/audit-logs")
def get_audit_logs(
    db: Session = Depends(get_db),
    _ = Depends(require_roles(Roles.ADMIN))
):
    data = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()
    return success_response(data = jsonable_encoder(data))

@router.get("/me",response_model=UserResponse) 
def get_my_info(current_user: User = Depends(get_current_user)):
    
    return success_response(data = UserResponse.model_validate(current_user).model_dump(mode="json") )

@router.put("/me",response_model=UserResponse)
def update_my_profile(userupdateobj: UserUpdate, db: Session = Depends(get_db), current_user:User =  Depends(get_current_user)):
    
    updated_data = userupdateobj.model_dump(exclude_unset=True)
    
    if "email" in updated_data:
        exists = db.query(User).filter(
            User.email == updated_data["email"],
            User.id != current_user.id
        ).first()
        if exists:
            raise UserEmailAlreadyExists()
    
    for k,v in updated_data.items():
        setattr(current_user,k,v)
    
    current_user.updated_at = datetime.now()
    
    # Audit user updation 
    log_audit(
        db,
        action=AuditAction.USER_UPDATED,
        entity="User",
        entity_id=current_user.id,
        performed_by=current_user.id,
        message=f"User {current_user.email} updated by himself/herself."
    )
    
    db.commit()
    db.refresh(current_user)

    return success_response(data = UserResponse.model_validate(current_user).model_dump(mode="json") )

@router.delete("/me")
def delete_profile(
    db: Session = Depends(get_db),
    current_user: User =Depends(get_current_user)
):
    # checking the loan history of the user before removing
    loans_history = db.query(Loan).filter(Loan.user_id == current_user.id, Loan.is_active == True).first()
    
    if loans_history:
        raise UserLoanPending()
    
    # soft delete the user
    current_user.is_active = False # db.delete(user)
    current_user.deleted_at = datetime.now()
    current_user.deleted_by = current_user.id
    
    # revoking the refresh tokens 
    db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.is_revoked == False
    ).update({"is_revoked": True},synchronize_session=False)
    
    # Audit user deletion
    log_audit(
        db,
        action=AuditAction.USER_SELF_DELETED,
        entity="User",
        entity_id=current_user.id,
        performed_by=current_user.id,
        message=f"User {current_user.email} deleted by himself/herself."
    )
    
    db.commit()
    
    return success_response(message="Account deleted")

@router.post("/", 
             response_model=UserResponse, 
             status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user),_= Depends(require_roles(Roles.ADMIN,Roles.LIBRARIAN))):
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email.strip().lower(), User.is_active == True).first()
    
    if existing_user:
        raise AuthenticationError(message = "Email already registered")

    # Validate role
    role = db.query(Role).filter(Role.id == user.role_id).first()
    if not role:
        raise AuthenticationError(message = "Invalid role_id")
        
    
    db_user = User(
        name=user.name,
        email=user.email.strip().lower(),
        password_hash=hash_password(user.password),
        role_id=user.role_id
    )

    db.add(db_user)
    db.flush()
    
    # Audit user creation
    log_audit(
        db,
        action=AuditAction.USER_CREATED,
        entity="User",
        entity_id=db_user.id,
        performed_by=current_user.id,
        message=f"User {user.email} created by admin"
    )
    
    db.commit()
    db.refresh(db_user)
    
    return success_response(data = UserResponse.model_validate(db_user).model_dump(mode="json"))

@router.get("/", 
             response_model=List[UserResponse], 
             status_code=status.HTTP_200_OK)
def get_all_users(db: Session = Depends(get_db),_= Depends(require_roles(Roles.ADMIN))):
    allUsers = db.query(User).filter(User.is_active==True).all()
    return success_response(
        data = [ UserResponse.model_validate(i).model_dump(mode="json") for i in allUsers]
    )

@router.get("/{userid}", 
             response_model=UserResponse, 
             status_code=status.HTTP_200_OK)
def get_user_by_id(userid: int, db:Session = Depends(get_db),_= Depends(require_roles(Roles.ADMIN))):
    
    user= db.query(User).filter(User.id == userid,User.is_active==True).first()
    
    if not user:
        raise UserNotFound()        
    
    return success_response(data = UserResponse.model_validate(user).model_dump(mode="json"))


@router.put("/{userid}", response_model=UserResponse)
def update_user_by_id(userid: int, 
                      updateuserobj: UserUpdate, 
                      db: Session = Depends(get_db), 
                      current_user: User = Depends(get_current_user),
                      _=Depends(require_roles(Roles.ADMIN))):
    
    user = db.query(User).filter(User.id == userid,User.is_active==True).first()
    
    if not user:
        raise UserNotFound()        
    
    updated_data = updateuserobj.model_dump(exclude_unset=True)
    if "email" in updated_data:
        exists = db.query(User).filter(
            User.email == updated_data["email"],
            User.id != user.id
        ).first()
        if exists:
            raise UserEmailAlreadyExists()
    
    for k,v in updated_data.items():
        setattr(user,k,v)
    
    user.updated_at = datetime.now()
    
    # Audit user updation
    log_audit(
        db,
        action=AuditAction.USER_UPDATED,
        entity="User",
        entity_id=user.id,
        performed_by=current_user.id,
        message=f"User {user.email} updated by admin"
    )
    
    db.commit()
    db.refresh(user)
    
    return success_response(data = UserResponse.model_validate(user).model_dump(mode="json"))

@router.delete("/{userid}")
def delete_user(userid: int, db:Session = Depends(get_db), current_user: User = Depends(get_current_user),_=Depends(require_roles(Roles.ADMIN))):
    
    user = db.query(User).filter(User.id == userid,User.is_active==True).first()
    
    if not user:
        raise UserNotFound()
    
    # checkin the loan history of the user before removing
    loans_history = db.query(Loan).filter(Loan.user_id == userid, Loan.is_active == True).first()
    
    if loans_history:
        raise UserLoanPending()
    
    # soft delete the user
    user.is_active = False # db.delete(user)
    user.deleted_at = datetime.now()
    user.deleted_by = current_user.id
    
    # revoking the refresh tokens 
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id,
        RefreshToken.is_revoked == False
    ).update({"is_revoked": True})
    
    # Audit user deletion 
    log_audit(
        db,
        action=AuditAction.USER_DELETED,
        entity="User",
        entity_id=user.id,
        performed_by=current_user.id,
        message=f"User {user.email} deleted by admin"
    )
    
    db.commit()
    
    return success_response(message="User Deleted!")

