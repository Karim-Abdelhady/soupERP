from database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    user = relationship("User", back_populates="supplier_profile")
    supplier_category: Mapped[str] = mapped_column(nullable=False)
    tax_id: Mapped[str] = mapped_column(nullable=True)
    ein: Mapped[str] = mapped_column(nullable=True)
    vat: Mapped[str] = mapped_column(nullable=True)
    diversity_status: Mapped[str] = mapped_column(nullable=True)
    vendor_tier: Mapped[str] = mapped_column(nullable=True)