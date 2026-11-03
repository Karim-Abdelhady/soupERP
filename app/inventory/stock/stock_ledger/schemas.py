from pydantic import BaseModel
from datetime import datetime

class StockLedgerResponse(BaseModel):
    id: int
    item_id: int
    warehouse_id: int
    posting_date: datetime
    quantity_delta: int
    qty_after_transaction: int
    incoming_rate: float
    outgoing_rate: float
    stock_value_delta: float
    stock_value_after_transaction: float
    voucher_type: str
    voucher_id: str
    voucher_line_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class StockLedgerCreate(BaseModel):
    item_id: int
    warehouse_id: int
    quantity_delta: int
    incoming_rate: float
    outgoing_rate: float
    voucher_type: str
    voucher_id: str
    voucher_line_id: str