from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.inventory.reorder import repository
from app.inventory.reorder.schemas import ReorderCreate, ReorderUpdate, Activation
from datetime import datetime, timezone
from app.inventory.stock.stock_balance import repository as SBrepository

def get_reorder_rules(db: Session):
    reorders = repository.get_reorder_rules(db)
    if not reorders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "No Reorder Rule was found")
    return reorders

def get_reorder_rule_by_id(db: Session, reorder_id: int):
    reorder = repository.get_reorder_rule_by_id(db, reorder_id)
    if reorder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Reorder ID is not found")
    return reorder

def get_reorder_rules_by_item_id(db: Session, item_id: int):
    reorders = repository.get_reorder_rules_by_item_id(db, item_id)
    if not reorders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Item ID is not associated with Reorders")
    return reorders

def get_reorder_rules_by_warehouse_id(db: Session, warehouse_id: int):
    reorders = repository.get_reorder_rules_by_warehouse_id(db, warehouse_id)
    if not reorders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Warehouse ID is not associated with Reorders")
    return reorders

def get_reorder_rules_by_item_and_warehouse(db: Session, item_id: int, warehouse_id: int):
    reorders = repository.get_reorder_rules_by_item_and_warehouse(db, item_id, warehouse_id)
    if not reorders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Item and/or Warehouse is not associated with Reorders")
    return reorders

def create_reorder_rule(db: Session, new_reorder: ReorderCreate):
    if new_reorder.reorder_level < new_reorder.safety_stock_level:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Reorder Level cannot be less than the safety stock level")
    new_data = new_reorder.model_dump(exclude_unset=True)
    new_data["is_active"] = True
    return repository.create_reorder_rule(db, new_data)

def update_reorder_rule(db: Session, reorder_id: int, update_reorder: ReorderUpdate):
    reorder = repository.get_reorder_rule_by_id(db, reorder_id)
    if reorder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Reorder Rule ID is not found")
    if not reorder.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Reorder Rule is not active")
    
    update_data = update_reorder.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(reorder, key, value)
    reorder.updated_at = datetime.now(timezone.utc)

    return repository.update_reorder_rule(db, reorder)

def activate_reorder_rule(db: Session, reorder_id: int, activate: Activation):
    reorder = repository.get_reorder_rule_by_id(db, reorder_id)
    if reorder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Reorder Rule ID is not found")

    if activate.is_active is not None:
        reorder.is_active = activate.is_active

    reorder.updated_at = datetime.now(timezone.utc)

    return repository.activate_reorder_rule(db, reorder)

def check_stock_alert(db: Session, reorder_id: int):
    reorder = repository.get_reorder_rule_by_id(db, reorder_id)
    if reorder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Reorder ID is not found")
    balance = SBrepository.get_stock_balance_by_item_and_warehouse(db, reorder.item_id, reorder.warehouse_id)
    if balance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Item and/or Warehouse is not associated with a stock balance")
    if not reorder.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Reorder Rule is not Active")

    is_below_reorder = balance.available_qty <= reorder.reorder_level
    if is_below_reorder:
        deflict = reorder.reorder_level - balance.available_qty
        print(f"Stock Alert: Item {reorder.item_id} in Warehouse {reorder.warehouse_id} is low with deflict of {deflict}.")

    return is_below_reorder