from sqlalchemy.orm import Session
from sqlalchemy import select
from app.systemadministration.users.models import User, UserType
from app.systemadministration.suppliers.models import Supplier
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status

def get_supplier_by_supplier_id(db: Session, supplier_id: int):
    statement = (
        select(User)
        .options(joinedload(User.supplier_profile))
        .where(User.id == supplier_id, User.user_type == UserType.SUPPLIER)
    )
    user = db.scalar(statement)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
        
    return {
        "user": user,
        "supplier_profile": user.supplier_profile
    }

def get_suppliers(db: Session):
    statement = (
            select(User)
            .options(joinedload(User.supplier_profile))
            .where(User.user_type == UserType.SUPPLIER)
        )
    users = db.scalars(statement).all()
    return [
        {
            "user": user,   
            "supplier_profile": user.supplier_profile
        }
        for user in users
    ]

def convert_user_to_supplier(db: Session, user: User):
    db.commit()
    db.refresh(user)
    return user

def update_supplier(db: Session, supplier: Supplier):
    db.commit()
    db.refresh(supplier)
    return supplier