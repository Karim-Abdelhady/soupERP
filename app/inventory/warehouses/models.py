from database.database import Base
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime
from typing import Optional, List

class WarehouseType(Base):
    __tablename__ = "warehousetypes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique = True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    created_by: Mapped[str] = mapped_column(default = "System", nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default = True)
    warehouses: Mapped[List["Warehouse"]] = relationship(back_populates="warehouse_type")

class Warehouse(Base):
    __tablename__ = "warehouses"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    parent_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=True)
    company_id: Mapped[int] = mapped_column(nullable=False, default = 1)
    warehouse_type_id: Mapped[int] = mapped_column(ForeignKey("warehousetypes.id"), nullable=False)
    is_group: Mapped[bool] = mapped_column(nullable=False, default = False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default = True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc), onupdate= lambda: datetime.now(timezone.utc), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc), nullable=False)
    created_by: Mapped[str] = mapped_column(nullable=False, default = "System")

    warehouse_type: Mapped["WarehouseType"] = relationship(back_populates="warehouses")
    parent: Mapped[Optional["Warehouse"]] = relationship("Warehouse",remote_side=[id], back_populates="children")
    children: Mapped[List["Warehouse"]] = relationship("Warehouse", back_populates="parent")
    warehousestockbalance: Mapped[List["StockBalance"]] = relationship("StockBalance", back_populates="warehouse") #type: ignore
    warehousestockledger: Mapped[List["StockLedger"]] = relationship("StockLedger", back_populates="warehouse") #type: ignore
    source_stock_entry: Mapped[List["StockEntry"]] = relationship("StockEntry", foreign_keys="[StockEntry.source_warehouse_id]", back_populates="source_warehouse") #type: ignore
    target_stock_entry: Mapped[List["StockEntry"]] = relationship("StockEntry", foreign_keys="[StockEntry.target_warehouse_id]", back_populates="target_warehouse") #type: ignore
    source_stock_entry_line: Mapped[List["StockEntryLine"]] = relationship("StockEntryLine", foreign_keys="[StockEntryLine.source_warehouse_id]", back_populates="source_warehouse") #type: ignore
    target_stock_entry_line: Mapped[List["StockEntryLine"]] = relationship("StockEntryLine", foreign_keys="[StockEntryLine.target_warehouse_id]", back_populates="target_warehouse") #type: ignore
    stock_reconciliations: Mapped[List["StockReconciliation"]] = relationship("StockReconciliation", back_populates="warehouse") #type: ignore
    warehouse_stock_reservation: Mapped[List["StockReservation"]] = relationship("StockReservation", back_populates="warehouse") #type: ignore