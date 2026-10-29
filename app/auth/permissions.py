from app.core.security import get_current_user
from fastapi import Depends
from app.users.models import User
from fastapi import HTTPException,status
from app.auth.enums import PermissionCatalog

def require_permission(requiredPermission: PermissionCatalog):
    def permission_checker(current_user: User = Depends(get_current_user)):
        user_permissions = {
            str(perm.name) == requiredPermission.value
            for role in current_user.roles
            for perm in role.permissions
        }

        if requiredPermission.value not in user_permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "Access Denied.")

        return current_user
    return permission_checker
