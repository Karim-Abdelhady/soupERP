from sqlalchemy.orm import Session
from app.purchasing.request_for_quotation import repository
from fastapi import HTTPException, status
from app.purchasing.request_for_quotation.schemas import QuotationCreate, QuotationUpdate, QuotationSupplierCreate, SupplierReplyCreate
from datetime import datetime, timezone
from app.inventory.items import repository as ItemRepository
from app.systemadministration.uom import repository as UOMRepository
from app.systemadministration.suppliers import repository as SupplierRepository
from app.purchasing.request_for_quotation.enums import ResponseStatus, Status
from app.purchasing.request_for_quotation.models import RequestForQuotationSupplier

def get_request_quotations(db: Session):
    quotations = repository.get_request_quotations(db)
    if not quotations:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "No Request for Quotations were found")
    return quotations

def get_request_quotation_by_id(db: Session, request_id:int):
    quotation = repository.get_request_quotation_by_id(db, request_id)
    if quotation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Request Quotation ID is not found")
    return quotation

def create_request_quotation(db: Session, new_request: QuotationCreate):
    existing_quotation = repository.get_request_quotation_by_document_number(db, new_request.document_number)
    if existing_quotation is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Request Quotation already exists")

    if new_request.required_by_date < new_request.request_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Required date can not be before the request date")
    current_date = datetime.now(timezone.utc).date()
    req_date = new_request.request_date.date() if isinstance(new_request.request_date, datetime) else new_request.request_date
    if req_date < current_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Request date can not be in the past")

    if not new_request.lines:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Request Quotation must at least contain one line")

    if not new_request.rfq_supplier:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Request Quotation must at least contain one supplier")

    prepared_lines: list[dict] = []
    for line in new_request.lines:
        req_date = line.required_by_date if line.required_by_date else new_request.required_by_date
        item = ItemRepository.get_item_by_id(db, line.item_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Item ID is not found")
        if not item.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Item ID is inactive")

        uom = UOMRepository.get_uom_by_id(db, line.uom_id)
        if uom is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "UOM ID is not found")
        if not uom.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "UOM ID is inactive")

        if line.quantity <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Quantity must be greater than Zero")

        if req_date < new_request.request_date:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Required date can not be before request date")

        prepared_lines.append(
            {
                "item_id": line.item_id,
                "quantity": line.quantity,
                "uom_id": line.uom_id,
                "required_by_date": req_date,
                "description": line.description 
            }
        )

    seen_suppliers: set[int] = set()
    suppliers: list[dict] = []
    for supplier in new_request.rfq_supplier:
        if supplier.supplier_id in seen_suppliers:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Duplicate supplier ID is not allowed in the same Request Quotation")
        seen_suppliers.add(supplier.supplier_id)

        sup = SupplierRepository.get_supplier_by_supplier_id(db, supplier.supplier_id)
        if sup is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Supplier ID is not found")

        suppliers.append(
            {
                "supplier_id": supplier.supplier_id,
                "response_status": ResponseStatus.PENDING.value
            }
        )

    request_data = {
        "document_number": new_request.document_number,
        "request_date": new_request.request_date,
        "required_by_date": new_request.required_by_date,
        "remarks": new_request.remarks,
        "status": Status.DRAFT.value
    }

    return repository.create_request_quotation(db, request_data, prepared_lines, suppliers)

def submit_request_quotation(db: Session, request_id: int):
    quotation = repository.get_request_quotation_by_id(db, request_id)
    if quotation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Request Quotation ID is not found")

    if quotation.status in (Status.SENT.value, Status.PARTIAL.value, Status.QUOTED.value):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Request Quotation has been already sent")

    if quotation.status != Status.DRAFT.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Only draft Request Quotation can be submitted")

    quotation.status = Status.SENT.value
    db.commit()
    db.refresh(quotation)
    return quotation

def cancel_request_quotation(db: Session, request_id: int):
    quotation = repository.get_request_quotation_by_id(db, request_id)
    if quotation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Request Quotation ID is not found")

    if quotation.status not in (Status.SENT.value, Status.PARTIAL.value, Status.QUOTED.value):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Only submitted Request Quotation can be cancelled")

    if quotation.status == Status.CANCELLED.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Request Quotation is already cancelled")

    quotation.status = Status.CANCELLED.value
    db.commit()
    db.refresh(quotation)
    return quotation

def update_request_quotation(db: Session, request_id: int, update_quotation: QuotationUpdate):
    quotation = repository.get_request_quotation_by_id(db, request_id)
    if quotation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Request Quotation ID is not found")

    if quotation.status != Status.DRAFT.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Only draft request quotation can be edited")
    update_data = update_quotation.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(quotation, key, value)
    current_date = datetime.now(timezone.utc).date()
    req_date = quotation.request_date.date() if isinstance(quotation.request_date, datetime) else quotation.request_date
    if req_date < current_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Request Date can not be in the past")
    if update_quotation.required_by_date < update_quotation.request_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Required date can not be before request date")
    prepared_lines: list[dict] | None = None
    if update_quotation.lines is not None:
        if not update_quotation.lines:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Request Quotation must at least contain one line")
        prepared_lines = []
        for line in update_quotation.lines:
            if line.item_id is None or line.quantity is None or line.uom_id or line.required_by_date:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, detail = "Item, quantity, uom, and required_by_date are required")
            req_date = line.required_by_date if line.required_by_date else update_quotation.required_by_date
            if line.quantity <= 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Quantity must be greater than zero")

            item = ItemRepository.get_item_by_id(db, line.item_id)
            if item is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Item ID is not found")
            if not item.is_active:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Item ID is inactive")

            uom = UOMRepository.get_uom_by_id(db, line.uom_id)
            if uom is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "UOM ID is not found")
            if not uom.is_active:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "UOM ID is inactive")

            prepared_lines.append(
                {
                    "item_id": line.item_id,
                    "quantity": line.quantity,
                    "uom_id": line.uom_id,
                    "required_by_date": line.required_by_date,
                    "description": line.description
                }
            )
    return repository.update_request_quotation(db, quotation, prepared_lines)

def supplier_reply_for_request_quotation(db: Session, request_id: int, supplier_id: int, new_reply: SupplierReplyCreate):
    quotation = repository.get_request_quotation_by_id(db, request_id)
    if quotation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Request Quotation ID is not found")

    if quotation.status == Status.DRAFT.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Request Quotation must be sent before sending a supplier reply")

    rfq_supplier = None
    for row in quotation.rfq_supplier:
        if row.supplier_id == supplier_id:
            rfq_supplier = row
            break

    if rfq_supplier is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Supplier is not invited to this Request Quotation")

    rfq_supplier.remarks = new_reply.remarks
    rfq_supplier.response_status = (ResponseStatus.DECLINED.value if new_reply.declined else ResponseStatus.RESPONDED.value)

    total_suppliers = len(quotation.rfq_supplier)
    responded_suppliers = 0
    for supp in quotation.rfq_supplier:
        if supp.response_status in (ResponseStatus.RESPONDED.value, ResponseStatus.DECLINED.value):
            responded_suppliers += 1

        if total_suppliers > 0 and responded_suppliers == total_suppliers:
            quotation.status = Status.QUOTED.value
        elif total_suppliers > 0 and responded_suppliers < total_suppliers:
            quotation.status = Status.PARTIAL.value
        else:
            pass

    db.commit()
    db.refresh(quotation)
    return quotation