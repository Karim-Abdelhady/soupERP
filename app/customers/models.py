from app.users.models import User
from database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    user: Mapped["User"] = relationship(back_populates="customer_profile")
    customer_category: Mapped[str] = mapped_column(nullable=False)
    trade_name: Mapped[str] = mapped_column(nullable=True)
    tin: Mapped[str] = mapped_column(nullable=True)
    vat: Mapped[str] = mapped_column(nullable=True)
    sales_tax_id: Mapped[str] = mapped_column(nullable=True)
    certificate_number: Mapped[str] = mapped_column(nullable=True)
    tax_exemption_status: Mapped[str] = mapped_column(nullable=True)