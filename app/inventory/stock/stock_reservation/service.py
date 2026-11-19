from sqlalchemy.orm import Session
from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.inventory.stock.stock_reservation.enums import ReservationStatus
from app.inventory.stock.stock_reservation import repository
from app.inventory.stock.stock_reservation.schemas import StockReservationCreate
from app.inventory.stock.stock_balance import repository as SBrepository
from app.inventory.items import repository as ItemRepository
from app.inventory.tracking_items import repository as TrackRepository
from app.inventory.tracking_items.enums import SerialStatus
from app.inventory.warehouses import repository as WarehouseRepository
from app.inventory.stock.stock_ledger.service import create_stock_ledger_entry
from app.inventory.stock.stock_ledger.schemas import StockLedgerCreate

def create_stock_reservation(db: Session, new_reservation: StockReservationCreate):
    item = ItemRepository.get_item_by_id(db, new_reservation.item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item ID is not found")

    batch_id = getattr(new_reservation, "batch_id", None)
    serial_id = getattr(new_reservation, "serial_id", None)

    check_item_and_warehouse_active_status(db, new_reservation.item_id, new_reservation.warehouse_id)

    if getattr(item, "is_batch_tracked", False):
        if not batch_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Batch ID is required for batch-tracked items.")
        
        batch = TrackRepository.get_batch_number_by_id(db, batch_id)
        if batch is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch ID is not found")
        if batch.item_id != new_reservation.item_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Batch does not belong to the item")
        if batch.expiry_date:
            current_date = datetime.now(timezone.utc).date()
            batch_exp = batch.expiry_date.date() if isinstance(batch.expiry_date, datetime) else batch.expiry_date
            if batch_exp < current_date:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot reserve expired batch")

    if getattr(item, "is_serial_tracked", False):
        if not serial_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Serial ID(s) are required for serialized items.")
        
        if len(serial_id) != int(new_reservation.quantity):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reservation quantity must match the number of serial IDs provided.")

        for s_id in serial_id:
            serial = TrackRepository.get_serial_number_by_id(db, s_id)
            if serial is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Serial ID {s_id} is not found")
            if serial.status != SerialStatus.INSTOCK.value:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Serial ID {s_id} is not In Stock")

    if batch_id:
        balance = SBrepository.get_stock_balance_by_item_warehouse_and_batch(db, new_reservation.item_id, new_reservation.warehouse_id, batch_id)
    else:
        balance = SBrepository.get_stock_balance_by_item_warehouse_and_batch(db, new_reservation.item_id, new_reservation.warehouse_id, batch_id)

    if not balance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item and/or Warehouse do not belong to a Stock Balance")

    available_quantity = balance.actual_qty - balance.reserved_qty
    if available_quantity < new_reservation.quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Available quantity is less than the reservation quantity")

    balance.reserved_qty = balance.reserved_qty + new_reservation.quantity
    balance.available_qty = balance.actual_qty - balance.reserved_qty
    if new_reservation.quantity <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Reservation quantity can not be zero or less")

    new_data = new_reservation.model_dump(exclude_unset=True)
    new_data["status"] = ReservationStatus.ACTIVE.value
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

    if reservation.status == ReservationStatus.FULFILLED.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Reservation is already fulfilled")

    if reservation.status == ReservationStatus.RELEASED.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Cannot fulfil a released reservation")

    check_item_and_warehouse_active_status(db, reservation.item_id, reservation.warehouse_id)

    batch_id = getattr(reservation, "batch_id", None)

    if batch_id is None:
        balance = SBrepository.get_stock_balance_by_item_warehouse_and_batch(db, reservation.item_id, reservation.warehouse_id)
    else:
        balance = SBrepository.get_stock_balance_by_item_warehouse_and_batch(db, reservation.item_id, reservation.warehouse_id)
    if not balance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Associated Stock balance is not found")
    if balance.actual_qty < reservation.quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Actual quantity is less than reservation quantity")
    if balance.reserved_qty < reservation.quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Reserved stock quantity is less than reservation quantity")
    
    balance.reserved_qty = balance.reserved_qty - reservation.quantity

    ledger_entry = StockLedgerCreate(
        item_id = reservation.item_id,
        batch_id= reservation.batch_id,
        serial_id = reservation.serial_id,
        warehouse_id = reservation.warehouse_id,
        quantity_delta=abs(reservation.quantity),
        incoming_rate=0.0,
        outgoing_rate=float(getattr(balance, "valuation_rate", 0.0) or 0.0),
        voucher_type="Stock Reservation",
        voucher_id=str(reservation.id),
        voucher_line_id=setattr(getattr(reservation, "source_line_id"), None)
    )
    create_stock_ledger_entry(db, ledger_entry)

    db.commit()
    db.refresh(balance)
    db.refresh(reservation)
    return reservation

def release_stock_reservation(db: Session, reservation_id):
    reservation = repository.get_stock_reservation_by_id(db, reservation_id)
    if reservation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock Reservation ID is not found")    

    if reservation.status == ReservationStatus.RELEASED.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stock Reservation is already released") # 400 is better than 404 for already released

    if getattr(reservation, "batch_id", None):
        balance = SBrepository.get_stock_balance_by_item_warehouse_and_batch(
            db, reservation.item_id, reservation.warehouse_id, reservation.batch_id
        )
    else:
        balance = SBrepository.get_stock_balance_by_item_and_warehouse(
            db, reservation.item_id, reservation.warehouse_id
        )

    if balance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock Balance not found for item/warehouse/batch")
 
    balance.reserved_qty = balance.reserved_qty - reservation.quantity
    balance.available_qty = balance.actual_qty - balance.reserved_qty
    
    reservation.status = ReservationStatus.RELEASED.value
    reservation.released_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(balance)
    db.refresh(reservation)
    return reservation

def check_item_and_warehouse_active_status(db: Session, item_id: int, *warehouse_ids):
    item = ItemRepository.get_item_by_id(db, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Item ID is not found")
    if hasattr(item, "is_active") and not item.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Item is inactive")

    for warehouse_id in warehouse_ids:
        if warehouse_id is not None:
            warehouse = WarehouseRepository.get_warehouse_by_id(db, warehouse_id)
            if warehouse is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Warehouse ID is not found")
            if not warehouse.is_active:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Warehouse ID is inactive")



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