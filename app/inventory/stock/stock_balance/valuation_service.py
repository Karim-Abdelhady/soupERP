from app.inventory.stock.stock_balance.models import StockBalance
from app.inventory.stock.stock_balance import repository as SBrepository
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

def moving_weight_average(current_qty: float, current_rate: float, incoming_qty: float, incoming_rate: float):

    current_stock_value = current_qty * current_rate
    new_qty = current_qty + incoming_qty
    incoming_stock_value = incoming_qty * incoming_rate


    if new_qty > 0:
        new_rate = (current_stock_value + incoming_stock_value) / new_qty
    else:
        new_rate = incoming_rate if incoming_rate > 0 else current_rate

    return new_rate, new_qty * new_rate

     