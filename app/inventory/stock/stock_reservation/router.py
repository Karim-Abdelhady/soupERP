from fastapi import APIRouter, Depends
from database.database import get_db
from sqlalchemy.orm import Session
from app.inventory.stock.stock_reservation.schemas import StockReservationCreate, StockReservationResponse
from typing import List
from app.inventory.stock.stock_reservation import service

router = APIRouter()

@router.get("/stockreservations/", response_model=List[StockReservationResponse], tags = ["Stock Reservation"])
def get_stock_reservations(db: Session = Depends(get_db)):
    return service.get_stock_reservations(db)

@router.get("/stockreservations/{reservation_id}/", response_model=StockReservationResponse, tags = ["Stock Reservation"])
def get_stock_reservation(reservation_id: int, db: Session = Depends(get_db)):
    return service.get_stock_reservation_by_id(db, reservation_id)


@router.get("/stockreservations/item/{item_id}", response_model=StockReservationResponse, tags = ["Stock Reservation"])
def get_stock_reservations_by_item_id(item_id: int, db: Session = Depends(get_db)):
    return service.get_stock_reservation_by_item_id(db, item_id)

@router.get("/stockreservations/item/{item_id}/quantity", response_model=StockReservationResponse, tags = ["Stock Reservation"])
def get_resreved_qty(item_id: int, db: Session = Depends(get_db)):
    return service.get_reserved_qty(db, item_id)

@router.get("/stockreservations/warehouse/{warehouse_id}", response_model=StockReservationResponse, tags = ["Stock Reservation"])
def get_stock_reservations_by_warehouse_id(warehouse_id: int, db: Session = Depends(get_db)):
    return service.get_stock_reservation_by_warehouse_id(db, warehouse_id)

@router.get("/stockreservations/item/{item_id}/warehouse/{warehouse_id}", response_model=StockReservationResponse, tags = ["Stock Reservation"])
def get_stock_resrevations_by_item_and_warehouse(item_id: int, warehouse_id: int, db: Session = Depends(get_db)):
    return get_stock_resrevations_by_item_and_warehouse(db, item_id, warehouse_id)

@router.post("/stockreservations/active/", response_model=StockReservationResponse, tags = ["Stock Reservation"])
def create_stock_reservation(new_reservation: StockReservationCreate, db: Session = Depends(get_db)):
    return create_stock_reservation(db, new_reservation)

@router.post("/stockreservations/{reservation_id}/fulfill/", response_model=StockReservationResponse, tags = ["Stock Reservation"])
def fulfill_stock_reservation(reservation_id: int, db: Session = Depends(get_db)):
    return fulfill_stock_reservation(db, reservation_id)

@router.post("/stockreservations/{reservation_id}/release/", response_model=StockReservationResponse, tags = ["Stock Reservation"])
def release_stock_reservation(reservation_id: int, db: Session = Depends(get_db)):
    return release_stock_reservation(db, reservation_id)