from database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, Text, String
from datetime import datetime, timezone
from app.purchasing.request_for_quotation.enums import Status, ResponseStatus
from typing import List

class RequestForQuotation(Base):
    __tablename__ = "requestquotations"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_number: Mapped[str] = mapped_column(unique=True, nullable=False)
    request_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc), nullable=False)
    required_by_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[Status] = mapped_column(String(50), default = Status.DRAFT.value, nullable=False)
    remarks: Mapped[str] = mapped_column(Text, nullable=True)

    lines: Mapped[List["RequestForQuotationLine"]] = relationship("RequestForQuotationLine", back_populates= "quotation", cascade="all, delete-orphan")
    rfq_supplier: Mapped[List["RequestForQuotationSupplier"]] = relationship("RequestForQuotationSupplier", back_populates="supplier_quotation", cascade="all, delete-orphan")

class RequestForQuotationLine(Base):
    __tablename__ = "requestquotationlines"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_for_quotation_id: Mapped[int] = mapped_column(ForeignKey("requestquotations.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(default = 0, nullable=False)
    uom_id: Mapped[int] = mapped_column(ForeignKey("unitmeasures.id"), nullable=False)
    required_by_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    quotation: Mapped["RequestForQuotation"] = relationship("RequestForQuotation", back_populates="lines")
    item: Mapped["Item"] = relationship("Item") #type: ignore
    uom: Mapped["UnitOfMeasure"] = relationship("UnitOfMeasure") #type: ignore

class RequestForQuotationSupplier(Base):
    __tablename__ = "requestquotationsuppliers"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_for_quotation_id: Mapped[int] = mapped_column(ForeignKey("requestquotations.id"), nullable=False)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default = None, nullable=True)
    response_status: Mapped[ResponseStatus] = mapped_column(String(50), default = ResponseStatus.PENDING.value, nullable=False)
    remarks: Mapped[str] = mapped_column(Text, nullable=True)
    declined: Mapped[bool] = mapped_column(default = False, nullable=False)

    supplier_quotation: Mapped["RequestForQuotation"] = relationship("RequestForQuotation", back_populates="rfq_supplier")
    supplier: Mapped["Supplier"] = relationship("Supplier") #type: ignore