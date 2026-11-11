from sqlalchemy.orm import Session
from sqlalchemy import select
from app.inventory.tracking_items.models import SerialNumber, ItemBatch
from datetime import datetime, timezone

def get_batch_numbers(db: Session):
    statement = select(ItemBatch)
    return db.scalars(statement).all()

def get_serial_numbers(db: Session):
    statement = select(SerialNumber)
    return db.scalars(statement).all()

def get_batch_number_by_id(db: Session, batch_id: int):
    statement = select(ItemBatch).where(ItemBatch.id == batch_id)
    return db.scalar(statement)

def get_serial_number_by_id(db: Session, serial_id: int):
    statement = select(SerialNumber).where(SerialNumber.id == serial_id)
    return db.scalar(statement)

def get_batches_by_item_id(db: Session, item_id: int):
    statement = select(ItemBatch).where(ItemBatch.item_id == item_id)
    return db.scalars(statement).all()

def get_batch_by_batch_number(db: Session, batch_number: str):
    statement = select(ItemBatch).where(ItemBatch.batch_number == batch_number)
    return db.scalar(statement)

def get_serials_by_item_id(db: Session, item_id: int):
    statement = select(SerialNumber).where(SerialNumber.item_id == item_id)
    return db.scalars(statement).all()

def get_serial_by_serial_number(db: Session, serial_number: str):
    statement = select(SerialNumber).where(SerialNumber.serial_number == serial_number)
    return db.scalar(statement)

def get_serials_by_item_and_warehouse(db: Session, item_id: int, warehouse_id: int):
    statement = (
        select(SerialNumber)
        .where(
            SerialNumber.item_id == item_id,
            SerialNumber.current_warehouse_id == warehouse_id
        )
    )
    return db.scalars(statement).all()

def create_batch_number(db: Session, new_batch: ItemBatch):
    new_data = ItemBatch(**new_batch)
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return new_data

def update_batch_number(db: Session, update_batch: ItemBatch):
    db.commit()
    db.refresh(update_batch)
    return update_batch

def create_serial_number(db: Session, new_serial: SerialNumber):
    new_data = SerialNumber(**new_serial)
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return new_data

def update_serial_number(db: Session, update_serial: SerialNumber):
    db.commit()
    db.refresh(update_serial)
    return update_serial