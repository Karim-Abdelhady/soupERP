from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.inventory.stock.stock_balance.schemas import StockBalanceResponse
from database.database import get_db
from typing import List
from app.inventory.stock.stock_balance import service

router = APIRouter()

@router.get("/stockbalances", response_model=List[StockBalanceResponse], tags = ["Stock Balance"])
def get_stock_balances(db: Session = Depends(get_db)):
    return service.get_stock_balances(db)

@router.get("/stockbalances/item/{item_id}", response_model=List[StockBalanceResponse], tags = ["Stock Balance"])
def get_stock_balance_item_history(item_id: int, db: Session = Depends(get_db)):
    return service.get_stock_balance_item_history(db, item_id)

@router.get("/stockbalances/warehouse/{warehouse_id}", response_model=List[StockBalanceResponse], tags = ["Stock Balance"])
def get_stock_balance_warehouse_history(warehouse_id: int, db: Session = Depends(get_db)):
    return service.get_stock_balance_warehouse_history(db, warehouse_id)

@router.get("/stockbalances/{balance_id}/", response_model=StockBalanceResponse, tags = ["Stock Balance"])
def get_stock_balance_by_id(balance_id: int, db: Session = Depends(get_db)):
    return service.get_stock_balance_by_id(db, balance_id)