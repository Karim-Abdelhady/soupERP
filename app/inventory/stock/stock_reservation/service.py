from sqlalchemy.orm import Session
from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.inventory.stock.stock_reservation.enums import Status
from app.inventory.stock.stock_reservation import repository
from app.inventory.stock.stock_reservation.schemas import StockReservationCreate
from app.inventory.stock.stock_balance import repository as SBrepository

def create_stock_reservation(db: Session, new_reservation: StockReservationCreate):
    balance = SBrepository.get_stock_balance_by_item_and_warehouse(db, new_reservation.item_id, new_reservation.warehouse_id)
    if not balance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Item and/or Warehouse do not belong to a Stock Balance")

    available_quantity = balance.actual_qty - balance.reserved_qty
    if available_quantity < new_reservation.quantity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Available quantity is less than the reservation quantity")

    balance.reserved_qty = balance.reserved_qty + new_reservation.quantity
    balance.available_qty = balance.actual_qty - balance.reserved_qty
    new_data = new_reservation.model_dump(exclude_unset=True)
    new_data["status"] = Status.ACTIVE
    new_data["reserved_at"] = datetime.now(timezone.utc)

    reservation = repository.create_stock_reservation(db, new_data)
    db.commit()
    db.refresh(balance)
    db.refresh(reservation)
    return reservation

def fulfill_stock_reservation(db: Session, reservation_id: int):
    reservation = repository.get_stock_reservation_by_id(db, reservation_id)
    if reservation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Stock Reservation ID is not found")

    if reservation.status == Status.FULFILLED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Reservation is already fulfilled")

    balance = SBrepository.get_stock_balance_by_item_and_warehouse(db, reservation.item_id, reservation.warehouse_id)
    if not balance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Associated Stock balance is not found")
    
    balance.actual_qty = balance.actual_qty - reservation.quantity
    balance.reserved_qty = balance.reserved_qty - reservation.quantity
    balance.available_qty = balance.actual_qty - balance.reserved_qty
    reservation.status = Status.FULFILLED
    reservation.fulfilled_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(balance)
    db.refresh(reservation)
    return reservation

def release_stock_reservation(db: Session, reservation_id):
    reservation = repository.get_stock_reservation_by_id(db, reservation_id)
    if reservation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Stock Reservation ID is not found")    

    if reservation.status == Status.RELEASED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Stock Reservation is already released")


    balance = SBrepository.get_stock_balance_by_item_and_warehouse(db, reservation.item_id, reservation.warehouse_id)
    if balance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Stock Reservation Line is not found")
 
    balance.reserved_qty = balance.reserved_qty - reservation.quantity
    balance.available_qty = balance.available_qty - balance.reserved_qty
    
    reservation.status = Status.RELEASED
    reservation.released_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(balance)
    db.refresh(reservation)
    return reservation

def get_reserved_qty(db: Session, item_id: int, quantity: int):
    quantity = repository.get_reserved_qty(db, item_id, quantity)
    if quantity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Item does not have a quantity")
    return quantity

def get_stock_reservations(db: Session):
    reservations = repository.get_stock_reservations(db)
    if not reservations:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "No stock reservations were found")
    return reservations

def get_stock_reservation_by_id(db: Session, reservation_id: int):
    reservation = repository.get_stock_reservation_by_id(db, reservation_id)
    if reservation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Stock Reservation ID is not found")
    return reservation

def get_stock_reservation_by_item_id(db: Session, item_id: int):
    reservation = repository.get_stock_reservations_by_item_id(db, item_id)
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Item ID does not belong to any Stock Reservation")
    return reservation

def get_stock_reservation_by_warehouse_id(db: Session, warehouse_id: int):
    reservation = repository.get_stock_reservations_by_warehouse_id(db, warehouse_id)
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Warehoues ID does not belong to any Stock Reservation")
    return reservation

def get_stock_reservation_by_item_and_warehouse(db: Session, item_id: int, warehouse_id: int):
    reservation = repository.get_stock_reservations_by_item_and_warehouse(db, item_id, warehouse_id)
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Item and Warehouse do not belong to a Stock Reservation")