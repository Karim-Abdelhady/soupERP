from sqlalchemy.orm import Session
from sqlalchemy import select
from app.inventory.reorder.models import ItemReorderRule
from app.inventory.reorder.schemas import Activation

def get_reorder_rules(db: Session):
    statement = select(ItemReorderRule)
    return db.scalars(statement).all()

def get_reorder_rule_by_id(db: Session, reorder_id: int):
    statement = select(ItemReorderRule).where(ItemReorderRule.id == reorder_id)
    return db.scalar(statement)

def get_reorder_rules_by_item_id(db: Session, item_id: int):
    statement = select(ItemReorderRule).where(ItemReorderRule.item_id == item_id)
    return db.scalars(statement).all()

def get_reorder_rules_by_warehouse_id(db: Session, warehouse_id: int):
    statement = select(ItemReorderRule).where(ItemReorderRule.warehouse_id == warehouse_id)
    return db.scalars(statement).all()

def get_reorder_rules_by_item_and_warehouse(db: Session, item_id: int, warehouse_id: int):
    statement = (
        select(ItemReorderRule)
        .where(
            ItemReorderRule.item_id == item_id,
            ItemReorderRule.warehouse_id == warehouse_id
        )
    )
    return db.scalars(statement).all()


def create_reorder_rule(db: Session, new_reorder: ItemReorderRule):
    new_data = ItemReorderRule(**new_reorder)
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return new_data

def update_reorder_rule(db: Session, update_reorder: ItemReorderRule):
    db.commit()
    db.refresh(update_reorder)
    return update_reorder

def activate_reorder_rule(db: Session, activate: ItemReorderRule):
    db.commit()
    db.refresh(activate)
    return activate