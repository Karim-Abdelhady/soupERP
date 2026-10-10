from app.users.models import User
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import EmailStr
from .schemas import UserCreate

def invite_user(db: Session, newuser: UserCreate):
    db_user = User(**newuser)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session):
    return db.execute(select(User)).scalars().all()

def get_user_by_user_id(db: Session, user_id: User):
    return db.get(User, user_id)

def get_user_by_user_email(db: Session, email: EmailStr):
    statement = select(User).where(User.email == email)
    return db.scalar(statement)

def update_user(db: Session, user: User):
    db.commit()
    db.refresh(user)
    return user

