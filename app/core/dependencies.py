from fastapi import HTTPException, status, Depends
from app.api.auth import get_current_user
from app.models.user import User

def require_roles(*allowed_roles: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        print(current_user.role.name)
        print(allowed_roles)
        if current_user.role.name not in allowed_roles:
            raise HTTPException(
                status_code= status.HTTP_401_UNAUTHORIZED,
                detail = "You do not have permissions to perform this action!"
            )
        return current_user
    return role_checker