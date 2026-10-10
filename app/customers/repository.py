from sqlalchemy import select
from app.users.models import User, UserType
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.customers.models import Customer

def get_customer_by_customer_id(db: Session, customer_id: int):
    statement = (
        select(User)
        .options(joinedload(User.customer_profile))
        .where(User.id == customer_id, User.user_type == UserType.CUSTOMER)
    )
    user = db.scalar(statement)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not found")

    return {
        "user": user,
        "customer_profile": user.customer_profile
    }

def get_customers(db: Session):
    statement = (
        select(User)
        .options(joinedload(User.customer_profile))
        .where(User.user_type == UserType.CUSTOMER)
    )

    users = db.scalars(statement).all()

    return [
        {
        "user": user,
        "customer_profile": user.customer_profile,
    }
        for user in users
    ]

def convert_user_to_customer(db: Session, user: User):
    db.commit()
    db.refresh(user)
    return user

def update_customer(db: Session, updatecustomer: Customer):
    db.commit()
    db.refresh(updatecustomer)
    return updatecustomer