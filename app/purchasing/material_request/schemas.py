from pydantic import BaseModel
from app.purchasing.material_request.enums import Status, MaterialRequestType
from datetime import datetime
from decimal import Decimal
from typing import List

class RequestLineResponse(BaseModel):
    id: int
    item_id: int
    quantity: int
    uom_id: int
    conversion_factor: Decimal
    stock_quantity: Decimal
    available_quantity: int
    warehouse_id: int | None = None
    required_by_date: datetime
    description: str | None = None

    class Config:
        from_attributes = True

class RequestResponse(BaseModel):
    id: int
    document_number: str
    request_type: MaterialRequestType
    request_date: datetime
    required_by_date: datetime
    requester_id: int
    status: Status
    remarks: str | None = None

    lines: List[RequestLineResponse]

    class Config:
        from_attributes = True

class RequestLineCreate(BaseModel):
    item_id: int
    quantity: int
    uom_id: int
    conversion_factor: Decimal = Decimal("1.0")
    warehouse_id: int | None = None
    required_by_date: datetime
    description: str | None = None

class RequestCreate(BaseModel):
    document_number: str
    request_type: MaterialRequestType
    request_date: datetime
    required_by_date: datetime
    requester_id: int
    remarks: str | None = None

    lines: List[RequestLineCreate]

class RequestLineUpdate(BaseModel):
    item_id: int | None = None
    quantity: int | None = None
    uom_id: int | None = None
    conversion_factor: Decimal | None = None
    warehouse_id: int | None = None
    required_by_date: datetime | None = None
    description: str | None = None

class RequestUpdate(BaseModel):
    request_type: MaterialRequestType | None = None
    request_date: datetime | None = None
    required_by_date: datetime | None = None
    requester_id: int | None = None
    remarks: str | None = None

    lines: List[RequestLineUpdate] | None = None
