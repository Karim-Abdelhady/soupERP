from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from app.systemadministration.suppliers.schemas import UserSupplierResponse, SupplierUpdate
from typing import List
from database.database import get_db
from app.systemadministration.suppliers import service
from app.systemadministration.users.schemas import UserResponse
from app.systemadministration.auth.permissions import PermissionCatalog, require_permission
from app.systemadministration.users.models import User


router = APIRouter()

@router.get("/users/suppliers",response_model=List[UserSupplierResponse], tags = ["Suppliers"])
def get_suppliers(db: Session = Depends(get_db), current_user: User = Depends(require_permission(PermissionCatalog.SUPPLIER_READ))):
    return service.get_suppliers(db)

@router.get("/users/suppliers/{supplier_id}", response_model=UserSupplierResponse, tags = ["Suppliers"])
def get_supplier_by_supplier_id(supplier_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission(PermissionCatalog.SUPPLIER_READ))):
    return service.get_supplier_by_supplier_id(db, supplier_id)

@router.post("/users/suppliers/{user_id}", response_model=UserResponse, tags = ["Suppliers"])
def convert_user_to_supplier(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission(PermissionCatalog.SUPPLIER_CREATE))):
    return service.convert_user_to_supplier(db, user_id)

@router.patch("/users/suppliers/{user_id}", response_model=UserSupplierResponse, tags = ["Suppliers"])
def update_supplier(user_id: int, updateSupplier: SupplierUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_permission(PermissionCatalog.SUPPLIER_UPDATE))):
    return service.update_supplier(db, user_id, updateSupplier)