from pydantic import BaseModel
from datetime import datetime

class ReorderResponse(BaseModel):
    id: int
    item_id: int
    warehouse_id: int
    reorder_level: int
    safety_stock_level: int
    reorder_qty: int
    maximum_order_qty: int | None = None
    lead_time_days: int | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ReorderCreate(BaseModel):
    item_id: int
    warehouse_id: int
    reorder_level: int
    safety_stock_level: int
    reorder_qty: int
    maximum_order_qty: int | None = None
    lead_time_days: int | None = None


class ReorderUpdate(BaseModel):
    item_id: int | None = None
    warehouse_id: int | None = None
    reorder_level: int | None = None
    safety_stock_level: int | None = None
    reorder_qty: int | None = None
    maximum_order_qty: int | None = None
    lead_time_days: int | None = None

class Activation(BaseModel):
    is_active: bool | None = None