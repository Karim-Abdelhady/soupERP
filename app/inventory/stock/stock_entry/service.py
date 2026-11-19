from sqlalchemy.orm import Session
from app.inventory.stock.stock_entry import repository
from app.inventory.stock.stock_entry.schemas import StockEntryCreate, StockEntryUpdate
from app.inventory.stock.stock_entry.models import StockEntry, StockEntryLine
from app.inventory.stock.stock_ledger.models import StockLedger
from app.inventory.stock.stock_ledger.schemas import StockLedgerCreate
from app.inventory.stock.stock_entry.enums import Status, Purpose
from app.inventory.stock.stock_ledger import repository as SLrepository
from app.inventory.stock.stock_ledger.service import create_stock_ledger_entry
from datetime import datetime,timezone
from fastapi import HTTPException,status
from app.inventory.warehouses import repository as WarehouseRepository
from app.inventory.stock.stock_balance import repository as SBrepository
from app.inventory.tracking_items.models import SerialNumber
from app.inventory.tracking_items import repository as TrackRepository
from app.inventory.tracking_items.enums import SerialStatus
from app.inventory.stock.stock_balance.models import StockBalance
from sqlalchemy import select
from app.inventory.items import repository as ItemRepository


def validate_warehouse_rules(purpose: Purpose, source_wh_int: int | None, target_wh_int: int | None):
    if purpose == Purpose.TRANSFER:
        if not source_wh_int or not target_wh_int:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Source and Target warehouse are required")
        if source_wh_int == target_wh_int:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Source and Target warehouse cannot be the same warehouse")
    elif purpose in (Purpose.ISSUE, Purpose.SCRAP):
        if not source_wh_int or target_wh_int:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Source Warehouse is required, and Target Warehouse must be null")
    elif purpose == Purpose.RECEIPT:
        if source_wh_int or not target_wh_int:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Source Warehouse must be null, and Target Warehouse is required")
    elif purpose in (Purpose.MANUFACTURE, Purpose.REPACK):
        if not source_wh_int and not target_wh_int:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "At least one warehouse specified")


def create_stock_entry(db: Session, new_stock: StockEntryCreate):
    existing_stock_entry = repository.get_stock_entry_by_document_number(db, new_stock.document_number)
    if existing_stock_entry is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail = "Stock Entry already exists.")

    validate_warehouse_rules(new_stock.purpose, new_stock.source_warehouse_id, new_stock.target_warehouse_id)

    if not new_stock.stock_entry_lines:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Stock Entry must have at least one line")
    
    new_data = new_stock.model_dump(exclude_unset=True)
    lines_data = new_data.pop("stock_entry_lines", [])
    new_data["status"] = Status.DRAFT
    db_stock_entry = StockEntry(**new_data)
    db.add(db_stock_entry)
    db.flush()

    for line in lines_data:
        if isinstance(line, dict):
            item_id = line.get("item_id")
            line_src = line.get("source_warehouse_id")
            line_tgt = line.get("target_warehouse_id")
        else:
            item_id = getattr(line, "item_id", None)
            line_src = getattr(line, "source_warehouse_id", None)
            line_tgt = getattr(line, "target_warehouse_id", None)
        src_wh = line_src or new_stock.source_warehouse_id
        tgt_wh = line_tgt or new_stock.target_warehouse_id
        check_item_and_warehouse_active_status(db, item_id , src_wh, tgt_wh)
        quantity = line.get("quantity", 0)
        if quantity is None or quantity <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail = "Quantity must be greater than Zero")
        conversion_factor = line.get("conversion_factor", 1.0)
        if conversion_factor is None or conversion_factor <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Conversion factor must be greater than Zero")
        unit_cost = line.get("unit_cost", 0.0)
        stock_quantity = quantity * conversion_factor
        line_amount = quantity * unit_cost

        batch_id = line.get("batch_id")
        serial_id = line.get("serial_id")
        item_id = line.get("item_id")
        if batch_id:
            batch = TrackRepository.get_batch_number_by_id(db, batch_id)
            if batch is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Batch ID is not found")       
            if batch.item_id != item_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Batch does not belong to the item")
            if batch.expiry_date:
                current_date = datetime.now(timezone.utc).date()
                batch_exp = batch.expiry_date.date() if isinstance(batch.expiry_date, datetime) else batch.expiry_date
                if batch_exp < current_date:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Batch is already Expired")

        if serial_id and len(serial_id) != int(stock_quantity):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Mismatch, stock quantity is different from the provided serial numbers")
        line["stock_quantity"] = stock_quantity
        line["line_amount"] = line_amount
        db_line = StockEntryLine(
            stock_entry_id=db_stock_entry.id,
            item_id=item_id,
            source_warehouse_id=src_wh,
            target_warehouse_id=tgt_wh,
            quantity=quantity,
            uom_id=line.get("uom_id"),
            conversion_factor=conversion_factor,
            stock_quantity=line.get("stock_quantity"),
            unit_cost=unit_cost,
            line_amount=line.get("line_amount"),
            batch_id=batch_id,
            serial_id = serial_id
        )
        db.add(db_line)
        db.flush()

    return repository.create_stock_entry(db, db_stock_entry)

def submit_stock_entry(db: Session, stock_id: int):
    stock_entry = repository.get_stock_entry_by_id(db, stock_id)
    if stock_entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Stock Entry ID is not found")

    if stock_entry.status == Status.SUBMITTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Stock Entry is already submitted")

    if stock_entry.status == Status.CANCELED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Stock Entry is already cancelled")

    if not stock_entry.stock_entry_lines:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Cannot submit a Stock Entry without a line")

    if stock_entry.source_warehouse_id is not None:
        src_warehouse = WarehouseRepository.get_warehouse_by_id(db, stock_entry.source_warehouse_id)
        if src_warehouse is None or not src_warehouse.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Source Warehouse is Invalid")
    if stock_entry.target_warehouse_id is not None:
        tgt_warehouse = WarehouseRepository.get_warehouse_by_id(db, stock_entry.target_warehouse_id)
        if tgt_warehouse is None or not tgt_warehouse.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Target Warehouse is Invalid")


    for line in stock_entry.stock_entry_lines:
        src_wh = line.source_warehouse_id or stock_entry.source_warehouse_id
        tgt_wh = line.target_warehouse_id or stock_entry.target_warehouse_id

        serial_id = getattr(line, "serial_id", [])
        if serial_id:
            for s_id in serial_id:
                serial = TrackRepository.get_serial_number_by_id(db, s_id)
                if serial is None:
                    serial = SerialNumber(
                        item_id = line.item_id,
                        serial_id = s_id,
                        status = SerialStatus.INSTOCK.value,
                        batch_id = line.batch_id
                    )
                    db.add(serial)
                else:
                    serial.status = SerialStatus.INSTOCK.value
                    serial.batch_id = line.batch_id

        if src_wh:
            balance = SBrepository.get_stock_balance_by_item_warehouse_and_batch(db, line.item_id, src_wh, line.batch_id)

            available_qty = balance.actual_qty if balance else 0.0

            if available_qty < line.stock_quantity:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Insufficient Stock for Item ID")
        
            outgoing = StockLedgerCreate(
                stock_entry_id = line.stock_entry_id,
                item_id=line.item_id,
                warehouse_id=src_wh,
                batch_id = line.batch_id,
                serial_id = line.serial_id,
                quantity_delta=-line.stock_quantity,
                incoming_rate=0.0,
                outgoing_rate=line.unit_cost,
                voucher_type="Stock Entry",
                voucher_id=stock_entry.document_number,
                voucher_line_id=f"{stock_entry.document_number}-L{line.id}"
            )
            create_stock_ledger_entry(db, outgoing)
        if tgt_wh:
            ingoing = StockLedgerCreate(
                stock_entry_id = line.stock_entry_id,
                item_id = line.item_id,
                warehouse_id = tgt_wh,
                batch_id=line.batch_id,
                serial_id=line.serial_id,
                quantity_delta=line.stock_quantity,
                incoming_rate = line.unit_cost,
                outgoing_rate = 0.0,
                voucher_type = "Stock Entry",
                voucher_id = stock_entry.document_number,
                voucher_line_id=f"{stock_entry.document_number}-L{line.id}"
            )
            create_stock_ledger_entry(db, ingoing)

    stock_entry.status = Status.SUBMITTED
    stock_entry.submitted_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(stock_entry)
    return stock_entry

def cancel_stock_entry(db: Session, stock_id: int):
    stock_entry = repository.get_stock_entry_by_id(db, stock_id)
    if stock_entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Stock Entry ID is not found")
    if stock_entry.status == Status.CANCELED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Stock Entry is already canceled")
    if stock_entry.status != Status.SUBMITTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Only submitted stock entries can be canceled")
    
    for line in stock_entry.stock_entry_lines:
        tgt_wh = line.target_warehouse_id or stock_entry.target_warehouse_id
        if tgt_wh:
            if getattr(line, "batch_id", None):
                tgt_balance = SBrepository.get_stock_balance_by_item_warehouse_and_batch(db, line.item_id, tgt_wh, line.batch_id)
            else:
                tgt_balance = SBrepository.get_stock_balance_by_item_and_warehouse(db, line.item_id, tgt_wh)

            if tgt_balance is None or tgt_balance.actual_qty < line.stock_quantity:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=("Insuffient Stock"),)

            if getattr(line, "serial_id", None):
                for s_id in line.serial_id:
                    serial = TrackRepository.get_serial_number_by_id(db, s_id)
                    if serial is None or serial.status != SerialStatus.INSTOCK.value:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=("Serial ID is no longer available"))

    for line in stock_entry.stock_entry_lines:
        src_wh = line.source_warehouse_id or stock_entry.source_warehouse_id
        tgt_wh = line.target_warehouse_id or stock_entry.target_warehouse_id

        if src_wh:
            reversal_outgoing = StockLedgerCreate(
                stock_entry_id = line.stock_entry_id,
                item_id=line.item_id,
                batch_id = line.batch_id,
                serial_id = line.serial_id,
                warehouse_id=src_wh,
                quantity_delta=line.stock_quantity,
                incoming_rate=line.unit_cost,
                outgoing_rate=0.0,
                voucher_type="Stock Entry",
                voucher_id=stock_entry.document_number,
                voucher_line_id=f"{stock_entry.document_number}-L{line.id}"
            )
            create_stock_ledger_entry(db, reversal_outgoing)
        if tgt_wh:
            reversal_ingoing = StockLedgerCreate(
                stock_entry_id = line.stock_entry_id,
                item_id = line.item_id,
                batch_id = line.batch_id,
                serial_id=line.serial_id,
                warehouse_id = tgt_wh,
                quantity_delta=-line.stock_quantity,
                incoming_rate = 0.0,
                outgoing_rate = line.unit_cost,
                voucher_type = "Stock Entry",
                voucher_id = stock_entry.document_number,
                voucher_line_id=f"{stock_entry.document_number}-L{line.id}"
            )
            create_stock_ledger_entry(db, reversal_ingoing)

    stock_entry.status = Status.CANCELED
    stock_entry.cancelled_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(stock_entry)
    return stock_entry

def update_stock_entry(db: Session, stock_id: int, update_stock_entry: StockEntryUpdate):
    stock_entry = repository.get_stock_entry_by_id(db, stock_id)
    if stock_entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Stock Entry ID is not found")
    if stock_entry.status != Status.DRAFT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Only draft Stock Entries can be updated")
    
    update_data = update_stock_entry.model_dump(exclude_unset=True)
    update_lines = "stock_entry_lines" in update_data
    new_lines = update_data.pop("stock_entry_lines", None)
    for key, value in update_data.items():
        setattr(stock_entry, key, value)
    purpose = stock_entry.purpose
    src_wh = stock_entry.source_warehouse_id
    tgt_wh = stock_entry.target_warehouse_id

    validate_warehouse_rules(purpose, src_wh, tgt_wh)

    if src_wh is None:
        warehouse = WarehouseRepository.get_warehouse_by_id(db, src_wh)
        if warehouse is None or warehouse.is_active == "False":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Warehouse ID is not found or inactive")
    if tgt_wh is None:
        warehouse = WarehouseRepository.get_warehouse_by_id(db, tgt_wh)
        if warehouse is None or warehouse.is_active == "False":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Warehouse ID is not found or inactive")

    prepared_lines = list[dict] = []
    if update_lines:
        if not new_lines:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Stock Entry must have at least one line")

        for new_line in new_lines:
            if isinstance(new_line, dict):
                item_id = new_line.get("item_id")
                line_src = new_line.get("source_warehouse_id")
                line_tgt = new_line.get("target_warehouse_id")
                quantity = new_line.get("quantity", 0)
                conversion_factor = new_line.get("conversion_factor", 1.0)
                unit_cost = new_line.get("unit_cost", 0.0)
                uom_id = new_line.get("uom_id")
                batch_id = new_line.get("batch_id")
                serial_id = new_line.get("serial_id")
            else:
                item_id = getattr(new_line, "item_id", None)
                line_src = getattr(new_line, "source_warehouse_id", None)
                line_tgt = getattr(new_line, "target_warehouse_id", None)
                quantity = getattr(new_line, "quantity", 0)
                conversion_factor = getattr(new_line, "conversion_factor", 1.0)
                unit_cost = getattr(new_line, "unit_cost", 0.0)
                uom_id = getattr(new_line, "uom_id", None)
                batch_id = getattr(new_line, "batch_id", None)
                serial_id = getattr(new_line, "serial_id", None)

            if item_id is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Item ID is required for each stock entry line")

            item = ItemRepository.get_item_by_id(db, item_id)
            if item is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Item ID is not found")

            src_wh = line_src if line_src is not None else src_wh
            tgt_wh = line_tgt if line_tgt is not None else tgt_wh
            check_item_and_warehouse_active_status(db, item_id, src_wh, tgt_wh)

            if quantity is None or quantity <= 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Quantity must be greater than Zero")

            if conversion_factor is None or conversion_factor <= 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Conversion factor must be greater than Zero")

            if unit_cost is None or unit_cost < 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Unit cost cannot be negative")

            if getattr(item, "is_batch_tracked", False) and not batch_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Batch ID is required")

            if batch_id:
                batch = TrackRepository.get_batch_number_by_id(db, batch_id)
                if batch is None:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Batch ID is not found")
                if batch.item_id != item_id:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Batch does not belong to the item")
                if batch.expiry_date:
                    current_date = datetime.now(timezone.utc).date()
                    batch_exp = (
                        batch.expiry_date.date()
                        if isinstance(batch.expiry_date, datetime)
                        else batch.expiry_date
                    )
                    if batch_exp < current_date:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Batch is already Expired")

            stock_quantity = quantity * conversion_factor
            line_amount = quantity * unit_cost

            if getattr(item, "is_serial_tracked", False) and not serial_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Serial ID is required for Item_id")

            if serial_id:
                if len(serial_id) != int(stock_quantity):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Mismatch, Stock quantity is different from the provided serial numbers")
                for s_id in serial_id:
                    serial = TrackRepository.get_serial_number_by_id(db, s_id)
                    if serial is None:
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Serial ID is not found")
                    if serial.item_id != item_id:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Serial ID does not belong to item",)

            prepared_lines.append(
                {
                    "stock_entry_id": stock_entry.id,
                    "item_id": item_id,
                    "source_warehouse_id": src_wh,
                    "target_warehouse_id": tgt_wh,
                    "quantity": quantity,
                    "uom_id": uom_id,
                    "conversion_factor": conversion_factor,
                    "stock_quantity": stock_quantity,
                    "unit_cost": unit_cost,
                    "line_amount": line_amount,
                    "batch_id": batch_id,
                    "serial_id": serial_id,
                }
            )

        stock_entry.stock_entry_lines.clear()
        db.flush()

        for line_payload in prepared_lines:
            stock_entry.stock_entry_lines.append(StockEntryLine(**line_payload))

    if hasattr(stock_entry, "updated_at"):
        stock_entry.updated_at = datetime.now(timezone.utc)

    return repository.update_stock_entry(db, stock_entry)

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

def get_stock_entries(db: Session):
    stock_entries = repository.get_stock_entries(db)
    if not stock_entries:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "No stock entries were found")
    return stock_entries

def get_stock_entry_by_id(db: Session, entry_id: int):
    stock_entry = repository.get_stock_entry_by_id(db, entry_id)
    if stock_entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Stock Entry ID is not found")
    return stock_entry