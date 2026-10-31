from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.inventory.items import service
from app.inventory.items.schemas import TrackUpdate, ItemResponse, ItemGroupResponse, ItemGroupCreate, ItemCreate, ItemUpdate, ItemGroupUpdate, Activation
from database.database import get_db
from typing import List

router = APIRouter()

@router.get("/itemgroups/", response_model=List[ItemGroupResponse], tags = ["Item Group"])
def get_item_groups(db: Session = Depends(get_db)):
    return service.get_item_groups(db)

@router.get("/itemgroups/{group_id}/", response_model=ItemGroupResponse, tags = ["Item Group"])
def get_item_group_by_id(group_id: int, db: Session = Depends(get_db)):
    return service.get_item_group_by_id(db, group_id)

@router.post("/itemgroups/", response_model=ItemGroupResponse, tags = ["Item Group"])
def create_item_group(new_group: ItemGroupCreate, db: Session = Depends(get_db)):
    return service.create_item_group(db, new_group)

@router.patch("/itemsgroups/{group_id}/", response_model=ItemGroupResponse, tags = ["Item Group"])
def update_item_group(group_id: int, update_group: ItemGroupUpdate, db: Session = Depends(get_db)):
    return service.update_item_group(db, group_id, update_group)

@router.patch("/itemsgroups/activate/{group_id}/", response_model=Activation, tags = ["Item Group"])
def activate_item_group(group_id: int, activate: Activation, db: Session = Depends(get_db)):
    return service.activate_item_group(db, group_id, activate)

@router.get("/items/", response_model=List[ItemResponse], tags = ["Item"])
def get_items(db: Session = Depends(get_db)):
    return service.get_items(db)

@router.get("/items/{item_id}/", response_model=ItemResponse, tags = ["Item"])
def get_item_by_id(item_id: int, db: Session = Depends(get_db)):
    return service.get_item_by_id(db, item_id)

@router.post("/items/", response_model=ItemResponse, tags = ["Item"])
def create_item(new_item: ItemCreate, db: Session = Depends(get_db)):
    return service.create_item(db, new_item)

@router.patch("/items/{item_id}/", response_model=ItemResponse, tags = ["Item"])
def update_item(item_id: int, update_item: ItemUpdate, db: Session = Depends(get_db)):
    return service.update_item(db, item_id, update_item)

@router.patch("/items/track/{item_id}", response_model = ItemResponse, tags = ["Item"])
def track_item(item_id: int, track_item: TrackUpdate, db: Session = Depends(get_db)):
    return service.track_item(db, item_id, track_item)

@router.patch("/items/activate/{item_id}/", response_model=Activation, tags = ["Item"])
def activate_item(item_id: int, activate: Activation, db: Session = Depends(get_db)):
    return service.activate_item(db, item_id, activate)