from database.database import get_db
from fastapi import Depends, APIRouter
from app.inventory.warehouses.schemas import WarehouseResponse, WarehouseTypeResponse, WarehouseCreate, WarehouseTypeCreate, WarehouseUpdate, WarehouseTypeUpdate, Activation
from typing import List
from sqlalchemy.orm import Session
from app.inventory.warehouses import service

router = APIRouter()

@router.get("/warehousetypes/", response_model=List[WarehouseTypeResponse], tags = ["Warehouse Type"])
def get_warehouse_types(db: Session = Depends(get_db)):
    return service.get_warehouse_types(db)

@router.get("/warehousetypes/{type_id}/", response_model=WarehouseTypeResponse, tags = ["Warehouse Type"])
def get_warehouse_type_by_id(type_id: int, db: Session = Depends(get_db)):
    return service.get_warehouse_type_by_id(db, type_id)

@router.post("/warehousetypes/", response_model=WarehouseTypeResponse, tags = ["Warehouse Type"])
def create_warehouse_type(new_warehouse: WarehouseTypeCreate, db: Session = Depends(get_db)):
    return service.create_warehouse_type(db, new_warehouse)

@router.patch("/warehousetypes/{type_id}/", response_model = WarehouseTypeResponse, tags = ["Warehouse Type"])
def update_warehouse_type(type_id: int, update_warehouse: WarehouseTypeUpdate, db: Session = Depends(get_db)):
    return service.update_warehouse_type(db, type_id, update_warehouse)

@router.patch("/warehousetypes/activate/{type_id}/", response_model=Activation, tags = ["Warehouse Type"])
def activate_warehouse_type(type_id: int, activate: Activation, db: Session = Depends(get_db)):
    return service.activate_warehouse_type(db, type_id, activate)

@router.get("/warehouses/", response_model = List[WarehouseResponse], tags = ["Warehouse"])
def get_warehouses(db: Session = Depends(get_db)):
    return service.get_warehouses(db)

@router.get("/warehouses/{warehouse_id}", response_model = WarehouseResponse, tags = ["Warehouse"])
def get_warehouse_by_id(warehouse_id: int, db: Session = Depends(get_db)):
    return service.get_warehouse_by_id(db, warehouse_id)

@router.post("/warehouses", response_model=WarehouseResponse, tags = ["Warehouse"])
def create_warehouse(new_warehouse: WarehouseCreate, db: Session = Depends(get_db)):
    return service.create_warehouse(db, new_warehouse)

@router.patch("/warehouses/{warehouse_id}", response_model=WarehouseResponse, tags = ["Warehouse"])
def update_warehouse(warehouse_id: int, update_warehouse: WarehouseUpdate, db: Session = Depends(get_db)):
    return service.update_warehouse(db, warehouse_id, update_warehouse)

@router.patch("/warehouses/activate/{warehouse_id}", response_model=Activation, tags = ["Warehouse"])
def activate_warehouse(warehouse_id: int, activate: Activation, db: Session = Depends(get_db)):
    return service.activate_warehouse(db, warehouse_id, activate)