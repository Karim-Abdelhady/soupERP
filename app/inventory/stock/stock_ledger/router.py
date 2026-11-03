from fastapi import APIRouter, Depends
from app.inventory.stock.stock_ledger.schemas import StockLedgerResponse
from app.inventory.stock.stock_ledger import service
from typing import List
from sqlalchemy.orm import Session
from database.database import get_db
from app.inventory.stock.stock_ledger.schemas import StockLedgerCreate

router = APIRouter()

@router.post("/stockledgers/", response_model=StockLedgerResponse, tags = ["Stock Ledger"])
def create_stock_ledger_entry(data: StockLedgerCreate, db: Session = Depends(get_db)):
    return service.create_stock_ledger_entry(db, data)  

@router.get("/stockledgers/", response_model=List[StockLedgerResponse], tags = ["Stock Ledger"])
def get_stock_ledgers(db: Session = Depends(get_db)):
    return service.get_stock_ledgers(db)

@router.get("/stockledgers/items/{item_id}/", response_model=List[StockLedgerResponse], tags = ["Stock Ledger"])
def get_stock_ledger_item_history(item_id: int, db: Session = Depends(get_db)):
    return service.get_stock_ledger_item_history(db, item_id)

@router.get("/stockledgers/warehouses/{warehouse_id}/", response_model=List[StockLedgerResponse], tags = ["Stock Ledger"])
def get_stock_ledger_warehouse_history(warehouse_id: int, db: Session = Depends(get_db)):
    return service.get_stock_ledger_warehouse_history(db, warehouse_id)

@router.get("/stockledgers/{ledger_id}/", response_model=StockLedgerResponse, tags = ["Stock Ledger"])
def get_stock_ledger_by_id(ledger_id: int, db: Session = Depends(get_db)):
    return service.get_stock_ledger_by_id(db, ledger_id)