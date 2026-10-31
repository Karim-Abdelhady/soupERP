from fastapi import Depends, APIRouter
from database.database import get_db
from app.systemadministration.customers.schemas import CustomerUserResponse
from sqlalchemy.orm import Session
from app.systemadministration.customers import service
from typing import List
from app.systemadministration.customers.schemas import CustomerUpdate
from app.systemadministration.users.schemas import UserResponse
from app.systemadministration.auth.permissions import require_permission, PermissionCatalog
from app.systemadministration.users.models import User

router = APIRouter()

@router.get("/users/customers", response_model= List[CustomerUserResponse], tags = ["Customers"])
def get_customers(db: Session = Depends(get_db), current_user: User = Depends(require_permission(PermissionCatalog.CUSTOMER_READ))):
    return service.get_customers(db)

@router.get("/users/customers/{customer_id}", response_model=CustomerUserResponse, tags = ["Customers"])
def get_customer_by_customer_id(customer_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission(PermissionCatalog.CUSTOMER_READ))):
    return service.get_customer_by_customer_id(db, customer_id)

@router.post("/users/customers/{user_id}", response_model=UserResponse, tags = ["Customers"])
def convert_user_to_customer(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission(PermissionCatalog.CUSTOMER_CREATE))):
    return service.convert_user_to_customer(db, user_id)

@router.patch("/users/customers/{customer_id}", response_model=CustomerUserResponse, tags = ["Customers"])
def update_customer(customer_id: int, updateCustomer: CustomerUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_permission(PermissionCatalog.CUSTOMER_UPDATE))):
    return service.update_customer(db, customer_id, updateCustomer)