from sqlalchemy.orm import Session
from sqlalchemy import select
from app.auth.models import Role, Permission
from app.users.models import User
from app.auth.enums import PermissionCatalog

def get_roles(db: Session):
    statement = select(Role)
    return db.scalars(statement).all()

def get_role_by_role_id(db: Session, role_id: int):
    statement = select(Role).where(Role.id == role_id)
    return db.scalar(statement)

def get_role_by_role_name(db: Session, role_name: str):
    statement = select(Role).where(Role.name == role_name)
    return db.scalar(statement)

def create_role(db: Session, role: Role):
    db.add(role)
    db.commit()
    db.refresh(role)
    return role

def update_role(db: Session, role: Role):
    db.commit()
    db.refresh(role)
    return role

def add_permission_to_role(db: Session, role: Role, permission: Permission):
    if permission not in role.permissions:
        role.permissions.append(permission)
        db.commit()
        db.refresh(role)
    return role

def delete_role_permission(db: Session, role: Role, permission: Permission):
    if permission in role.permissions:
        role.permissions.remove(permission)
        db.commit()
        db.refresh(role)
    return role

def add_role_to_user(db: Session, user: User, role: Role):
    if role in role.users:
        role.users.append(user)
        db.commit()
        db.refresh(role)
    return user



