from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.inventory.stock.stock_reconciliation.schemas import StockReconciliationCreate, StockReconciliationUpdate
from app.inventory.stock.stock_reconciliation import repository
from app.inventory.stock.stock_reconciliation.models import StockReconciliation, StockReconciliationLine
from app.inventory.stock.stock_reconciliation.enums import Status
from app.inventory.stock.stock_balance import repository as SBrepository
from app.inventory.stock.stock_ledger.schemas import StockLedgerCreate
from app.inventory.stock.stock_ledger.service import create_stock_ledger_entry
from datetime import datetime, timezone
from app.inventory.tracking_items import repository as TrackRepository
from app.inventory.tracking_items.models import SerialNumber
from app.inventory.tracking_items.enums import SerialStatus
from app.inventory.items import repository as ItemRepository
from app.inventory.warehouses import repository as WarehouseRepository

def create_stock_reconciliation(db: Session, new_stock_reconciliation: StockReconciliationCreate):
    existing_stock_reconciliation = repository.get_stock_reconciliation_by_document_number(db, new_stock_reconciliation.document_number)
    if existing_stock_reconciliation is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Stock Reconciliation already exists")

    new_data = new_stock_reconciliation.model_dump(exclude_unset=True)
    lines_data = new_data.pop("stock_reconciliation_lines", [])
    new_data["status"] = Status.DRAFT
    db_stock_reconciliation = StockReconciliation(**new_data)
    db.add(db_stock_reconciliation)
    db.flush()

    for line in lines_data:
        if hasattr(line, "model_dump"):
            line_dict = line.model_dump()
        elif isinstance(line, dict):
            line_dict = line
        else:
            line_dict = line.__dict__

        batch_id = line_dict.get("batch_id")
        serial_id = line_dict.get("serial_id")
        item_id = line_dict.get("item_id")

        check_item_and_warehouse_active_status(db, item_id, db_stock_reconciliation.warehouse_id)

        if batch_id:
            batch = TrackRepository.get_batch_number_by_id(db, batch_id)
            if batch is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Batch ID is not found")
            if batch.item_id != item_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Batch does not belong to the item")
            if batch.expiry_date:
                current_date = datetime.now(timezone.utc)
                batch_exp = batch.expiry_date.date() if isinstance(batch.expiry_date, datetime) else batch.expiry_date

                if batch_exp < current_date:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Batch is expired")
                
        counted_qty = line_dict.get("counted_qty", 0)
        if counted_qty < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Quantity can not be less than Zero")
        uom_id = line_dict.get("uom_id", 1)
        conversion_factor = line_dict.get("conversion_factor", 1)
        balance = SBrepository.get_stock_balance_by_item_warehouse_and_batch(db, item_id=item_id, warehouse_id=db_stock_reconciliation.warehouse_id, batch_id=batch_id)
        expected_qty = balance.actual_qty if balance else 0
        difference_qty = counted_qty - expected_qty

        db_line = StockReconciliationLine(
            reconciliation_id = db_stock_reconciliation.id,
            item_id = item_id,
            batch_id = batch_id,
            serial_id = serial_id,
            expected_qty=expected_qty,
            counted_qty= counted_qty,
            difference_qty = difference_qty,
            uom_id=uom_id,
            conversion_factor=conversion_factor,
            valuation_rate=balance.valuation_rate if balance else 0.0
        )
        db.add(db_line)

        if serial_id:
            if len(serial_id) != int(counted_qty):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail ="Mismatch, Line quantity is different from the expected quantity")

    return repository.create_stock_reconciliation(db, db_stock_reconciliation)

def submit_stock_reconciliation(db: Session, rec_id: int):
    stock_reconciliation = repository.get_stock_reconciliation_by_id(db, rec_id)
    if stock_reconciliation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Stock Reconciliation ID is not found")

    if stock_reconciliation.status == Status.SUBMITTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Stock Reconciliation is already submitted")

    if not stock_reconciliation.stock_reconciliation_lines:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Stock Reconciliation does not have any lines")

    for line in stock_reconciliation.stock_reconciliation_lines:
        counted_serial_ids = getattr(line, "serial_id", []) or []
        balance = SBrepository.get_stock_balance_by_item_warehouse_and_batch(db, item_id=line.item_id, warehouse_id=stock_reconciliation.warehouse_id, batch_id=line.batch_id)
        current_serials = list(balance.serial_id) if balance and balance.serial_id else []

        for s_id in counted_serial_ids:
            serial = TrackRepository.get_serial_number_by_id(db, s_id)
            if serial is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Serial ID is not found")
            serial.status = SerialStatus.INSTOCK.value
            serial.batch_id = line.batch_id

        missing_serial_ids = [s for s in current_serials if s not in counted_serial_ids]
        for s_id in missing_serial_ids:
            serial = TrackRepository.get_serial_number_by_id(db, s_id)
            if serial:
                serial.status = SerialStatus.EXPIRED

        if line.difference_qty != 0:
            payload = StockLedgerCreate(
                item_id = line.item_id,
                batch_id = line.batch_id,
                serial_id = counted_serial_ids,
                warehouse_id = stock_reconciliation.warehouse_id,
                quantity_delta = line.difference_qty,
                incoming_rate = line.valuation_rate if line.difference_qty > 0 else 0.0,
                outgoing_rate = line.valuation_rate if line.difference_qty < 0 else 0.0,
                voucher_type = "Stock Reconciliation",
                voucher_id = stock_reconciliation.document_number,
                voucher_line_id = f"{stock_reconciliation.document_number}-L{line.id}"
            )
            create_stock_ledger_entry(db, payload)
    
    
    stock_reconciliation.status = Status.SUBMITTED
    stock_reconciliation.submitted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(stock_reconciliation)
    return stock_reconciliation

def cancel_stock_reconciliation(db: Session, rec_id: int):
    stock_reconciliation = repository.get_stock_reconciliation_by_id(db, rec_id)
    if stock_reconciliation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Stock Reconciliation ID is not found")

    if stock_reconciliation.status == Status.CANCELED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Stock Reconciliation is already canceled")

    if stock_reconciliation.status == Status.SUBMITTED:
        for line in stock_reconciliation.stock_reconciliation_lines:
            if line.difference_qty != 0:
                payload = StockLedgerCreate(
                    item_id = line.item_id,
                    batch_id = line.batch_id,
                    serial_id= line.serial_id,
                    warehouse_id = stock_reconciliation.warehouse_id,
                    quantity_delta = -line.difference_qty,
                    incoming_rate = line.valuation_rate if line.difference_qty > 0 else 0.0,
                    outgoing_rate = line.valuation_rate if line.difference_qty < 0 else 0.0,
                        voucher_type = "Stock Reconciliation",
                    voucher_id = stock_reconciliation.document_number,
                    voucher_line_id = f"{stock_reconciliation.document_number}-L{line.id}"
                )
                create_stock_ledger_entry(db, payload)
    stock_reconciliation.status = Status.CANCELED
    stock_reconciliation.canceled_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(stock_reconciliation)
    return stock_reconciliation

def update_stock_reconciliation(db: Session, rec_id: int, update_stock_rec: StockReconciliationUpdate):
    stock_reconciliation = repository.get_stock_reconciliation_by_id(db, rec_id)
    if stock_reconciliation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Stock Reconciliation ID is not found")

    update_data = update_stock_rec.model_dump(exclude_unset=True)
    lines_data = update_data.pop("stock_reconciliation_lines", None)

    if StockReconciliation.status != Status.DRAFT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Stock Reconciliation can not be edited after submitted/canceled")
 
    for key, value in update_data.items():
        setattr(stock_reconciliation, key, value)

    if lines_data is not None:
        for existing_line in list(stock_reconciliation.stock_reconciliation_lines):
            db.delete(existing_line)
        db.flush()
        for line in lines_data:
            if isinstance(line, dict):
                item_id = line.get("item_id")
                counted_qty = line.get("counted_qty", 0)
                uom_id = line.get("uom_id", 1)
                conversion_factor = line.get("conversion_factor", 1)
            else:
                item_id = line.item_id
                counted_qty = line.counted_qty
                uom_id = getattr(line, "uom_id", 1)
                conversion_factor = getattr(line, "conversion_factor", 1)

            balance = SBrepository.get_stock_balance_by_item_and_warehouse(db, item_id=item_id, warehouse_id=stock_reconciliation.warehouse_id)
            expected_qty = balance.actual_qty if balance else 0
            difference_qty = counted_qty - expected_qty

            db_line = StockReconciliationLine(
                reconciliation_id=stock_reconciliation.id,
                item_id=item_id,
                expected_qty=expected_qty,
                counted_qty=counted_qty,
                difference_qty=difference_qty,
                uom_id=uom_id,
                conversion_factor=conversion_factor,
                valuation_rate=balance.valuation_rate if balance else 0.0
            )
            db.add(db_line)

    db.commit()
    db.refresh(stock_reconciliation)
    return stock_reconciliation

def check_item_and_warehouse_active_status(db: Session, item_id: int, *warehouse_ids):
    item = ItemRepository.get_item_by_id(db, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Item ID is not found")
    if hasattr(item, "is_active") and not item.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Item is inactive")

    for warehouse_id in warehouse_ids:
        if warehouse_id is not None:
            warehouse = WarehouseRepository.get_warehouse_by_id(db, warehouse_id)
            if warehouse is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Warehouse ID is not found")
            if not warehouse.is_active:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Warehouse ID is inactive")


def get_stock_reconciliations(db: Session):
    stock_reconciliations = repository.get_stock_reconciliations(db)
    if not stock_reconciliations:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "No Stock Reconciliations were found")
    return stock_reconciliations

def get_stock_reconciliation_by_id(db: Session, rec_id: int):
    stock_reconciliation = repository.get_stock_reconciliation_by_id(db, rec_id)
    if stock_reconciliation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Stock Reconciliation ID is not found")
    return stock_reconciliation

def get_stock_reconciliation_by_item_and_warehouse(db: Session, warehouse_id: int, item_id: int):
    stock_reconciliation = repository.get_stock_reconciliation_by_item_and_warehouse(db, warehouse_id, item_id)
    if not stock_reconciliation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Item or Warehouse is not found")
    return stock_reconciliation

def get_stock_reconciliation_by_item_id(db: Session, item_id: int):
    stock_reconciliation = repository.get_stock_reconciliation_by_item_id(db, item_id)
    if stock_reconciliation is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail = "Stock Reconciliation with Item ID is not found")
    return stock_reconciliation

def get_stock_reconciliation_by_warehouse_id(db: Session, warehouse_id: int):
    stock_reconciliation = repository.get_stock_reconciliation_by_warehouse_id(db, warehouse_id)
    if not stock_reconciliation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Stock Reconciliation with Warehouse ID is not found")
    return stock_reconciliation