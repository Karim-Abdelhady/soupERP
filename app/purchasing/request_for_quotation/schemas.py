from pydantic import BaseModel
from datetime import datetime
from app.purchasing.request_for_quotation.enums import Status, ResponseStatus
from typing import List

class QuotationLineResponse(BaseModel):
    id: int
    request_for_quotation_id: int
    item_id: int
    quantity: int
    uom_id: int
    required_by_date: datetime
    description: str | None = None

    class Config:
        from_attributes = True

class QuotationSupplierResponse(BaseModel):
    id: int
    request_for_quotation_id: int
    supplier_id: int
    sent_at: datetime | None = None
    response_status: ResponseStatus
    remarks: str | None = None

    class Config:
        from_attributes = True

class QuotationResponse(BaseModel):
    id: int
    document_number: str
    request_date: datetime
    required_by_date: datetime
    status: Status
    remarks: str | None = None
    lines: List[QuotationLineResponse]
    rfq_supplier: List[QuotationSupplierResponse]
    
    class Config:
        from_attributes = True

class QuotationLineCreate(BaseModel):
    item_id: int
    quantity: int
    uom_id: int
    required_by_date: datetime | None = None
    description: str | None = None

class QuotationSupplierCreate(BaseModel):
    supplier_id: int

class QuotationCreate(BaseModel):
    document_number: str
    request_date: datetime
    required_by_date: datetime
    remarks: str
    lines: List[QuotationLineCreate]
    rfq_supplier: List[QuotationSupplierCreate]

class QuotationLineUpdate(BaseModel):
    item_id: int | None = None
    quantity: int | None = None
    uom_id: int | None = None
    required_by_date: datetime | None = None
    description: str | None = None

class QuotationUpdate(BaseModel):
    request_date: datetime | None = None
    required_by_date: datetime | None = None
    remarks: str | None = None

    lines: List[QuotationLineUpdate] | None = None

class SupplierReplyCreate(BaseModel):
    remarks: str
    declined: bool = False