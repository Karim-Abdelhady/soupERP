from sqlalchemy.orm import Session
from sqlalchemy import select, func
from fastapi import HTTPException, status
from .schemas import ItemCreate, ItemGroupCreate, ItemUpdate, ItemGroupUpdate, Activation, ItemwithBatchandSerialResponse
from app.inventory.items import repository
from datetime import datetime, timezone
from app.inventory.stock.stock_balance import repository as SBrepository
from app.inventory.stock.stock_ledger import repository as LedgerRepository
from app.inventory.stock.stock_balance.models import StockBalance
from app.inventory.warehouses import repository as WarehouseRepository
from app.inventory.tracking_items import repository as TrackingRepository
from app.inventory.items.models import ItemGroup

def get_item_groups(db: Session):
    groups = repository.get_item_groups(db)
    if not groups:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No Item groups were created")
    return groups

def get_item_group_by_id(db: Session, group_id: int):
    group = repository.get_item_group_by_id(db, group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Item Group with ID is not found")
    return group

def create_item_group(db: Session, new_group: ItemGroupCreate):
    existing_group = repository.get_item_group_by_code(db, new_group.group_code)
    if existing_group is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Item Group already exists ")

    new_data = new_group.model_dump(exclude_unset=True)
    return repository.create_item_group(db, new_data)

def update_item_group(db: Session, group_id: int, update_group: ItemGroupUpdate):
    group = repository.get_item_group_by_id(db, group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Group with ID is not found")

    if not group.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Item Group is not active")

    update_data = update_group.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(group, key, value)
    group.updated_at = datetime.now(timezone.utc)

    return repository.update_item_group(db, group)

def activate_item_group(db: Session, group_id: int, activate_group: Activation):
    group = repository.get_item_group_by_id(db, group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Group with ID is not found")

    if activate_group.is_active is not None:
        group.is_active = activate_group.is_active

    group.updated_at = datetime.now(timezone.utc)

    return repository.activation(db, group)

def get_items(db: Session):
    items = repository.get_items(db)
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "No items were created")
    return items

def get_item_by_id(db: Session, item_id: int):
    item = repository.get_item_by_id(db, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Item with ID is not found")
    return item

def get_item_with_batch_and_serial(db: Session, item_id: int):
    item = repository.get_item_with_batch_and_serial(db, item_id)
    if item is None:
        return None

    for batch in item.item_batch_track:
        statement = select(StockBalance).where(StockBalance.batch_id == batch.id, StockBalance.actual_qty > 0)
        balances = db.scalars(statement).all()
        total_batch_qty = sum(b.actual_qty for b in balances)
        batch.actual_qty = total_batch_qty

        warehouses = []
        for b in balances:
            warehouse = WarehouseRepository.get_warehouse_by_id(db, b.warehouse_id)
            warehouse_name = warehouse.name if warehouse else f"Warehouse {b.warehouse_id}"
            warehouses.append({
                "warehouse_id": b.warehouse_id,
                "warehouse_name": warehouse_name,
                "quantity": b.actual_qty
            })
        batch.warehouses = warehouses

    return item

def create_item(db: Session, new_item: ItemCreate):
    existing_item = repository.get_item_by_code(db, new_item.item_code)
    if existing_item is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail = "Item already exists")
    if not ItemGroup.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Item Group is inactive")
    if new_item.has_expiry_date and not new_item.is_batch_tracked:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Item cannot have an expiry date unless batch tracking is enabled")
    new_data = new_item.model_dump(exclude_unset=True)
    return repository.create_item(db, new_data)

def update_item(db: Session, item_id: int, update_item: ItemUpdate):
    item = repository.get_item_by_id(db, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Item with ID is not found")
    if not item.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Item is not active")
    if update_item.has_expiry_date and not update_item.is_batch_tracked:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Item cannot have an expiry date unless batch tracking is enabled")

    new_data = update_item.model_dump(exclude_unset=True)

    if update_item.has_expiry_date and not update_item.is_batch_tracked:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Item cannot have an expiry date without is_batch_tracked enabled")
    batch_changed = "is_batch_tracked" in new_data and new_data["is_batch_tracked"] != item.is_batch_tracked
    serial_changed = "is_serial_tracked" in new_data and new_data["is_serial_tracked"] != item.is_serial_tracked
    expiry_changed = "has_expiry_data" in new_data and new_data["has_expiry_date"] != item.has_expiry_date
    uom_changed = "stock_uom_id" in new_data and new_data["stock_uom_id"] != item.stock_uom_id

    ledger_entries = None
    if uom_changed or batch_changed or serial_changed or expiry_changed:
        ledger_entries = LedgerRepository.get_stock_ledger_item_history(db, item_id)
    if uom_changed and ledger_entries:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Cannot modify Base UOM because stock transactions already exists for this item")
    if batch_changed or serial_changed or expiry_changed:
        if ledger_entries:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Cannot modify batch, serial, or expiry tracking settings because stock transactions already exists for this item")
        existing_balance = SBrepository.get_stock_balance_item_history(db, item_id)
        if existing_balance:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Cannot modify batch, serial, or expiry tracking settings because stock balances are already exists for this item")
        existing_batches = TrackingRepository.get_batches_by_item_id(db, item_id)
        if existing_batches:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Cannot modify batch, serial, or expired tracking settings because batch records are already exists for this item")
        existing_serials = TrackingRepository.get_serials_by_item_id(db, item_id)
        if existing_serials:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Cannot modify batch, serial, or expired tracking settings because serial records are already exists for this item")
        
    for key, value in new_data.items():
        setattr(item, key, value)
    item.updated_at = datetime.now(timezone.utc)

    return repository.update_item(db, item)

def activate_item(db: Session, item_id: int, activate: Activation):
    item = repository.get_item_by_id(db, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Item with ID is not found")

    if activate.is_active is False:
        balances = SBrepository.get_stock_balance_item_history(db, item_id)
        total_stock = sum(b.actual_qty for b in balances) if balances else 0

        if total_stock > 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Cannot deactivate item since Item has active stock quantity")        

    if activate.is_active is not None:
        item.is_active = activate.is_active
    item.updated_at = datetime.now(timezone.utc)

    return repository.activation(db, item)