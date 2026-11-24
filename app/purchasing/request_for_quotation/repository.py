from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from app.purchasing.request_for_quotation.schemas import QuotationCreate, QuotationUpdate
from app.purchasing.request_for_quotation.models import RequestForQuotation, RequestForQuotationLine, RequestForQuotationSupplier

def get_request_quotations(db:Session):
    statement = (
        select(RequestForQuotation)
        .options(
            selectinload(RequestForQuotation.lines),
            selectinload(RequestForQuotation.rfq_supplier)
        )
    )
    return db.scalars(statement).all()

def get_request_quotation_by_id(db: Session, request_id: int):
    statement = (
        select(RequestForQuotation)
        .options(
            selectinload(RequestForQuotation.lines),
            selectinload(RequestForQuotation.rfq_supplier)
        )
        .where(RequestForQuotation.id == request_id)
    )
    return db.scalar(statement)

def get_request_quotation_by_document_number(db: Session, document_number:str):
    statement = (
        select(RequestForQuotation)
        .options(
            selectinload(RequestForQuotation.lines),
            selectinload(RequestForQuotation.rfq_supplier)
        )
        .where(RequestForQuotation.document_number == document_number)
    )
    return db.scalar(statement)

def create_request_quotation(db: Session, new_request: RequestForQuotation, lines_data: list[dict], supplier_data: list[dict]):
    new_data = RequestForQuotation(**new_request)
    for line in lines_data:
        new_data.lines.append(RequestForQuotationLine(**line))
    for supplier in supplier_data:
        new_data.rfq_supplier.append(RequestForQuotationSupplier(**supplier))
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return new_data

def update_request_quotation(db: Session, update_request: RequestForQuotation, lines_data: list[dict] | None = None):
    if lines_data is not None:
        update_request.lines.clear()
        db.flush()
        for line in lines_data:
            update_request.lines.append(RequestForQuotation(**line))
        db.commit()
        db.refresh(update_request)
        return update_request
