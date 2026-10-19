from fastapi import Depends, APIRouter
from database.database import get_db
from sqlalchemy.orm import Session
from app.auth.schemas import RoleResponse, RoleCreate, RoleUpdate
from app.auth.enums import PermissionCatalog
from typing import List
from app.auth import service
from app.users.schemas import UserResponse
from app.auth.permissions import require_permission, PermissionCatalog
from app.users.models import User


router = APIRouter()

@router.get("/roles", response_model=List[RoleResponse], tags = ["Roles"])
def get_roles(db: Session = Depends(get_db), current_user: User = Depends(require_permission(PermissionCatalog.ROLE_READ))):
    return service.get_roles(db)

@router.get("/roles/{role_id}", response_model=RoleResponse, tags = ["Roles"])
def get_role_by_role_id(role_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission(PermissionCatalog.ROLE_READ))):
    return service.get_role_by_role_id(db, role_id)
    
@router.post("/roles", response_model=RoleResponse, tags=["Roles"])
def create_role(newRole: RoleCreate, db: Session = Depends(get_db), current_user: User = Depends(require_permission(PermissionCatalog.ROLE_CREATE))):
    return service.create_role(db, newRole)

@router.patch("/roles/{role_id}", response_model=RoleResponse, tags=["Roles"])
def update_role(role_id: int, updateRole: RoleUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_permission(PermissionCatalog.ROLE_UPDATE))):
    return service.update_role(db, role_id, updateRole)

@router.post("/roles/{role_id}/permissions/{permission_catalog}", response_model=RoleResponse, tags = ["Roles"])
def add_permission_to_role(role_id: int, permission_catalog: PermissionCatalog, db: Session=Depends(get_db), current_user: User = Depends(require_permission(PermissionCatalog.PERMISSION_CREATE))):
    return service.add_permission_to_role(db,role_id,permission_catalog)

@router.delete("/roles/{role_id}/permissions/{permission_catalog}", response_model=RoleResponse, tags = ["Roles"])
def delete_role_permission(role_id: int, permission_catalog: PermissionCatalog, db: Session = Depends(get_db), current_user: User = Depends(require_permission(PermissionCatalog.PERMISSION_REMOVE))):
    return service.delete_role_permission(db, role_id, permission_catalog)

@router.post("/user/{user_id}/roles/{role_id}", response_model=UserResponse, tags = ["Roles"])
def add_role_to_user(user_id: int, role_id: int, db: Session = Depends(get_db)):
    return service.add_role_to_user(db, user_id, role_id)
