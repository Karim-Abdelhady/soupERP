from app.inventory.tracking_items import repository
from sqlalchemy.orm import Session
from app.inventory.tracking_items.enums import SerialStatus, BatchStatus
from app.inventory.tracking_items.schemas import BatchCreate, SerialNumberCreate, BatchUpdate, SerialNumberUpdate
from fastapi import HTTPException, status
from app.inventory.items.models import Item
from app.inventory.items import repository as ItemRepository
from datetime import datetime, timezone
from app.inventory.stock.stock_balance import repository as SBrepository
from sqlalchemy import select
from app.inventory.stock.stock_balance.models import StockBalance
from app.inventory.stock.stock_ledger.models import StockLedger
from decimal import Decimal
from app.inventory.tracking_items.models import SerialNumber, stock_ledger_serial_map

def get_batch_numbers(db: Session):
    batches = repository.get_batch_numbers(db)
    if not batches:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "No batch numbers were found")
    return batches

def get_serial_numbers(db: Session):
    serials = repository.get_serial_numbers(db)
    if not serials:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "No serial numbers were found")
    return serials

def get_batch_number_by_id(db: Session, batch_id: int):
    batch = repository.get_batch_number_by_id(db, batch_id)
    if batch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Batch number ID is not found")
    return batch

def get_serial_number_by_id(db: Session, serial_id: int):
    serial = repository.get_serial_number_by_id(db, serial_id)
    if serial is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Serial number ID is not found")
    return serial

def get_batches_by_item_id(db: Session, item_id: int):
    batches = repository.get_batches_by_item_id(db, item_id)
    if not batches:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Item ID is not associated with Batch Number")
    return batches

def get_serials_by_item_id(db: Session, item_id: int):
    serials = repository.get_serials_by_item_id(db, item_id)
    if not serials:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Item ID is nto associated with Serial Number")
    return serials

def create_batch_number(db: Session, new_batch: BatchCreate):
    existing_batch = repository.get_batch_by_batch_number(db, new_batch.batch_number)
    if existing_batch is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Batch number already exists")

    item = ItemRepository.get_item_by_id(db, new_batch.item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Item ID is not found")

    if not Item.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Item ID is not active")

    if not Item.is_batch_tracked:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Item ID must have is_batch_tracked enabled")

    if not Item.has_expiry_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Item ID must have has_expiry_Date enabled")

    new_data = new_batch.model_dump(exclude_unset=True)
    new_data["status"] = BatchStatus.ACTIVE
    new_data["item_id"] = new_batch.item_id

    return repository.create_batch_number(db, new_data)

def update_batch_number(db: Session, batch_id: int, update_batch: BatchUpdate):
    batch = repository.get_batch_number_by_id(db, batch_id)
    if batch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Batch ID is not found")
    if batch.status in [BatchStatus.EXPIRED, BatchStatus.QUARANTINED]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Batch is Expired or Quarantineed")

    update_data = update_batch.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(batch, key, value)
    return repository.update_batch_number(db, batch)

def issue_batch_inventory(db: Session, item_id: int, warehouse_id: str, batch_id: str, qty_delta: float, voucher_type: str, voucher_id: str, voucher_line_id: int):
    batch = repository.get_batch_number_by_id(db, batch_id)
    if not batch:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail = "Batch number ID is not found")

    if not batch or batch.status in [BatchStatus.EXPIRED, BatchStatus.QUARANTINED]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Batch is Expired or Quarantined")

    balance = db.query(StockBalance).filter_by(
        item_id=item_id, 
        warehouse_id=warehouse_id,
        batch_id=batch_id
    ).first()

    if not balance or balance.actual_qty < abs(qty_delta):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Insufficient Stock in Batch")

    current_batch_rate = balance.valuation_rate
    balance.actual_qty = balance.actual_qty + qty_delta
    balance.stock_value = balance.actual_qty * current_batch_rate

    batch.status = BatchStatus.ISSUED

    ledger_entry = StockLedger(
        posting_date = datetime.now(timezone.utc),
        item_id = item_id,
        warehouse_id = warehouse_id,
        batch_id = batch_id,
        quantity_delta = qty_delta,
        qty_after_transaction=balance.actual_qty,
        incoming_rate = 0.00,
        outgoing_rate = current_batch_rate,
        stock_value_delta = qty_delta * current_batch_rate,
        stock_value_after_transaction=balance.stock_value,
        voucher_type = voucher_type,
        voucher_id = voucher_id,
        voucher_line_id = voucher_line_id
    )
    db.add(ledger_entry)
    return balance.actual_qty

def create_serial_number(db: Session, new_serial: SerialNumberCreate):
    existing_serial_number = repository.get_serial_by_serial_number(db, new_serial.serial_number)
    if existing_serial_number is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Serial Number already exists")
    item = ItemRepository.get_item_by_id(db, new_serial.item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Item is not found")
    if not item.is_serial_tracked:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail ="Item must have is_serial_tracked enabled")

    new_data = new_serial.model_dump(exclude_unset=True)
    new_data["status"] = SerialStatus.INSTOCK
    new_data["item_id"] = new_serial.item_id

    return repository.create_serial_number(db, new_data)

def update_serial_number(db: Session, serial_id: int, update_serial: SerialNumberUpdate):
    serial_number = repository.get_serial_number_by_id(db, serial_id)
    if serial_number is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Serial Number ID is not found")
    if serial_number.status == SerialStatus.ISSUED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Serial Number is already issued")

    update_data = update_serial.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(serial_number, key, value)
    return repository.update_serial_number(db, serial_number)

def issue_serial_number(db: Session, item_id: int, warehouse_id: int, serial_strings: list[str], voucher_type: str, voucher_id: str, voucher_line_id: int):
    total_qty_to_issue = Decimal(len(serial_strings))
    serials = db.query(SerialNumber).filter(
        SerialNumber.item_id == item_id,
        SerialNumber.serial_number.in_(serial_strings)
    ).all()
    if len(serials) != len(serial_strings):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "One or more serial numbers do not exist")

    for serial in serials:
        if serial.status != SerialStatus.INSTOCK or serial.current_warehouse_id != warehouse_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Serial Number is not available in warehouse")

    balance = SBrepository.get_stock_balance_by_item_and_warehouse(db, item_id, warehouse_id)
    if not balance or balance.actual_qty < total_qty_to_issue:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Insufficient Stock")

    current_valuation_rate = balance.valuation_rate
    qty_delta = -total_qty_to_issue
    balance.actual_qty = balance.actual_qty + qty_delta
    balance.stock_value = balance.actual_qty * current_valuation_rate

    ledger_entry = StockLedger(
        posting_date=datetime.now(timezone.utc),
        item_id=item_id,
        warehouse_id=warehouse_id,
        quantity_delta=qty_delta,
        qty_after_transaction=balance.actual_qty,
        incoming_rate = 0.0,
        outgoing_rate=current_valuation_rate,
        stock_value_delta=qty_delta * current_valuation_rate,
        stock_value_after_transaction=balance.stock_value,
        voucher_type=voucher_type,
        voucher_id = voucher_id,
        voucher_line_id = voucher_line_id
    )
    db.add(ledger_entry)
    db.flush()
    for serial in serials:
        serial.status = SerialStatus.ISSUED
        serial.current_warehouse_id = None

        db.execute(stock_ledger_serial_map.insert().values(
            stock_ledger_id = ledger_entry.id,
            serial_number_id = serial.id
        ))

    return balance.actual_qty

    
