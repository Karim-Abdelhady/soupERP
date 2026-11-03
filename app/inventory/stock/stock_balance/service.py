from sqlalchemy.orm import Session
from app.inventory.stock.stock_balance import repository
from fastapi import HTTPException, status


def get_stock_balances(db: Session):
    stock_balances = repository.get_stock_balances(db)
    if not stock_balances:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "No stock balances were found")
    return stock_balances

def get_stock_balance_by_id(db: Session, balance_id: int):
    stock_balance = repository.get_stock_balance_by_id(db, balance_id)
    if stock_balance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Stock balance with ID is not found")
    return stock_balance

def get_stock_balance_item_history(db: Session, item_id: int):
    stock_item_balance = repository.get_stock_balance_item_history(db, item_id)
    if stock_item_balance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Item ID is not found")
    return stock_item_balance

def get_stock_balance_warehouse_history(db: Session, warehouse_id: int):
    stock_warehouse_balance = repository.get_stock_balance_warehouse_history(db, warehouse_id)
    if stock_warehouse_balance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Warehouse ID is not found")
    return stock_warehouse_balance