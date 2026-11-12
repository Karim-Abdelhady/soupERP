from database.database import get_db
from sqlalchemy.orm import Session
from app.inventory.reorder import service
from fastapi import APIRouter, Depends
from app.inventory.reorder.schemas import ReorderUpdate, ReorderCreate, ReorderResponse, Activation
from typing import List

router = APIRouter()

@router.get("/reorders/", response_model=List[ReorderResponse], tags = ["Reorder Rules"])
def get_reorder_rules(db: Session = Depends(get_db)):
    return service.get_reorder_rules(db)

@router.get("/reorders/{reorder_id}", response_model = ReorderResponse, tags = ["Reorder Rules"])
def get_reorder_rule_by_id(reorder_id: int, db: Session = Depends(get_db)):
    return service.get_reorder_rule_by_id(db, reorder_id)

@router.get("/reorders/items/{item_id}", response_model= List[ReorderResponse], tags = ["Reorder Rules"])
def get_reorder_rule_by_item_id(item_id: int, db: Session = Depends(get_db)):
    return service.get_reorder_rules_by_item_id(db, item_id)

@router.get("/reorders/warehouses/{warehouse_id}", response_model= List[ReorderResponse], tags = ["Reorder Rules"])
def get_reorder_rules_by_warehouse_id(warehouse_id: int, db: Session = Depends(get_db)):
    return service.get_reorder_rules_by_warehouse_id(db, warehouse_id)

@router.get("/reorder/items/{item_id}/warehouses/{warehouse_id}/", response_model=List[ReorderResponse], tags = ["Reorder Rules"])
def get_reorder_rules_by_item_and_warehouse(item_id: int, warehouse_id: int, db: Session = Depends(get_db)):
    return service.get_reorder_rules_by_item_and_warehouse(db, item_id, warehouse_id)

@router.post("/reorders/", response_model=ReorderResponse, tags = ["Reorder Rules"])
def create_reorder_rules(new_reorder: ReorderCreate, db: Session = Depends(get_db)):
    return service.create_reorder_rule(db, new_reorder)

@router.patch("/reorders/{reorder_id}/", response_model=ReorderResponse, tags = ["Reorder Rules"])
def update_reorder_rules(reorder_id: int, update_reorder: ReorderUpdate, db: Session = Depends(get_db)):
    return service.update_reorder_rule(db, reorder_id, update_reorder)

@router.patch("/reorders/{reorder_id}/activate", response_model=ReorderResponse, tags = ["Reorder Rules"])
def activate_reorder_rule(reorder_id: int, activate: Activation, db: Session = Depends(get_db)):
    return service.activate_reorder_rule(db, reorder_id, activate)

@router.get("/reorders/{reorder_id}/stockalert/", tags = ["Stock Alert"]) #only for test calling
def check_stock_alert(reorder_id: int, db: Session = Depends(get_db)):
    return service.check_stock_alert(db, reorder_id)