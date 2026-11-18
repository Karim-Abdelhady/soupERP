from pydantic import BaseModel
from datetime import datetime

class StockBalanceResponse(BaseModel):
    id: int
    item_id: int
    batch_id: int | None = None
    serial_id: list[int] | None = None
    warehouse_id: int
    actual_qty: int
    reserved_qty: int
    available_qty: int
    valuation_rate: float
    stock_value: float
    created_at: datetime

    class Config:
        from_attributes = True