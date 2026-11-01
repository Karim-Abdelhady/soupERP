from sqlalchemy.orm import Session
from app.inventory.warehouses import repository
from fastapi import HTTPException,status
from app.inventory.warehouses.schemas import WarehouseCreate, WarehouseTypeCreate, WarehouseUpdate, WarehouseTypeUpdate, Activation
from datetime import datetime, timezone

def get_warehouse_types(db: Session):
    types = repository.get_warehouse_types(db)
    if not types:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "No warehouse type is created")
    return types

def get_warehouse_type_by_id(db: Session, type_id: int):
    type = repository.get_warehouse_type_by_id(db, type_id)
    if type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Warehouse type with ID is not found")
    return type

def create_warehouse_type(db: Session, new_warehouse: WarehouseTypeCreate):
    existing_warehouse_type = repository.get_warehouse_type_by_name(db, new_warehouse.name)
    if existing_warehouse_type is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Warehouse is already created")

    new_data = new_warehouse.model_dump(exclude_unset=True)
    return repository.create_warehouse_type(db, new_data)

def update_warehouse_type(db: Session, type_id: int, update_warehouse: WarehouseTypeUpdate):
    type = repository.get_warehouse_type_by_id(db, type_id)
    if type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Warehouse type with ID is not found")

    update_data = update_warehouse.model_dump(exclude_unset=True)
    for key,value in update_data.items():
        setattr(type, key, value)
    type.updated_at = datetime.now(timezone.utc)

    return repository.update_warehouse_type(db, type)

def activate_warehouse_type(db: Session, type_id: int, activate: Activation):
    type = repository.get_warehouse_type_by_id(db, type_id)
    if type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Warehouse type with ID is not found")

    if activate.is_active is not None:
        type.is_active = activate.is_active

    type.updated_at = datetime.now(timezone.utc)

    return repository.activation(db, type)

def get_warehouses(db: Session):
    warehouses = repository.get_warehouses(db)
    if not warehouses:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "No warehouses were created")
    return warehouses

def get_warehouse_by_id(db: Session, warehouse_id: int):
    warehouse = repository.get_warehouse_by_id(db, warehouse_id)
    if warehouse is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Warehouse with ID is not found")
    return warehouse

def create_warehouse(db: Session, new_warehouse: WarehouseCreate):
    existing_warehouse = repository.get_warehouse_by_code(db, new_warehouse.code)
    if existing_warehouse is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Warehouse is already created")

    new_data = new_warehouse.model_dump(exclude_unset=True)
    return repository.create_warehouse(db, new_data)

def update_warehouse(db: Session, warehouse_id: int, update_warehouse: WarehouseUpdate):
    warehouse = repository.get_warehouse_by_id(db, warehouse_id)
    if warehouse is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Warehouse with ID is not found")

    update_data = update_warehouse.model_dump(exclude_unset=True)

    target_is_group = update_data.get("is_group", warehouse.is_group)
    target_parent_id = update_data.get("parent_id", warehouse.parent_id)

    if target_parent_id is not None and not target_is_group:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "A warehouse cannot have a parent unless it is designated as a group warehouse.")

    if target_parent_id == warehouse_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "A warehouse cannot be assigned as its own parent.")

    if target_parent_id is not None:
        parent_warehouse = repository.get_warehouse_by_id(db, target_parent_id)
        if parent_warehouse is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent warehouse does not exist.")
        if parent_warehouse.parent_id is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail ="Parent warehouse can not have a parent warehouse.")

    for key, value in update_data.items():
        setattr(warehouse, key, value)
    warehouse.updated_at = datetime.now(timezone.utc)

    return repository.update_warehouse(db, warehouse)

def activate_warehouse(db: Session, warehouse_id: int, activate: Activation):
    warehouse = repository.get_warehouse_by_id(db, warehouse_id)
    if warehouse is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Warehouse with ID is not found")

    if activate.is_active is not None:
        warehouse.is_active = activate.is_active

    warehouse.updated_at = datetime.now(timezone.utc)

    return repository.activation(db, warehouse)
