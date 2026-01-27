from sqlalchemy.orm import Session
from datetime import datetime

from app.models.user import User
from app.models.role import Role
from app.models.loan import Loan
from app.models.refresh_token import RefreshToken
from app.models.audit_log import AuditLog

from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.audit_logs import AuditAction

from app.core.audit import log_audit

from app.utils.security import hash_password

from app.exceptions.auth import AuthenticationError
from app.exceptions.user import UserNotFound,UserLoanPending,UserEmailAlreadyExists

def get_audit_logs_admin(db: Session):
    data = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()
    return data

def update_my_profile_user(userupdateobj: UserUpdate, db: Session, current_user:User):
    
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

    return current_user

def delete_profile_user(db: Session, current_user: User):
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
    
    return

def create_user_admin(user: UserCreate, db: Session, current_user: User):
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
    
    return db_user

def get_all_users_admin(db: Session):
    allUsers = db.query(User).filter(User.is_active==True).all()
    return allUsers

def get_user_by_id_admin(userid: int, db:Session):
    user= db.query(User).filter(User.id == userid,User.is_active==True).first()
    if not user:
        raise UserNotFound()        
    return user

def update_user_by_id_admin(userid: int, updateuserobj: UserUpdate, db: Session, current_user: User):
    
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
    
    return user

def delete_user_admin(userid: int, db:Session, current_user: User):
    
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
    
    return 