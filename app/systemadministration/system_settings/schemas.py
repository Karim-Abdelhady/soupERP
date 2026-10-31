from pydantic import BaseModel
from datetime import datetime

class SystemSettingResponse(BaseModel):
    id: int
    key: str
    value: str
    category: str
    data_type: str
    description: str
    is_editable: bool
    updated_at: datetime
    updated_by: str

    class Config:
        from_attributes = True

class SystemSettingCreate(BaseModel):
    key: str
    value: str
    category: str
    data_type: str
    description: str
    is_editable: bool

class SystemSettingUpdate(BaseModel):
    value: str | None = None
    category: str | None = None
    data_type: str | None = None
    description: str | None = None
    updated_by: str | None = None
    reason: str | None = None

class SystemSettingHistoryResponse(BaseModel):
    id: int
    system_setting_id: int
    key: str
    old_value: str | None = None
    new_value: str
    default_key: str | None = None
    changed_by: str | None = None
    changed_at: datetime
    reason: str | None = None

    class Config:
        from_attributes = True