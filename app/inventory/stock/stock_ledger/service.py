from sqlalchemy.orm import Session
from app.inventory.stock.stock_ledger import repository
from app.inventory.stock.stock_balance.models import StockBalance
from app.inventory.stock.stock_balance import repository as SBrepository
from app.inventory.stock.stock_ledger.schemas import StockLedgerCreate
from fastapi import HTTPException,status

def create_stock_ledger_entry(db: Session, data: StockLedgerCreate):
    balance = SBrepository.get_stock_balance_by_item_and_warehouse(db, data.item_id, data.warehouse_id)
    if not balance:
        balance = StockBalance(
            item_id = data.item_id,
            warehouse_id = data.warehouse_id,
            actual_qty = 0,
            reserved_qty = 0,
            available_qty = 0,
            valuation_rate = 0.0,
            stock_value = 0.0
        )
        db.add(balance)
        db.flush()

    new_actual_qty = balance.actual_qty + data.quantity_delta
    if new_actual_qty < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Insufficient stock")
    if data.quantity_delta > 0: #ingoing
        rate = data.incoming_rate
        total_current_value = balance.actual_qty + balance.valuation_rate
        incoming_value = data.quantity_delta * rate
        new_valuation_rate = ((total_current_value+incoming_value) / new_actual_qty if new_actual_qty > 0 else rate)
    else: #outgoing
        rate = balance.valuation_rate if balance.valuation_rate > 0 else data.outgoing_rate
        new_valuation_rate = balance.valuation_rate
    stock_value_delta = data.quantity_delta * rate
    new_stock_value = balance.stock_value + stock_value_delta
    new_available_qty = new_actual_qty - balance.reserved_qty

    ledger_data = {
        "item_id": data.item_id,
        "warehouse_id": data.warehouse_id,
        "quantity_delta": data.quantity_delta,
        "qty_after_transaction": new_actual_qty,
        "incoming_rate": data.incoming_rate if data.quantity_delta > 0 else 0.0,
        "outgoing_rate": rate if data.quantity_delta < 0 else 0.0,
        "stock_value_delta": stock_value_delta,
        "stock_value_after_transaction": new_stock_value,
        "voucher_type": data.voucher_type,
        "voucher_id": data.voucher_id,
        "voucher_line_id": data.voucher_line_id,
    }
    ledger_entry = repository.create_stock_ledger(db, ledger_data)

    balance.actual_qty = new_actual_qty
    balance.available_qty = new_available_qty
    balance.valuation_rate = new_valuation_rate
    balance.stock_value = new_stock_value

    db.commit()
    db.refresh(ledger_entry)
    db.refresh(balance)

    return ledger_entry

def get_stock_ledgers(db: Session):
    ledgers = repository.get_stock_ledgers(db)
    if not ledgers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "No stock ledgers were found")
    return ledgers

def get_stock_ledger_by_id(db: Session, ledger_id: int):
    ledger = repository.get_stock_ledger_by_id(db, ledger_id)
    if ledger is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Stock Ledger ID is not found")
    return ledger

def get_stock_ledger_item_history(db: Session, item_id: int):
    ledgers = repository.get_stock_ledger_item_history(db, item_id)
    if not ledgers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "No Stock Ledgers were found for this Item ID")
    return ledgers

def get_stock_ledger_warehouse_history(db: Session, warehouse_id: int):
    ledgers = repository.get_stock_ledger_warehouse_history(db, warehouse_id)
    if not ledgers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "No Stock Ledgers were found for this Warehouse ID")
    return ledgers