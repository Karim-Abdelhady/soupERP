from pydantic import BaseModel
from app.users.schemas import UserResponse
from datetime import date
from app.employees.enums import EmployeeStatus, EmployeeClassification, EmployeeSite, PayFrequently, PayRateType

class EmployeeUpdate(BaseModel):
    hire_date: date | None = None
    rehire_date: date | None = None
    termination_date: date | None = None
    employee_status: EmployeeStatus | None = None
    employee_classification: EmployeeClassification | None = None
    employee_site: EmployeeSite | None = None
    position_title: str | None = None
    department: str | None = None
    supervisor_id: int | None = None
    supervisor_name: str | None = None
    manager_name: str | None = None
    assigned_office: str | None = None
    warehouse_id: str | None = None
    remote_designation: str | None = None
    pay_frequently: PayFrequently | None = None
    pay_rate_type: PayRateType | None = None
    base_pay_amount: int | None = None
    direct_deposit_banking_details: str | None = None
    tax_withholding_status: str | None = None

class EmployeeDetailsResponse(BaseModel):
    id: int
    hire_date: date
    rehire_date: date
    termination_date: date
    employee_status: EmployeeStatus
    employee_classification: EmployeeClassification
    employee_site: EmployeeSite
    position_title: str
    department: str
    supervisor_id: int
    supervisor_name: str
    manager_name: str
    assigned_office: str
    warehouse_id: str
    remote_designation: str
    pay_frequently: PayFrequently
    pay_rate_type: PayRateType
    base_pay_amount: int
    direct_deposit_banking_details: str
    tax_withholding_status: str

class EmployeeUserResponse(BaseModel):
    user: UserResponse
    employee_profile: EmployeeDetailsResponse | None = None

    class Config:
        from_attributes = True