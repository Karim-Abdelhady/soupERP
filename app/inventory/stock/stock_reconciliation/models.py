from database.database import Base
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, Text
from app.inventory.stock.stock_reconciliation.enums import Status
from typing import List

class StockReconciliation(Base):
    __tablename__ = "stockreconciliations"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_number: Mapped[str] = mapped_column(unique = True, nullable=False)
    status: Mapped[Status] = mapped_column(default = Status.DRAFT, nullable=False)
    posting_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc), nullable=False)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable = True)
    created_by: Mapped[str] = mapped_column(default = "System", nullable=False)
    submitted_by: Mapped[str] = mapped_column(default = "System", nullable= True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    canceled_by: Mapped[str] = mapped_column(default = "System", nullable=True)
    canceled_at: Mapped[datetime] = mapped_column(DateTime(True), nullable=True)
    warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates="stock_reconciliations") #type: ignore
    stock_reconciliation_lines: Mapped[List["StockReconciliationLine"]] = relationship("StockReconciliationLine", back_populates="stock_reconciliation")

class StockReconciliationLine(Base):
    __tablename__ = "stockreconciliationlines"

    id: Mapped[int] = mapped_column(primary_key=True)
    reconciliation_id: Mapped[int] = mapped_column(ForeignKey("stockreconciliations.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)
    expected_qty: Mapped[int] = mapped_column(default = 0, nullable=False)
    counted_qty: Mapped[int] = mapped_column(default = 0, nullable=False)
    difference_qty: Mapped[int] = mapped_column(default = 0, nullable=False)
    uom_id: Mapped[int] = mapped_column(ForeignKey("unitmeasures.id"), nullable=False)
    conversion_factor: Mapped[int] = mapped_column(default = 1, nullable=False)
    valuation_rate: Mapped[int] = mapped_column(default = 0, nullable=False)

    stock_reconciliation: Mapped["StockReconciliation"] = relationship("StockReconciliation", back_populates="stock_reconciliation_lines")
    item: Mapped["Item"] = relationship("Item", back_populates="stock_reconciliation_lines") #type: ignore
    uom: Mapped["UnitOfMeasure"] = relationship("UnitOfMeasure", back_populates="stock_reconciliation_lines") #type: ignore
