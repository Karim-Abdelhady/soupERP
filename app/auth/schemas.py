from pydantic import BaseModel, field_validator
from app.users.models import UserType
from datetime import datetime
from app.auth.enums import PermissionCatalog
from typing import List, Any

class RoleCreate(BaseModel): #
    name: str
    description: str
    user_type: UserType
    is_active: bool

class RoleResponse(BaseModel): #
    id: int
    name: str
    description: str
    user_type: UserType
    is_active: bool
    last_modified_at: datetime
    modified_by: str
    created_by: str
    permissions: List[PermissionCatalog] | None

    @field_validator("permissions", mode="before")
    @classmethod
    def transform_permissions(cls, v: Any) -> List[PermissionCatalog]:
        if not v:
            return []
        return [p.name if hasattr(p, "name") else p for p in v]

    class Config:
        from_attributes = True

class RoleUpdate(BaseModel): #
    name: str | None = None
    description: str | None = None
    user_type: UserType | None = None
    is_active: bool | None = None  

class UserRoleResponse(BaseModel):
    id: int
    name: str
    is_active: bool
    permissions: List[PermissionCatalog]

    @field_validator("permissions", mode="before")
    @classmethod
    def transform_permissions(cls, v: Any) -> List[Any]:
        if not v:
            return []
        return [p.name.value if hasattr(p.name, "value") else p.name if hasattr(p, "name") else p for p in v]

    class Config:
        from_attributes = True
