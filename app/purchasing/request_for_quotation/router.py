from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.purchasing.request_for_quotation import service
from app.purchasing.request_for_quotation.schemas import QuotationResponse, QuotationCreate, QuotationUpdate, SupplierReplyCreate
from typing import List
from database.database import get_db

router = APIRouter()

@router.get("/requestquotations/", response_model=List[QuotationResponse], tags = ["Request For Quotation"])
def get_request_quotations(db: Session = Depends(get_db)):
    return service.get_request_quotations(db)

@router.get("/requestquotations/{quotation_id}", response_model=QuotationResponse, tags = ["Request For Quotation"])
def get_request_quotation_by_id(quotation_id: int, db: Session = Depends(get_db)):
    return service.get_request_quotation_by_id(db, quotation_id)

@router.post("/requestquotations/draft", response_model = QuotationResponse, tags = ["Request For Quotation"])
def create_request_quotation(new_quotation: QuotationCreate, db: Session = Depends(get_db)):
    return service.create_request_quotation(db, new_quotation)

@router.post("/requestquotations/submit/{quotation_id}", response_model = QuotationResponse, tags = ["Request For Quotation"])
def submit_request_quotation(quotation_id: int, db: Session = Depends(get_db)):
    return service.submit_request_quotation(db, quotation_id)

@router.post("/requestquotations/cancel/{quotation_id}", response_model= QuotationResponse, tags = ["Request For Quotation"])
def cancel_request_quotation(quotation_id: int, db: Session = Depends(get_db)):
    return service.cancel_request_quotation(db, quotation_id)

@router.patch("/requestquotations/update/{quotation_id}", response_model = QuotationResponse, tags = ["Request For Quotation"])
def update_request_quotation(quotation_id: int, update_quotation: QuotationUpdate, db: Session = Depends(get_db)):
    return service.update_request_quotation(db, quotation_id, update_quotation)

@router.patch("/requestquotations/{quotation_id}/reply/{supplier_id}", response_model = QuotationResponse, tags = ["Request For Quotation"])
def supplier_reply_for_request_quotation(quotation_id: int, supplier_id: int, reply: SupplierReplyCreate, db: Session = Depends(get_db)):
    return service.supplier_reply_for_request_quotation(db, quotation_id, supplier_id, reply)