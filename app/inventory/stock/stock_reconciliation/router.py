from fastapi import APIRouter, Depends
from app.inventory.stock.stock_reconciliation import service
from app.inventory.stock.stock_reconciliation.schemas import StockReconciliationCreate, StockReconciliationResponse, StockReconciliationUpdate
from database.database import get_db
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()

@router.post("/stockreconciliations/draft/", response_model=StockReconciliationResponse, tags = ["Stock Reconciliation"])
def create_stock_reconciliation(new_stock_reconciliation: StockReconciliationCreate, db: Session = Depends(get_db)):
    return service.create_stock_reconciliation(db, new_stock_reconciliation)

@router.post("/stockreconciliations/{rec_id}/submit/", response_model=StockReconciliationResponse, tags = ["Stock Reconciliation"])
def submit_stock_reconciliation(rec_id: int, db: Session = Depends(get_db)):
    return service.submit_stock_reconciliation(db, rec_id)

@router.post("/stockreconcilations/{rec_id}/cancel/", response_model = StockReconciliationResponse, tags = ["Stock Reconciliation"])
def cancel_stock_reconciliation(rec_id: int, db: Session = Depends(get_db)):
    return service.cancel_stock_reconciliation(db, rec_id)

@router.patch("/stockreconciliations/{rec_id}/draft/", response_model = StockReconciliationResponse, tags = ["Stock Reconciliation"])
def update_stock_reconcilation(rec_id: int, update_stock_reconciliation: StockReconciliationUpdate, db: Session = Depends(get_db)):
    return service.update_stock_reconciliation(db, rec_id, update_stock_reconciliation)

@router.get("/stockreconciliations/",response_model=List[StockReconciliationResponse], tags = ["Stock Reconciliation"])
def get_stock_reconciliations(db: Session = Depends(get_db)):
    return service.get_stock_reconciliations(db)

@router.get("/stockreconciliations/{rec_id}/", response_model=StockReconciliationResponse, tags = ["Stock Reconciliation"])
def get_stock_reconciliation_by_id(rec_id: int, db: Session = Depends(get_db)):
    return service.get_stock_reconciliation_by_id(db, rec_id)

@router.get("/stockreconciliations/item/{item_id}", response_model= List[StockReconciliationResponse], tags = ["Stock Reconciliation"])
def get_stock_reconciliation_by_item_id(item_id: int, db: Session = Depends(get_db)):
    return service.get_stock_reconciliation_by_item_id(db, item_id)

@router.get("/stockreconciliations/warehouse/{warehouse_id}", response_model= List[StockReconciliationResponse], tags = ["Stock Reconciliation"])
def get_stock_reconciliation_by_warehouse_id(warehouse_id: int, db: Session = Depends(get_db)):
    return service.get_stock_reconciliation_by_warehouse_id(db, warehouse_id)

@router.get("/stockreconcilations/item/{item_id}/warehouse/{warehouse_id}", response_model= List[StockReconciliationResponse], tags = ["Stock Reconciliation"])
def get_stock_reconciliation_by_item_and_warehouse(item_id: int, warehouse_id: int, db: Session = Depends(get_db)):
    return service.get_stock_reconciliation_by_item_and_warehouse(db, warehouse_id, item_id)