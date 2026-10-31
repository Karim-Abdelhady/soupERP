from pydantic import BaseModel
from datetime import datetime

class ItemGroupCreate(BaseModel):
    group_code: str
    name: str
    description: str | None = None
    
class ItemGroupResponse(BaseModel):
    id: int
    group_code: str
    name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime
    created_by: str
    is_active: bool

    class Config:
        from_attributes = True

class ItemGroupUpdate(BaseModel):
    group_code: str | None = None
    name: str | None = None
    description: str | None = None

class ItemCreate(BaseModel):
    item_code: str
    name: str
    description: str | None = None
    item_type: str | None = None
    stock_uom_id: int
    item_group_id: int
    is_batch_tracked: bool
    is_serial_tracked: bool
    has_expiry_date: bool
    expiry_date: datetime | None = None
    valuation_method: str | None = None

class ItemResponse(BaseModel):
    id: int
    item_code: str
    description: str | None = None
    item_type: str | None = None
    stock_uom_id: int
    item_group_id: int
    is_active: bool
    is_batch_tracked: bool
    is_serial_tracked: bool
    has_expiry_date: bool 
    expiry_date: datetime | None = None
    valuation_method: str | None = None
    created_at: datetime
    updated_at: datetime
    created_by: str

    class Config:
        from_attributes = True

class ItemUpdate(BaseModel):
    item_code: str | None = None
    name: str | None = None
    description: str | None = None
    item_type: str | None = None
    stock_uom_id: int | None = None
    item_group_id: int | None = None 

    valuation_method: str | None = None

class TrackUpdate(BaseModel):
    is_batch_tracked: bool | None = None
    is_serial_tracked: bool | None = None
    has_expiry_date: bool | None = None
    expiry_date: datetime | None = None


class Activation(BaseModel):
    is_active: bool