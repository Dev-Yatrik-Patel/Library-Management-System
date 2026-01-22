from fastapi import HTTPException, status, Depends
from app.api.auth import get_current_user
from app.models.user import User
from app.core.roles import Roles
from app.exceptions.auth import AuthorizationError


def require_roles(*allowed_roles: Roles):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role.name not in [i.value for i in allowed_roles]:
            print([i.value for i in allowed_roles])
            print(current_user.role.name)
            raise AuthorizationError("You do not have permissions to perform this action!")
        return current_user
    return role_checker