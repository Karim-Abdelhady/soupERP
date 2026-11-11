from database.database import get_db
from fastapi import Depends, APIRouter
from app.inventory.tracking_items import service
from app.inventory.tracking_items.schemas import SerialNumberResponse, BatchResponse, BatchSerialResponse, BatchCreate, SerialNumberCreate, BatchUpdate, SerialNumberUpdate
from typing import List
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/batches/", response_model=List[BatchResponse], tags = ["Batch Numbers"])
def get_batch_numbers(db: Session = Depends(get_db)):
    return service.get_batch_numbers(db)

@router.get("/serialnumbers/", response_model=List[SerialNumberResponse], tags = ["Serial Numbers"])
def get_serial_numbers(db: Session = Depends(get_db)):
    return service.get_serial_numbers(db)

@router.get("/batches/{batch_id}/serialnumbers/", response_model=BatchSerialResponse, tags = ["Batch/Serial Numbers"])
def get_batch_and_serials(batch_id: int, db: Session = Depends(get_db)):
    return service.get_batch_number_by_id(db, batch_id)

@router.get("/batches/{batch_id}", response_model=BatchResponse, tags = ["Batch Numbers"])
def get_batch_number_by_id(batch_id: int, db: Session = Depends(get_db)):
    return service.get_batch_number_by_id(db, batch_id)

@router.get("/serials/{serial_id}", response_model = SerialNumberResponse, tags = ["Serial Numbers"])
def get_serial_number_by_id(serial_id: int, db: Session = Depends(get_db)):
    return service.get_serial_number_by_id(db, serial_id)

@router.get("/batches/items/{item_id}", response_model=List[BatchResponse], tags = ["Batch Numbers"])
def get_batches_by_item_id(item_id: int, db: Session = Depends(get_db)):
    return service.get_batches_by_item_id(db, item_id)

@router.get("/serials/items/{item_id}", response_model=List[SerialNumberResponse], tags = ["Serial Numbers"])
def get_serials_by_item_id(item_id: int, db: Session = Depends(get_db)):
    return service.get_serials_by_item_id(db, item_id)

@router.post("/batches/", response_model=BatchResponse, tags = ["Batch Numbers"])
def create_batch_number(new_batch: BatchCreate, db: Session = Depends(get_db)):
    return service.create_batch_number(db, new_batch)

@router.patch("/batches/{batch_id}", response_model = BatchResponse, tags = ["Batch Numbers"])
def update_batch_number(batch_id: int, update_batch: BatchUpdate, db: Session = Depends(get_db)):
    return service.update_batch_number(db, batch_id, update_batch)

@router.post("/serials/", response_model = SerialNumberResponse, tags = ["Serial Numbers"])
def create_serial_number(new_serial: SerialNumberCreate, db: Session = Depends(get_db)):
    return service.create_serial_number(db, new_serial)

@router.patch("/serials/{serial_id}", response_model = SerialNumberResponse, tags = ["Serial Numbers"])
def update_serial_number(serial_id: int, update_serial: SerialNumberUpdate, db: Session = Depends(get_db)):
    return service.update_serial_number(db, serial_id, update_serial) 