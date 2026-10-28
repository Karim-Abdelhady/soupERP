from sqlalchemy.orm import Session
from sqlalchemy import select
from app.uom.models import UnitOfMeasure, UnitConversion

def get_uoms(db: Session):
    statement = select(UnitOfMeasure)
    return db.scalars(statement).all()

def get_uom_by_id(db: Session, uom_id: int):
    statement = select(UnitOfMeasure).where(UnitOfMeasure.id == uom_id)
    return db.scalar(statement)

def get_uom_by_code(db: Session, code: str):
    statement = select(UnitOfMeasure).where(UnitOfMeasure.code == code)
    return db.scalar(statement)

def create_uom(db: Session, uom: UnitOfMeasure):
    db_data = UnitOfMeasure(**uom)
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

def update_uom(db: Session, uom: UnitOfMeasure):
    db.commit()
    db.refresh(uom)
    return uom

def get_unit_conversions(db: Session):
    statement = select(UnitConversion)
    return db.scalars(statement).all()

def get_unit_conversion_by_id(db: Session, uom_id: int):
    statement = select(UnitConversion).where(UnitConversion.id == uom_id)
    return db.scalar(statement)

def create_unit_conversion(db: Session, new_conversion: UnitConversion):
    db_data = UnitConversion(**new_conversion)
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

def update_unit_conversion(db: Session, update_conversion: UnitConversion):
    db.commit()
    db.refresh(update_conversion)
    return update_conversion
