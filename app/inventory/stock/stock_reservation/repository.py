from sqlalchemy.orm import Session
from sqlalchemy import select
from app.inventory.stock.stock_reservation.models import StockReservation

def get_stock_reservations(db: Session):
    statement = select(StockReservation)
    return db.scalars(statement).all()

def get_stock_reservation_by_id(db: Session, reservation_id: int):
    statement = select(StockReservation).where(StockReservation.id == reservation_id)
    return db.scalar(statement)

def get_stock_reservation_by_document_and_line_id(db: Session, document_id: str, line_id: int):
    statement = (
        select(StockReservation)
        .where(
            StockReservation.source_document_id == document_id,
            StockReservation.source_line_id == line_id
        )
    )
    return db.scalar(statement)

def get_stock_reservations_by_item_id(db: Session, item_id: int):
    statement = select(StockReservation).where(StockReservation.item_id == item_id)
    return db.scalars(statement).all()

def get_stock_reservations_by_warehouse_id(db: Session, warehouse_id: int):
    statement = select(StockReservation).where(StockReservation.warehouse_id == warehouse_id)
    return db.scalars(statement).all()

def get_stock_reservations_by_item_and_warehouse(db: Session, item_id: int, warehouse_id: int):
    statement = (
        select(StockReservation)
        .where(
            StockReservation.item_id == item_id,
            StockReservation.warehouse_id == warehouse_id
        )
    )
    return db.scalars(statement).all()

def get_reserved_qty(db: Session, item_id: int, quantity: int):
    statement = (
        select(StockReservation)
        .where(
            StockReservation.item_id == item_id,
            StockReservation.quantity == quantity
        )
    )
    return db.scalar(statement)

def create_stock_reservation(db: Session, new_reservation: StockReservation):
    new_data = StockReservation(**new_reservation)
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return new_data