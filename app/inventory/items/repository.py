from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import Item, ItemGroup
from .schemas import Activation

def get_item_groups(db: Session):
    statement = select(ItemGroup)
    return db.scalars(statement).all()

def get_item_group_by_id(db: Session, group_id: int):
    statement = select(ItemGroup).where(ItemGroup.id == group_id)
    return db.scalar(statement)

def get_item_group_by_code(db: Session, group_code: str):
    statement = select(ItemGroup).where(ItemGroup.group_code == group_code)
    return db.scalar(statement)

def create_item_group(db: Session, new_group: ItemGroup):
    new_data = ItemGroup(**new_group)
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return new_data

def update_item_group(db: Session, update_group: ItemGroup):
    db.commit()
    db.refresh(update_group)
    return update_group

def get_items(db: Session):
    statement = select(Item)
    return db.scalars(statement).all()

def get_item_by_id(db: Session, item_id: int):
    statement = select(Item).where(Item.id == item_id)
    return db.scalar(statement)

def get_item_by_code(db: Session, item_code: str):
    statement = select(Item).where(Item.item_code == item_code)
    return db.scalar(statement)

def create_item(db: Session, new_item: Item):
    new_data = Item(**new_item)
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return new_data

def update_item(db: Session, update_item: Item):
    db.commit()
    db.refresh(update_item)
    return update_item

def track_item(db: Session, track_item: Item):
    db.commit()
    db.refresh(track_item)
    return track_item

def activation(db: Session, activate: Activation):
    db.commit()
    db.refresh(activate)
    return activate