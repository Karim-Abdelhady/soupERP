from pydantic import BaseModel
from datetime import datetime
from app.inventory.stock.stock_reservation.enums import ReservationStatus

class StockReservationCreate(BaseModel):
    item_id: int
    warehouse_id: int
    batch_id: int | None = None
    serial_id: list[int] | None = None
    quantity: int


    class Config:
        from_attributes = True

class StockReservationResponse(BaseModel):
    id: int
    item_id: int
    warehouse_id: int
    batch_id: int | None = None
    serial_id: list[int] | None = None
    quantity: int
    source_document_type: str | None = None
    source_document_id: str | None = None
    source_line_id: int | None = None
    status: ReservationStatus
    reserved_at: datetime
    released_at: datetime | None = None
    fulfilled_at: datetime | None = None