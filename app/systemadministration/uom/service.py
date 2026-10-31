from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.systemadministration.uom import repository
from app.systemadministration.uom.schemas import UomCreate, UnitConversionCreate, UomUpdate, UnitConversionUpdate
from datetime import datetime, timezone

def get_uoms(db: Session):
    uoms = repository.get_uoms(db)
    if not uoms:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "No UOMs were found")
    return uoms

def get_uom_by_id(db: Session, uom_id: int):
    uom = repository.get_uom_by_id(db, uom_id)
    if uom is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "No UOM with ID is found")
    return uom

def create_uom(db: Session, new_uom: UomCreate):
    existing_uom = repository.get_uom_by_code(db, new_uom.code)
    if existing_uom is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "UOM already exists")

    db_data = new_uom.model_dump(exclude_unset=True)
    return repository.create_uom(db, db_data)

def update_uom(db: Session, uom_id: int, update_uom: UomUpdate):
    uom = repository.get_uom_by_id(db, uom_id)
    if uom is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "UOM with ID is not found")

    db_data = update_uom.model_dump(exclude_unset=True)
    for key,value in db_data.items():
        setattr(uom, key, value)
    uom.updated_at = datetime.now(timezone.utc)

    return repository.update_uom(db, uom)

def get_unit_conversions(db: Session):
    uomc = repository.get_unit_conversions(db)
    if not uomc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "No Unit Conversion is found")
    return uomc

def get_unit_conversion_by_id(db: Session, uom_id: int):
    uom = repository.get_unit_conversion_by_id(db, uom_id)
    if uom is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Unit Conversion with ID is not found")
    return uom

def create_unit_conversion(db: Session, new_uomc: UnitConversionCreate):
    db_data = new_uomc.model_dump(exclude_unset=True)
    return repository.create_unit_conversion(db, db_data)

def update_unit_conversion(db: Session, uom_id: int, update_uomc: UnitConversionUpdate):
    uom = repository.get_unit_conversion_by_id(db, uom_id)
    if uom is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "No UOM with ID is found")

    db_data = update_uomc.model_dump(exclude_unset=True)
    for key, value in db_data.items():
        setattr(uom, key, value)
    uom.updated_at = datetime.now(timezone.utc)

    return repository.update_uom(db, uom)

def uom_conversion(db: Session, conversion_id: int, amount: int):
    conversion = repository.get_unit_conversion_by_id(db, conversion_id)
    if conversion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Unit Conversion is not found")
    if not conversion.from_unit.is_active or not conversion.to_unit.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Unit conversion is disabled")

    result = amount * conversion.factor
    decimal_places = 0 if conversion.to_unit.must_be_whole_number else 4

    return {
        "from_uom": conversion.from_unit.code,
        "to_uom": conversion.to_unit.code,
        "result": round(result, decimal_places),
        "unit_conversion": conversion.factor,
        "converted_unit": round(result, decimal_places)
    }