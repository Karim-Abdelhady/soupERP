from pydantic import BaseModel
from datetime import datetime
from app.inventory.stock.stock_reconciliation.enums import Status
from typing import List

class StockReconciliationLineResponse(BaseModel):
    id: int
    reconciliation_id: int
    item_id: int
    expected_qty: int
    counted_qty: int
    difference_qty: int
    uom_id: int
    conversion_factor: int
    valuation_rate: int

    class Config:
        from_attributes = True

class StockReconciliationResponse(BaseModel):
    id: int
    document_number: str
    status: Status
    posting_date: datetime
    warehouse_id: int
    reason: str | None = None
    created_by: str
    submitted_by: str | None = None
    submitted_at: datetime | None = None
    canceled_by: str | None = None
    canceled_at: datetime | None = None
    stock_reconciliation_lines: List[StockReconciliationLineResponse]

    class Config:
        from_attributes = True

class StockReconciliationLineCreate(BaseModel):
    item_id: int
    counted_qty: int

class StockReconciliationCreate(BaseModel):
    document_number: str
    posting_date: datetime
    warehouse_id: int
    reason: str | None = None
    stock_reconciliation_lines: List[StockReconciliationLineCreate]

class StockReconciliationLineUpdate(BaseModel):
    item_id: int | None = None
    counted_qty: int | None = None

class StockReconciliationUpdate(BaseModel):
    posting_date: datetime | None = None
    warehouse_id: int | None = None
    reason: str | None = None
    stock_reconciliation_lines: List[StockReconciliationLineUpdate]

