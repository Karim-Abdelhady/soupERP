from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .schemas import ItemCreate, ItemGroupCreate, ItemUpdate, ItemGroupUpdate, Activation, TrackUpdate
from app.inventory.items import repository
from datetime import datetime, timezone

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

def create_item(db: Session, new_item: ItemCreate):
    existing_item = repository.get_item_by_code(db, new_item.item_code)
    if existing_item is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail = "Item already exists")

    new_data = new_item.model_dump(exclude_unset=True)
    return repository.create_item(db, new_data)

def update_item(db: Session, item_id: int, update_item: ItemUpdate):
    item = repository.get_item_by_id(db, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Item with ID is not found")
    new_data = update_item.model_dump(exclude_unset=True)
    for key, value in new_data.items():
        setattr(item, key, value)
    item.updated_at = datetime.now(timezone.utc)

    return repository.update_item(db, item)

def track_item(db: Session, item_id: int, track_item: TrackUpdate):
    item = repository.get_item_by_id(db, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Item not found")

    if track_item.expiry_date is None and hasattr(track_item, "expiry_date") and track_item.expiry_date == None:
        item.expiry_date = None

    if item.expiry_date is not None:
        if track_item.is_serial_tracked is False or track_item.is_batch_tracked is False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Cannot disable tracking modes while an expiry date is assigned.")
        if track_item.has_expiry_date is False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Cannot disable expiry tracking while an expiry date is assigned.")

    if track_item.is_serial_tracked is not None:
        item.is_serial_tracked = track_item.is_serial_tracked
    if track_item.is_batch_tracked is not None:
        item.is_batch_tracked = track_item.is_batch_tracked
    if track_item.has_expiry_date is not None:
        item.has_expiry_date = track_item.has_expiry_date

    if track_item.expiry_date is not None:
        if not item.has_expiry_date or not (item.is_batch_tracked or item.is_serial_tracked):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Expiry date can only be set if the item has expiry tracking enabled and is batch or serial tracked.")
        item.expiry_date = track_item.expiry_date


    item.updated_at = datetime.now(timezone.utc)

    return repository.track_item(db, item)

def activate_item(db: Session, item_id: int, activate: Activation):
    item = repository.get_item_by_id(db, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Item with ID is not found")

    if activate.is_active is not None:
        item.is_active = activate.is_active
    item.updated_at = datetime.now(timezone.utc)

    return repository.activation(db, item)