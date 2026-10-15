from sqlalchemy.orm import Session
from app.auth import repository
from fastapi import HTTPException, status
from app.auth.schemas import RoleCreate, RoleUpdate
from app.auth.models import Role, Permission
from app.users import repository as userRepository
from app.auth.enums import PermissionCatalog

def get_roles(db: Session):
    roles = repository.get_roles(db)
    if not roles:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Please create a role")
    return roles

def get_role_by_role_id(db: Session, role_id: int):
    role = repository.get_role_by_role_id(db, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Role with ID is not found")
    return role

def create_role(db: Session, newRole: RoleCreate):
    exist_role = repository.get_role_by_role_name(db, newRole.name)
    if exist_role is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Role is already created")
    
    role_data = newRole.model_dump()
    
    role_obj = Role(
        **role_data,
        permission_count=0,
        assigned_user_count=0
    )
    db_user = repository.create_role(db, role_obj)
    return db_user

def update_role(db: Session, role_id: int, updateRole: RoleUpdate):
    role = repository.get_role_by_role_id(db, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Role is not found")
    update_data = updateRole.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(role, field, value)

    return repository.update_role(db, role)

def add_permission_to_role(db: Session, role_id: int, permission_catalog: PermissionCatalog):
    role = repository.get_role_by_role_id(db, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Role is not found")
    permission = repository.get_permission_by_name(db, permission_catalog)
    if permission is None:
        permission = Permission(name=permission_catalog)
        db.add(permission)
        db.flush()

    return repository.add_permission_to_role(db, role, permission)

def delete_role_permission(db: Session, role_id: int, permission_catalog: PermissionCatalog):
    role = repository.get_role_by_role_id(db, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Role is not found")
    permission = repository.get_permission_by_name(db, permission_catalog)
    if permission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Permission is not found")

    return repository.delete_role_permission(db, role,permission)

def add_role_to_user(db: Session, user_id: int, role_id: int):
    user = userRepository.get_user_by_user_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User is not found")
    role = repository.get_role_by_role_id(db, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Role is not found")
    if role not in user.roles:
        user.roles.append(role)
        db.commit()

    return repository.add_role_to_user(db, user, role)