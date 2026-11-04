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

def validate_warehouse_rules(purpose: Purpose, source_wh_int: int | None, target_wh_int: int | None):
    if purpose == Purpose.TRANSFER:
        if not source_wh_int or not target_wh_int:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Source and Target warehouse are required")
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
    existing_stock_entry = repository.get_draft_stock_entry(db, new_stock.document_number)
    if existing_stock_entry is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail = "Stock Entry already exists.")

    validate_warehouse_rules(new_stock.purpose, new_stock.source_warehouse_id, new_stock.target_warehouse_id)
    
    new_data = new_stock.model_dump(exclude_unset=True)
    lines_data = new_data.pop("lines", [])
    StockEntry.status = Status.DRAFT
    db_stock_entry = StockEntry(**new_data)
    db.add(db_stock_entry)
    db.flush()

    for line in lines_data:
        quantity = line.get("quantity", 0)
        conversion_factor = line.get("conversion_factor", 1.0)
        unit_cost = line.get("unit_cost", 0.0)

        line["stock_quantity"] = quantity * conversion_factor
        line["line_amount"] = quantity * unit_cost
        db_line = StockEntryLine(stock_entry_id=db_stock_entry.id, **line)
        db.add(db_line)

    return repository.create_stock_entry(db, db_stock_entry)

def submit_stock_entry(db: Session, stock_id: int):
    stock_entry = repository.get_stock_entry_by_id(db, stock_id)
    if stock_entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Stock Entry ID is not found")

    if stock_entry.status == Status.SUBMITTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Stock Entry is already submitted")

    if not stock_entry.stock_entry_lines:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Cannot submit a Stock Entry without a line")

    for line in stock_entry.stock_entry_lines:
        src_wh = line.source_warehouse_id or stock_entry.source_warehouse_id
        tgt_wh = line.target_warehouse_id or stock_entry.target_warehouse_id

        if src_wh:
            outgoing = StockLedgerCreate(
                stock_entry_id = line.stock_entry_id,
                item_id=line.item_id,
                warehouse_id=src_wh,
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

    if stock_entry.status == Status.CANCELED:
        for line in stock_entry.stock_entry_lines:
            src_wh = line.source_warehouse_id or stock_entry.source_warehouse_id
            tgt_wh = line.target_warehouse_id or stock_entry.target_warehouse_id

            if src_wh:
                reversal_outgoing = StockLedgerCreate(
                    stock_entry_id = line.stock_entry_id,
                    item_id=line.item_id,
                    warehouse_id=src_wh,
                    quantity_delta=line.stock_quantity,
                    incoming_rate=line.unit_Cost,
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
    
    update_data = update_stock_entry.model_dump(exclude_unset=True)
    if stock_entry.status == Status.DRAFT:
        for key, value in update_data.items():
            setattr(stock_entry, key, value)
    return repository.update_stock_entry(db, stock_entry)

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