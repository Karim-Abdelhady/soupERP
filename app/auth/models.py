from __future__ import annotations

from database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
from datetime import datetime, timezone
from sqlalchemy import DateTime, Column, Integer
from sqlalchemy import Enum as SQLEnum
from app.users.enums import UserType
from app.auth.tables import user_roles, role_permissions
from app.auth.enums import PermissionCatalog

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique = True, nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    user_type: Mapped[UserType] = mapped_column(nullable=False, default = UserType.USER)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    last_modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    modified_by: Mapped[str] = mapped_column(nullable=False, default = "system")
    created_by: Mapped[str] = mapped_column(nullable=False, default = "system")
    permissions: Mapped[list["Permission"]] = relationship(secondary=role_permissions, back_populates="roles")  
    users: Mapped[list["User"]] = relationship(secondary=user_roles, back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[PermissionCatalog] = mapped_column(SQLEnum(PermissionCatalog), unique=True, nullable=False)

    roles: Mapped[list["Role"]] = relationship(secondary=role_permissions, back_populates="permissions")
    

