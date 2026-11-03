from sqlalchemy.orm import Session
from sqlalchemy import select
from app.inventory.stock.stock_ledger.models import StockLedger

def create_stock_ledger(db: Session, ledger: StockLedger):
    new_data = StockLedger(**ledger)
    db.add(new_data)
    db.flush()
    return new_data

def get_stock_ledgers(db: Session):
    statement = select(StockLedger)
    return db.scalars(statement).all()

def get_stock_ledger_by_id(db: Session, ledger_id: int):
    statement= select(StockLedger).where(StockLedger.id == ledger_id)
    return db.scalar(statement)

def get_stock_ledger_item_history(db: Session, item_id: int):
    statement = select(StockLedger).where(StockLedger.item_id == item_id)
    return db.scalars(statement).all()

def get_stock_ledger_warehouse_history(db: Session, warehouse_id: int):
    statement = select(StockLedger).where(StockLedger.warehouse_id == warehouse_id)
    return db.scalars(statement).all()