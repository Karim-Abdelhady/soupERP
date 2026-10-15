from fastapi import APIRouter, Depends
from database.database import get_db
from typing import List
from app.employees.schemas import EmployeeUserResponse
from app.employees import service
from sqlalchemy.orm import Session
from app.users.schemas import UserResponse
from app.employees.schemas import EmployeeUpdate
from app.auth.permissions import require_permission, PermissionCatalog
from app.users.models import User

router = APIRouter()

@router.get("/users/employees", response_model=List[EmployeeUserResponse], tags = ["Employees"])
def get_employees(db: Session = Depends(get_db), current_user: User = Depends(require_permission(PermissionCatalog.EMPLOYEE_READ))):
    return service.get_employes(db)

@router.get("/users/employees/{employee_id}", response_model=EmployeeUserResponse, tags = ["Employees"])
def get_employee_by_employee_id(employee_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission(PermissionCatalog.EMPLOYEE_READ))):
    return service.get_employee_by_employee_id(db, employee_id)

@router.post("/users/employees/{user_id}", response_model=UserResponse, tags = ["Employees"])
def convert_user_to_employee(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission(PermissionCatalog.EMPLOYEE_CREATE))):
    return service.convert_user_to_employee(db, user_id)

@router.patch("/users/employees/{employee_id}", response_model=EmployeeUserResponse, tags = ["Employees"])
def update_employee(employee_id: int, updateEmployee: EmployeeUpdate, db:Session=Depends(get_db), current_user: User = Depends(require_permission(PermissionCatalog.EMPLOYEE_UPDATE))):
    return service.update_employee(db, employee_id, updateEmployee)