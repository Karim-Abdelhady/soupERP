from database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime
from datetime import datetime, timezone

class UnitOfMeasure(Base):
    __tablename__ = "unitmeasures"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    symbol: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    must_be_whole_number: Mapped[bool] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default= lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    created_by: Mapped[str] = mapped_column(nullable=False, default = "System")

    from_conversion = relationship("UnitConversion", foreign_keys="[UnitConversion.from_uom_id]", back_populates="from_unit")
    to_conversion = relationship("UnitConversion", foreign_keys="[UnitConversion.to_uom_id]", back_populates="to_unit")
    items: Mapped[list["Item"]] = relationship(back_populates="uom")
    
class UnitConversion(Base):
    __tablename__ = "unitconversions"

    id: Mapped[int] = mapped_column(primary_key=True)
    from_uom_id: Mapped[int] = mapped_column(ForeignKey("unitmeasures.id"), nullable=False)
    to_uom_id: Mapped[int] = mapped_column(ForeignKey("unitmeasures.id"), nullable=False)
    factor: Mapped[float] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc), onupdate= lambda:datetime.now(timezone.utc), nullable=False)

    from_unit = relationship("UnitOfMeasure", foreign_keys=[from_uom_id], back_populates="from_conversion")
    to_unit = relationship("UnitOfMeasure", foreign_keys=[to_uom_id], back_populates="to_conversion")