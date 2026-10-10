from app.users.models import User
from database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Date
from enum import Enum
from datetime import date

class EmployeeStatus(str, Enum):
    ACTIVE = "Active"
    ONLEAVE = "On leave"
    TERMINATED = "Terminated"
    SUSPENDED = "Suspended"

class EmployeeClassification(str, Enum):
    FULLTIME = "Full-Time"
    PARTTIME = "Part-Time"
    CONTRACTOR = "Contractor"
    INTERN = "Intern"
    TEMPORARY = "Temporary"

class EmployeeSite(str, Enum):
    ONSITE = "On-Site"
    REMOTE = "Remotely"
    HYBRID = "Hybrid"

class PayFrequently(str, Enum):
    WEEKLY = "Weekly"
    BIWEEKLY = "Bi-Weekly"
    SEMIMONTHLY = "Semi-Monthly"
    MONTHLY = "Monthly"

class PayRateType(str, Enum):
    SALARIED = "Salaried"
    HOURLY = "Hourly"
    PIECEWORK = "Piecework"
    COMMISSION = "Commission"

class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    user: Mapped["User"] = relationship(back_populates="employee_profile")
    hire_date: Mapped[date] = mapped_column(Date, nullable=True)
    rehire_date: Mapped[date] = mapped_column(Date, nullable=True)
    termination_date: Mapped[date] = mapped_column(Date, nullable=True)
    employee_status: Mapped[EmployeeStatus] = mapped_column(default=EmployeeStatus.ACTIVE, nullable = False)
    employee_classification: Mapped[EmployeeClassification] = mapped_column(default=EmployeeClassification.FULLTIME, nullable=False)
    employee_site: Mapped[EmployeeSite] = mapped_column(default = EmployeeSite.ONSITE, nullable=False)
    position_title: Mapped[str] = mapped_column(nullable=False)
    department: Mapped[str] = mapped_column(nullable=False)
    supervisor_id: Mapped[int] = mapped_column(nullable=True)
    supervisor_name: Mapped[str] = mapped_column(nullable=True)
    manager_name: Mapped[str] = mapped_column(nullable=True)
    assigned_office: Mapped[str] = mapped_column(nullable=True)
    warehouse_id: Mapped[str] = mapped_column(nullable=True)
    remote_designation: Mapped[str] = mapped_column(nullable=True)
    pay_frequently: Mapped[PayFrequently] = mapped_column(default=PayFrequently.MONTHLY, nullable=False)
    pay_rate_type: Mapped[PayRateType] = mapped_column(default = PayRateType.SALARIED, nullable=True)
    base_pay_amount: Mapped[int] = mapped_column(nullable=True)
    direct_deposit_banking_details: Mapped[str] = mapped_column(nullable=True)
    tax_withholding_status: Mapped[str] = mapped_column(nullable=True)