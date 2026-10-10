from database.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from sqlalchemy import String, DateTime
from enum import Enum
from pydantic import EmailStr
from sqlalchemy.orm import relationship

class UserType(str, Enum):
    USER = "User"
    CUSTOMER = "Customer"
    SUPPLIER = "Supplier"
    EMPLOYEE = "Employee"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    #Authorization
    email: Mapped[EmailStr] = mapped_column(String(255), nullable=False, unique=True)
    username: Mapped[str] = mapped_column(nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False)
    user_type: Mapped[UserType] = mapped_column(default=UserType.USER ,nullable=False)
    #Profile
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    phone: Mapped[str] = mapped_column(nullable=True)
    gender: Mapped[bool] = mapped_column(nullable=True)
    bio: Mapped[str] = mapped_column(nullable=True)
    avatar_url: Mapped[str] = mapped_column(nullable=True)
    #Preferences
    language: Mapped[int] = mapped_column(nullable=False)
    time_zone: Mapped[str] = mapped_column(nullable=True, default = "UTC") #0 is Africa/Cairo
    currency: Mapped[str] = mapped_column(nullable=True, default = "USD") #0 is dollar
    #Audit and Security
    last_login_at: Mapped[datetime] =  mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    last_ip: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] =  mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    created_by: Mapped[str] = mapped_column(nullable=False)
    #ERP Linkages
    customer_profile = relationship("Customer",back_populates="user", uselist = False)
    employee_profile = relationship("Employee",back_populates="user", uselist = False)
    supplier_profile = relationship("Supplier",back_populates="user", uselist=False)


