from database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, Text
from app.inventory.stock.stock_entry.enums import Purpose, Status
from datetime import datetime, timezone
from typing import List

class StockEntry(Base):
    __tablename__ = "stockentries"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_number: Mapped[str] = mapped_column(unique=True, default = "STE-2026-001", nullable=False)
    purpose: Mapped[Purpose] = mapped_column(default = Purpose.TRANSFER, nullable=False)
    status: Mapped[Status] = mapped_column(default = Status.DRAFT, nullable=False)
    source_warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=True)
    target_warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=True)
    remarks: Mapped[str] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(default = "System", nullable=False)
    submitted_by: Mapped[str] = mapped_column(default = "System", nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc), nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_by: Mapped[str] = mapped_column(default = "System", nullable=True)
    cancelled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    source_warehouse = relationship("Warehouse", foreign_keys=[source_warehouse_id], back_populates="source_stock_entry")
    target_warehouse = relationship("Warehouse", foreign_keys=[target_warehouse_id], back_populates="target_stock_entry")
    stock_entry_lines: Mapped[List["StockEntryLine"]] = relationship("StockEntryLine", back_populates="stock_entry")
    
class StockEntryLine(Base): #rows
    __tablename__ = "stockentryrows"

    id: Mapped[int] = mapped_column(primary_key=True)
    stock_entry_id: Mapped[int] = mapped_column(ForeignKey("stockentries.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)
    source_warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=True)
    target_warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=True)
    quantity: Mapped[int] = mapped_column(default = 0, nullable=False)
    uom_id: Mapped[int] = mapped_column(ForeignKey("unitmeasures.id"), nullable=False)
    conversion_factor: Mapped[int] = mapped_column(default = 1, nullable=False)
    stock_quantity: Mapped[int] = mapped_column(default = 0, nullable=False)
    unit_cost: Mapped[int] = mapped_column(default = 1, nullable=False)
    line_amount: Mapped[int] = mapped_column(default = 1, nullable=False)

    stock_entry: Mapped["StockEntry"] = relationship("StockEntry", back_populates="stock_entry_lines")
    items: Mapped["Item"] = relationship("Item", back_populates="stock_entry_line") #type: ignore
    source_warehouse = relationship("Warehouse", foreign_keys=[source_warehouse_id], back_populates="source_stock_entry_line")
    target_warehouse = relationship("Warehouse", foreign_keys=[target_warehouse_id], back_populates="target_stock_entry_line")
    uom: Mapped["UnitOfMeasure"] = relationship("UnitOfMeasure", back_populates="stock_entry_line") #type: ignore