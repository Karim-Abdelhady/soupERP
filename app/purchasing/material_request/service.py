from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.purchasing.material_request.enums import Status, MaterialRequestType
from fastapi import HTTPException, status
from app.purchasing.material_request import repository
from app.purchasing.material_request.schemas import RequestCreate, RequestUpdate
from app.systemadministration.users import repository as UserRepository
from app.inventory.items import repository as ItemRepository
from app.systemadministration.uom import repository as UOMRepository
from app.inventory.warehouses import repository as WarehouseRepository
from app.inventory.stock.stock_balance import repository as SBrepository
from decimal import Decimal

def get_material_requests(db: Session):
    requests = repository.get_material_requests(db)
    if not requests:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "No Material Requests were found")
    return requests

def get_material_request_by_id(db: Session, request_id: int):
    request = repository.get_material_request_by_id(db, request_id)
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Material Request ID is not found")
    return request

def create_material_request(db: Session, new_request: RequestCreate):
    existing_request = repository.get_material_request_by_document_number(db, new_request.document_number)
    if existing_request is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Material Request already exists")


    if new_request.required_by_date < new_request.request_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Required Date can not be before the request date")
    current_date = datetime.now(timezone.utc).date()
    if new_request.request_date.date() < current_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Request Date can not be in the past")
    if new_request.requester_id:
        user = UserRepository.get_user_by_user_id(db, new_request.requester_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "User ID is not found")

    if not new_request.lines:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Material Request must have at least one line")

    prepared_lines: list[dict] = []
    for line in new_request.lines:
        req_date = line.required_by_date if line.required_by_date else new_request.required_by_date

        if line.quantity <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Quantity must be greater than Zero")
        if line.conversion_factor <= Decimal("0"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Conversion Factor must be greater than Zero")
        if new_request.request_type in (MaterialRequestType.TRANSFER, MaterialRequestType.ISSUE) and line.warehouse_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Warehouse ID is required for the choosen material request type")
        
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

        if line.warehouse_id is not None:
            warehouse = WarehouseRepository.get_warehouse_by_id(db, line.warehouse_id)
            if warehouse is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Warehouse ID is not found")
            if not warehouse.is_active:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Warehouse ID is inactive")

            balance = SBrepository.get_stock_balance_by_item_and_warehouse(db, line.item_id, line.warehouse_id)
            available_qty = balance.available_qty if balance is not None else 0
        else:
            balances = SBrepository.get_stock_balance_item_history(db, line.item_id)
            if not balances:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Item ID does not have a stock balance")
            elif isinstance(balances, list):
                available_qty = sum(b.available_qty for b in balance)
            else:
                available_qty = balances.available_qty

        stock_qty = Decimal(line.quantity) * line.conversion_factor
        prepared_lines.append(
            {
                "item_id": line.item_id,
                "quantity": line.quantity,
                "uom_id": line.uom_id,
                "conversion_factor": line.conversion_factor,
                "stock_quantity": stock_qty,
                "available_quantity": available_qty,
                "warehouse_id": line.warehouse_id,
                "required_by_date": req_date,
                "description": line.description
            }
        )

    request_data = {
        "document_number": new_request.document_number,
        "request_type": new_request.request_type,
        "request_date": new_request.request_date,
        "required_by_date": new_request.required_by_date,
        "requester_id": new_request.requester_id,
        "remarks": new_request.remarks,
        "status": Status.DRAFT.value
    }

    return repository.create_material_request(db, request_data, prepared_lines)

def submit_material_request(db: Session, request_id: int):
    request = repository.get_material_request_by_id(db, request_id)
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Material Request ID is not found")
    if request.status != Status.DRAFT.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Only Draft Material Requests can be submitted")
    if request.status == Status.SUBMIT.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Material Request is already submitted")

    request.status = Status.SUBMIT.value

    db.commit()
    db.refresh(request)
    return request

def cancel_material_request(db: Session, request_id: int):
    request = repository.get_material_request_by_id(db, request_id)
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Material Request ID is not found")
    if request.status == Status.CANCEL.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Material Request is already cancelled")
    if request.status != Status.SUBMIT.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Only submitted material requests can be cancelled")

    request.status = Status.CANCEL.value

    db.commit()
    db.refresh(request)
    return request

def update_material_request(db: Session, request_id: int, update_request: RequestUpdate):
    request = repository.get_material_request_by_id(db, request_id)
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Material Request ID is not found")
    if request.status != Status.DRAFT.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Only draft material request can be submitted")
    update_data = update_request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(request, key, value)
    current_date = datetime.now(timezone.utc).date()
    req_date = request.request_date.date() if isinstance(request.request_date, datetime) else request.request_date
    if req_date < current_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Request date can not be in the past")

    if request.requester_id:
        user = UserRepository.get_user_by_user_id(db, request.requester_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "User ID is not found")
    prepared_lines: list[dict] | None = None
    if update_request.lines is not None:
        if not update_request.lines:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Material Request must at least contain one line")
        prepared_lines = []
        for line in update_request.lines:
            if line.item_id is None or line.quantity is None or line.uom_id is None or line.conversion_factor is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Item, quantity, uom_id, and conversion factor are required for each line")
            req_date = line.required_by_date if line.required_by_date is not None else request.required_by_date
            if line.quantity <= 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Quantity can not be negative")
            if line.conversion_factor <= Decimal("0"):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Conversion Factor must be greater than Zero")
            if request.request_type in (MaterialRequestType.TRANSFER, MaterialRequestType.ISSUE) and line.warehouse_id is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Warehouse ID is required for Material Transfer or Material Issue")

            item = ItemRepository.get_item_by_id(db, line.item_id)
            if item is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Item ID is not found")
            if not item.is_active:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Item ID is inactive")

            uom = UOMRepository.get_uom_by_id(db, line.uom_id)
            if uom is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "UOM ID is not found")
            if not uom.is_active:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "UOM ID is inactive")

            if line.warehouse_id is not None:
                warehouse = WarehouseRepository.get_warehouse_by_id(db, line.warehouse_id)
                if warehouse is None:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Warehouse ID is not found")
                if not warehouse.is_active:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Warehouse ID is inactive")

                balance = SBrepository.get_stock_balance_by_item_and_warehouse(db, line.item_id, line.warehouse_id)
                available_qty = balance.available_qty if balance is not None else 0
            else:
                balances = SBrepository.get_stock_balance_item_history(db, line.item_id)
                if not balances:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Item ID does not have a stock balance")
                elif isinstance(balances, list):
                    available_qty = sum(b.available_qty for b in balances)
                else:
                    available_qty = balance.available_qty
            stock_qty = Decimal(line.quantity) * line.conversion_factor
            prepared_lines.append(
                {
                    "item_id": line.item_id,
                    "quantity": line.quantity,
                    "uom_id": line.uom_id,
                    "conversion_factor": line.conversion_factor,
                    "stock_quantity": stock_qty,
                    "available_quantity": available_qty,
                    "warehouse_id": line.warehouse_id,
                    "required_by_date": req_date,
                    "description": line.description
                }
            )            
    return repository.update_material_request(db, request, prepared_lines)

