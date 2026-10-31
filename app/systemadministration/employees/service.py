from sqlalchemy.orm import Session
from app.systemadministration.employees import repository
from fastapi import HTTPException, status
from app.systemadministration.users.models import User, UserType
from app.systemadministration.users import repository as userRepository
from app.systemadministration.employees.schemas import EmployeeUpdate
from app.systemadministration.employees.models import Employee
from datetime import datetime, timezone

def get_employes(db: Session):
    employees = repository.get_employees(db)
    if employees is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Please add an employee")
    return employees

def get_employee_by_employee_id(db: Session, employee_id: int):
    employee = repository.get_employee_by_employee_id(db, employee_id)
    if employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Employee is not found") 

def convert_user_to_employee(db: Session, user_id: int) -> User:
    user = userRepository.get_user_by_user_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "User is not found")

    user.user_type = UserType.EMPLOYEE
    user.updated_at = datetime.now(timezone.utc)
    return repository.convert_user_to_employee(db, user)

def update_employee(db: Session, user_id: int, updateEmployee: EmployeeUpdate):
    user = userRepository.get_user_by_user_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "User is not found")
    if user.user_type != UserType.EMPLOYEE:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is not an Employee")

    updated_data = updateEmployee.model_dump(exclude_unset=True)
    if not user.employee_profile:
        employee = Employee(employee_id=user.id, **updated_data)
        db.add(employee)
    else:
        for field, value in updated_data.items():
            setattr(user.employee_profile, field, value)
    user.updated_at = datetime.now(timezone.utc)
    updated_user = repository.update_employee(db, user)
    return {
        "user": updated_user,
        "employee_profile": updated_user.employee_profile,
    }