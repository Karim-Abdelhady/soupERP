from pydantic import BaseModel
from datetime import datetime

class WarehouseTypeCreate(BaseModel):
    name: str

class WarehouseTypeResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    is_active: bool

    class Config:
        from_attributes = True

class WarehouseTypeUpdate(BaseModel):
    name: str | None = None

class WarehouseCreate(BaseModel):
    code: str
    name: str
    company_id: int
    warehouse_type_id: int

class WarehouseResponse(BaseModel):
    id: int
    code: str
    name: str
    parent_id: int | None = None
    company_id: int
    warehouse_type_id: int
    is_group: bool
    is_active: bool
    updated_at: datetime
    created_at: datetime
    created_by: str
    warehouse_type: WarehouseTypeResponse

    class Config:
        from_attributes = True

class WarehouseUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    parent_id: int | None = None
    company_id: int | None = None
    warehouse_type_id: int | None = None
    is_group: bool | None = None

class Activation(BaseModel):
    is_active: bool