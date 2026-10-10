from sqlalchemy.orm import Session
from app.suppliers import repository
from fastapi import HTTPException, status
from app.users.models import User, UserType
from app.suppliers.models import Supplier
from app.suppliers.schemas import SupplierUpdate
from app.users import repository as userRepository
from datetime import datetime, timezone

def get_supplier_by_supplier_id(db: Session, supplier_id: int):
    supplier = repository.get_supplier_by_supplier_id(db, supplier_id)
    if supplier is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier is not found")
    return supplier

def get_suppliers(db: Session):
    return repository.get_suppliers(db)

def convert_user_to_supplier(db: Session, user_id: int) -> User:
    user = userRepository.get_user_by_user_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "User is not found")
    user.user_type = UserType.SUPPLIER
    user.updated_at = datetime.now(timezone.utc)
    return repository.convert_user_to_supplier(db, user)

def update_supplier(db: Session, user_id: int, updateSupplier: SupplierUpdate):
    user = userRepository.get_user_by_user_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User is not found")
    if user.user_type != UserType.SUPPLIER:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is not a supplier")
    
    update_data = updateSupplier.model_dump(exclude_unset = True)
    if not user.supplier_profile:
        supplier = Supplier(supplier_id=user.id, **update_data)
        db.add(supplier)
    else:
        for field, value in update_data.items():
            setattr(user.supplier_profile, field, value)
    user.updated_at = datetime.now(timezone.utc)
    updated_user = repository.update_supplier(db, user)
    return {
        "user": updated_user,
        "supplier_profile": updated_user.supplier_profile
    }