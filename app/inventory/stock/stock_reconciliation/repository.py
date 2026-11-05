from sqlalchemy.orm import Session
from sqlalchemy import select
from app.inventory.stock.stock_reconciliation.models import StockReconciliation, StockReconciliationLine
from app.inventory.stock.stock_reconciliation.enums import Status

def get_stock_reconciliations(db: Session):
    statement = select(StockReconciliation)
    return db.scalars(statement).all()

def get_draft_stock_reconciliation(db: Session, document_number: str):
    statement = (
        select(StockReconciliation)
        .where(
            StockReconciliation.document_number == document_number,
            StockReconciliation.status == Status.DRAFT
        )
    )
    return db.scalar(statement)

def get_stock_reconciliation_by_id(db: Session, rec_id: int):
    statement = select(StockReconciliation).where(StockReconciliation.id == rec_id)
    return db.scalar(statement)

def get_stock_reconciliation_by_item_and_warehouse(db: Session, warehouse_id:int, item_id: int):
    statement = (
        select(StockReconciliation)
        .join(StockReconciliation.stock_reconciliation_lines)
        .where(
            StockReconciliation.warehouse_id == warehouse_id,
            StockReconciliationLine.item_id == item_id
        )
        .distinct()
    )
    return db.scalars(statement).all()

def get_stock_reconciliation_by_item_id(db: Session, item_id: int):
    statement = (
        select(StockReconciliation)
        .join(StockReconciliation.stock_reconciliation_lines)
        .where(StockReconciliationLine.item_id == item_id)
        .distinct()
    )
    return db.scalars(statement).all()

def get_stock_reconciliation_by_warehouse_id(db: Session, warehouse_id: int):
    statement = select(StockReconciliation).where(StockReconciliation.warehouse_id == warehouse_id)
    return db.scalars(statement).all()

def create_stock_reconciliation(db: Session, reconciliation: StockReconciliation):
    db.add(reconciliation)
    db.commit()
    db.refresh(reconciliation)
    return reconciliation

def update_stock_reconciliation(db: Session, reconciliation: StockReconciliation):
    db.commit()
    db.refresh(reconciliation)
    return reconciliation