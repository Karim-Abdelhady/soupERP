from sqlalchemy.orm import Session
from app.systemadministration.customers import repository
from fastapi import HTTPException, status
from app.systemadministration.users.models import UserType
from app.systemadministration.customers.models import Customer
from app.systemadministration.customers.schemas import CustomerUpdate
from app.systemadministration.users.models import User
from app.systemadministration.users import repository as userRepository
from datetime import datetime, timezone

def get_customer_by_customer_id(db: Session, customer_id:int):
    customer = repository.get_customer_by_customer_id(db, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Customer is not found")
    return customer

def get_customers(db: Session):
    customers = repository.get_customers(db)
    if customers is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Please make a customer first")
    return customers

def convert_user_to_customer(db: Session, user_id: int) -> User:
    user = userRepository.get_user_by_user_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "User is not found")
    user.user_type = UserType.CUSTOMER
    user.updated_at = datetime.now(timezone.utc)
    return repository.convert_user_to_customer(db, user)

def update_customer(db: Session, user_id: int, updateCustomer: CustomerUpdate):
    user = userRepository.get_user_by_user_id(db, user_id)
    if user is None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail = "User is not found")
    if user.user_type != UserType.CUSTOMER:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is not a customer")

    updated_data = updateCustomer.model_dump(exclude_unset=True)
    if not user.customer_profile:
        customer = Customer(customer_id=user.id, **updated_data)
        db.add(customer)
    else:
        for field, value in updated_data.items():
            setattr(user.customer_profile, field, value)
    user.updated_at = datetime.now(timezone.utc)
    updated_user = repository.update_user(db, user)

    return {
        "user": updated_user,
        "customer_profile": updated_user.customer_profile,
    }