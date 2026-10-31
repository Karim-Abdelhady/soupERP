from sqlalchemy.orm import joinedload, Session
from sqlalchemy import select
from app.systemadministration.users.models import User, UserType
from fastapi import HTTPException, status
from app.systemadministration.employees.models import Employee

def get_employees(db: Session):
    statement = (
        select(User)
        .options(joinedload(User.employee_profile))
        .where(User.user_type == UserType.EMPLOYEE)
    )
    users = db.scalars(statement).all()

    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "No Employees")

    return [{
        "user": user,
        "employee_profile": user.employee_profile
    }
    for user in users
    ]

def get_employee_by_employee_id(db: Session, employee_id: int):
    statement = (
        select(User)
        .options(joinedload(User.employee_profile))
        .where(User.id == employee_id, User.user_type == UserType.EMPLOYEE)
    )
    user = db.scalar(statement)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    return {
        "user": user,
        "employee_profile": user.employee_profile
    }

def convert_user_to_employee(db: Session, user: User):
    db.commit()
    db.refresh(user)
    return user

def update_employee(db: Session, employee: Employee):
    db.commit()
    db.refresh(employee)
    return employee