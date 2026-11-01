from sqlalchemy.orm import Session
from sqlalchemy import select
from app.inventory.warehouses.models import Warehouse, WarehouseType
from app.inventory.warehouses.schemas import Activation

def get_warehouse_types(db: Session):
    statement = select(WarehouseType)
    return db.scalars(statement).all()

def get_warehouse_type_by_id(db: Session, type_id: int):
    statement = select(WarehouseType).where(WarehouseType.id == type_id)
    return db.scalar(statement)

def get_warehouse_type_by_name(db: Session, type_name: str):
    statement = select(WarehouseType).where(WarehouseType.name == type_name)
    return db.scalar(statement)

def create_warehouse_type(db: Session, new_type: WarehouseType):
    new_data = WarehouseType(**new_type)
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return new_data

def update_warehouse_type(db: Session, update_type: WarehouseType):
    db.commit()
    db.refresh(update_type)
    return update_type

def get_warehouses(db: Session):
    statement = select(Warehouse)
    return db.scalars(statement).all()

def get_warehouse_by_id(db: Session, warehouse_id: int):
    statement = select(Warehouse).where(Warehouse.id == warehouse_id)
    return db.scalar(statement)

def get_warehouse_by_code(db: Session, warehouse_code: str):
    statement = select(Warehouse).where(Warehouse.code == warehouse_code)
    return db.scalar(statement)

def create_warehouse(db: Session, new_warehouse: Warehouse):
    new_data = Warehouse(**new_warehouse)
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return new_data 

def update_warehouse(db: Session, update_warehouse: Warehouse):
    db.commit()
    db.refresh(update_warehouse)
    return update_warehouse

def activation(db: Session, activate: Activation):
    db.commit()
    db.refresh(activate)
    return activate