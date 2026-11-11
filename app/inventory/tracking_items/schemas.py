from pydantic import BaseModel
from datetime import datetime
from app.inventory.tracking_items.enums import SerialStatus, BatchStatus
from typing import List

class BatchCreate(BaseModel):
    item_id: int
    batch_number: str
    manufacture_date: datetime | None = None
    expiry_date: datetime | None = None

class BatchResponse(BaseModel):
    id: int
    item_id: int
    batch_number: str
    manufacture_date: datetime | None = None
    expiry_date: datetime | None = None
    status: BatchStatus
    created_at: datetime

    class Config:
        from_attributes = True

class BatchUpdate(BaseModel):
    item_id: int | None = None
    batch_number: str | None = None
    manufacture_date: datetime | None = None
    expiry_date: datetime | None = None

class SerialNumberCreate(BaseModel):
    item_id: int
    serial_number: str
    current_warehouse_id: int | None = None
    batch_id: int | None = None

class SerialNumberResponse(BaseModel):
    id: int
    item_id: int
    serial_number: str
    status: SerialStatus
    current_warehouse_id: int | None = None
    batch_id: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True

class SerialNumberUpdate(BaseModel):
    item_id: int | None = None
    serial_number: str | None = None
    current_warehouse_id: int | None = None
    batch_id: int | None = None

class BatchSerialResponse(BaseModel):
    id: int
    item_id: int
    batch_number: str
    manufacture_date: datetime | None = None
    expiry_date: datetime | None = None
    status: BatchStatus
    created_at: datetime

    serial_numbers: List[SerialNumberResponse]

    class Config:
        from_attributes = True