from pydantic import BaseModel
from app.inventory.stock.stock_entry.enums import Purpose, Status
from datetime import datetime
from typing import List

class StockEntryLineResponse(BaseModel):
    id: int
    stock_entry_id: int
    item_id: int
    source_warehouse_id: int | None = None
    target_warehouse_id: int | None = None
    quantity: int
    uom_id: int
    conversion_factor: int
    stock_quantity: int
    unit_cost: int
    line_amount: int

    class Config:
        from_attributes = True

class StockEntryResponse(BaseModel):
    id: int
    document_number: str
    purpose: Purpose
    status: Status
    source_warehouse_id: int | None = None
    target_warehouse_id: int | None = None
    remarks: str | None = None
    created_by: str
    submitted_by: str | None = None
    created_at: datetime
    submitted_at: datetime | None = None
    cancelled_by: str | None = None
    cancelled_at: datetime | None = None
    stock_entry_lines: List[StockEntryLineResponse]

    class Config:
        from_attributes = True

class StockEntryLineCreate(BaseModel):
    item_id: int
    source_warehouse_id: int | None = None
    target_warehouse_id: int | None = None
    quantity: int
    uom_id: int
    conversion_factor: int
    unit_cost: int

class StockEntryCreate(BaseModel):
    document_number: str
    purpose: Purpose
    source_warehouse_id: int | None = None
    target_warehouse_id: int | None = None
    remarks: str
    stock_entry_lines: List[StockEntryLineCreate]

class StockEntryLineUpdate(BaseModel):
    stock_entry_id: int | None = None
    item_id: int | None = None
    source_warehouse_id: int | None = None
    target_warehouse_id: int | None = None
    quantity: int | None = None
    uom_id: int | None = None
    conversion_factor: int | None = None
    unit_cost: int | None = None

class StockEntryUpdate(BaseModel):
    purpose: Purpose | None = None
    status: Status | None = None
    source_warehouse_id: int | None = None
    target_warehouse_id: int | None = None
    remarks: str | None = None
    stock_entry_lines: List[StockEntryLineUpdate]
