from fastapi import APIRouter, Depends
from database.database import get_db
from app.systemadministration.uom import service
from app.systemadministration.uom.schemas import UomResponse, ConversionResponse, UnitConversionResponse, UomCreate, UomUpdate, UnitConversionCreate, UnitConversionUpdate
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()

@router.get("/uoms/", response_model= List[UomResponse], tags = ["UOMs"])
def get_uoms(db: Session = Depends(get_db)):
    return service.get_uoms(db)

@router.get("/uoms/{uom_id}/", response_model=UomResponse, tags = ["UOMs"])
def get_uom_by_id(uom_id: int, db: Session = Depends(get_db)):
    return service.get_uom_by_id(db, uom_id)

@router.post("/uoms/", response_model=UomResponse, tags = ["UOMs"])
def create_uom(new_uom: UomCreate, db: Session = Depends(get_db)):
    return service.create_uom(db, new_uom)

@router.patch("/uoms/{uom_id}/", response_model=UomResponse, tags = ["UOMs"])
def update_uom(uom_id: int, update_uom: UomUpdate, db: Session = Depends(get_db)):
    return service.update_uom(db, uom_id, update_uom)

@router.get("/uomconversions/", response_model= List[UnitConversionResponse], tags = ["UOMs Conversion"])
def get_unit_conversions(db: Session = Depends(get_db)):
    return service.get_unit_conversions(db)

@router.get("/uomconversions/{conversion_id}", response_model=UnitConversionResponse, tags = ["UOMs Conversion"])
def get_unit_conversion_by_id(conversion_id: int, db: Session = Depends(get_db)):
    return service.get_unit_conversion_by_id(db, conversion_id)

@router.post("/uomconversions/", response_model= UnitConversionResponse, tags = ["UOMs Conversion"])
def create_unit_conversion(new_conversion: UnitConversionCreate, db: Session = Depends(get_db)):
    return service.create_unit_conversion(db, new_conversion)

@router.patch("/uomconversions/{conversion_id}", response_model=UnitConversionResponse, tags = ["UOMs Conversion"])
def update_unit_conversion(conversion_id: int, update_conversion: UnitConversionUpdate, db: Session = Depends(get_db)):
    return service.update_unit_conversion(db, conversion_id, update_conversion)

@router.post("/uomconversions/{conversion_id}/{amount}/", response_model = ConversionResponse, tags = ["UOMs Conversion"])
def uom_conversion(conversion_id: int, amount: int, db: Session = Depends(get_db)):
    return service.uom_conversion(db, conversion_id, amount)