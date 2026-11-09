from pydantic import BaseModel
from datetime import datetime
from app.inventory.stock.stock_reservation.enums import Status

class StockReservationCreate(BaseModel):
    item_id: int
    warehouse_id: int
    quantity: int
    source_document_type: str
    source_document_id: str
    source_line_id: int
    status: Status
    reserved_at: datetime
    released_at: datetime | None = None
    fulfilled_at: datetime | None = None

    class Config:
        from_attributes = True

class StockReservationResponse(BaseModel):
    id: int
    item_id: int
    warehouse_id: int
    quantity: int
    source_document_type: str
    source_document_id: str
    source_line_id: int
    status: Status
    reserved_at: datetime
    released_at: datetime | None = None
    fulfilled_at: datetime | None = None