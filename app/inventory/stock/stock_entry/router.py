from fastapi import APIRouter, Depends
from app.inventory.stock.stock_entry.schemas import StockEntryResponse, StockEntryCreate, StockEntryUpdate
from app.inventory.stock.stock_entry import service
from sqlalchemy.orm import Session
from database.database import get_db
from typing import List

router = APIRouter()

@router.post("/stockentries/draft", response_model=StockEntryResponse, tags = ["Stock Entry"])
def create_stock_entry(entry: StockEntryCreate, db: Session = Depends(get_db)):
    return service.create_stock_entry(db, entry)

@router.post("/stockentries/{entry_id}/submit/", response_model=StockEntryResponse, tags = ["Stock Entry"])
def submit_stock_entry(entry_id: int, db: Session = Depends(get_db)):
    return service.submit_stock_entry(db, entry_id)

@router.post("/stockentries/{entry_id}/cancel/", response_model = StockEntryResponse, tags = ["Stock Entry"])
def cancel_stock_entry(entry_id: int, db: Session = Depends(get_db)):
    return service.cancel_stock_entry(db, entry_id)

@router.patch("/stockentries/{entry_id}/draft/", response_model=StockEntryResponse, tags = ["Stock Entry"])
def update_stock_entry(entry_id: int, update_entry: StockEntryUpdate, db: Session = Depends(get_db)):
    return service.update_stock_entry(db, entry_id, update_entry)

@router.get("/stockentries/", response_model=List[StockEntryResponse], tags = ["Stock Entry"])
def get_stock_entries(db: Session = Depends(get_db)):
    return service.get_stock_entries(db)

@router.get("/stockentries/{entry_id}", response_model=StockEntryResponse, tags = ["Stock Entry"])
def get_stock_entry_by_id(entry_id: int, db: Session = Depends(get_db)):
    return service.get_stock_entry_by_id(db, entry_id)