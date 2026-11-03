from sqlalchemy.orm import Session
from sqlalchemy import select
from app.inventory.stock.stock_balance.models import StockBalance


def get_stock_balances(db: Session):
    statement = select(StockBalance)
    return db.scalars(statement).all()

def get_stock_balance_by_id(db: Session, balance_id: int):
    statement = select(StockBalance).where(StockBalance.id == balance_id)
    return db.scalar(statement)

def get_stock_balance_item_history(db: Session, item_id: int):
    statement = select(StockBalance).where(StockBalance.item_id == item_id)
    return db.scalars(statement).all()

def get_stock_balance_warehouse_history(db: Session, warehouse_id: int):
    statement = select(StockBalance).where(StockBalance.warehouse_id == warehouse_id)
    return db.scalars(statement).all()

def get_stock_balance_by_item_and_warehouse(db: Session, item_id: int, warehouse_id: int):
    statement = (
        select(StockBalance)
        .where(
            StockBalance.item_id == item_id,
            StockBalance.warehouse_id == warehouse_id
        )
    )
    return db.scalar(statement)