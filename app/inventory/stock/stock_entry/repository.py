from sqlalchemy.orm import Session
from sqlalchemy import select
from app.inventory.stock.stock_entry.models import StockEntry, StockEntryLine
from app.inventory.stock.stock_entry.enums import Status

def get_stock_entries(db: Session):
    statement = select(StockEntry)
    return db.scalars(statement).all()

def get_draft_stock_entry(db: Session, document_number: str):
    statement = (
        select(StockEntry)
        .where(
            StockEntry.document_number == document_number,
            StockEntry.status == Status.DRAFT
        )
    )
    return db.scalar(statement)

def get_stock_entry_by_id(db: Session, entry_id: int):
    statement = select(StockEntry).where(StockEntry.id == entry_id)
    return db.scalar(statement)

def get_stock_entry_by_document_number(db: Session, document_number: str):
    statement = select(StockEntry).where(StockEntry.document_number == document_number)
    return db.scalar(statement)

def create_stock_entry(db: Session, entry: StockEntry):
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def update_stock_entry(db: Session, entry: StockEntry):
    db.commit()
    db.refresh(entry)
    return entry