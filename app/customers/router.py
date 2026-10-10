from fastapi import Depends, APIRouter
from database.database import get_db
from app.customers.schemas import CustomerUserResponse
from sqlalchemy.orm import Session
from app.customers import service
from typing import List
from app.customers.schemas import CustomerUpdate
from app.users.schemas import UserResponse

router = APIRouter()

@router.get("/users/customers", response_model= List[CustomerUserResponse], tags = ["Customers"])
def get_customers(db: Session = Depends(get_db)):
    return service.get_customers(db)

@router.get("/users/customers/{customer_id}", response_model=CustomerUserResponse, tags = ["Customers"])
def get_customer_by_customer_id(customer_id: int, db: Session = Depends(get_db)):
    return service.get_customer_by_customer_id(db, customer_id)

@router.post("/users/customers/{user_id}", response_model=UserResponse, tags = ["Customers"])
def convert_user_to_customer(user_id: int, db: Session = Depends(get_db)):
    return service.convert_user_to_customer(db, user_id)

@router.patch("/users/customers/{customer_id}", response_model=CustomerUserResponse, tags = ["Customers"])
def update_customer(customer_id: int, updateCustomer: CustomerUpdate, db: Session = Depends(get_db)):
    return service.update_customer(db, customer_id, updateCustomer)