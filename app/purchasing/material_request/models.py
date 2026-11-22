from database.database import Base
from datetime import datetime, timezone
from app.purchasing.material_request.enums import MaterialRequestType, Status
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, Text, Numeric, String
from decimal import Decimal
from typing import List

class MaterialRequest(Base):
    __tablename__ = "materialrequests"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_number: Mapped[str] = mapped_column(unique=True, nullable=False)
    request_type: Mapped[MaterialRequestType] = mapped_column(Text, default = MaterialRequestType.PURCHASE, nullable=False)
    request_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc), nullable=False)
    required_by_date: Mapped[datetime] = mapped_column(DateTime(timezone.utc), nullable=False)
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(Text, default=Status.DRAFT.value, nullable=False)
    remarks: Mapped[str] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User") #type: ignore
    lines: Mapped[List["MaterialRequestLine"]] = relationship("MaterialRequestLine", back_populates="header", cascade="all, delete-orphan")

class MaterialRequestLine(Base):
    __tablename__ = "materialrequestlines"

    id: Mapped[int] = mapped_column(primary_key=True)

    material_request_id: Mapped[int] = mapped_column(ForeignKey("materialrequests.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(default = 0, nullable=False)
    uom_id: Mapped[int] = mapped_column(ForeignKey("unitmeasures.id"), nullable=False)
    conversion_factor: Mapped[Decimal] = mapped_column(Numeric(18,8), nullable=False)
    stock_quantity: Mapped[Decimal] = mapped_column(Numeric(18,4), nullable=False)
    available_quantity: Mapped[int] = mapped_column(default = 0, nullable=False)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=True)
    required_by_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    header: Mapped["MaterialRequest"] = relationship("MaterialRequest", back_populates="lines")
    item: Mapped["Item"] = relationship("Item") #type: ignore
    uom: Mapped["UnitOfMeasure"] = relationship("UnitOfMeasure") #type: ignore
    warehouse: Mapped["Warehouse"] = relationship("Warehouse") #type: ignore



