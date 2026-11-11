from database.database import Base
from datetime import datetime,timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, Integer, Column, Table
from app.inventory.tracking_items.enums import BatchStatus, SerialStatus
from typing import List

stock_ledger_serial_map = Table(
    "stock_ledger_serial_map",
    Base.metadata,
    Column("stock_ledger_id", Integer, ForeignKey("stockledgers.id"), primary_key=True),
    Column("serial_number_id", Integer, ForeignKey("serialnumbers.id"), primary_key=True)
)

class ItemBatch(Base):
    __tablename__ = "itembatches"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)
    batch_number: Mapped[str] = mapped_column(unique=True, nullable=False)
    manufacture_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    expiry_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[BatchStatus] = mapped_column(default=BatchStatus.ACTIVE, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc))

    items: Mapped["Item"] = relationship("Item", back_populates="item_batch_track") #type: ignore
    serial_numbers: Mapped[List["SerialNumber"]] = relationship("SerialNumber", back_populates="item_batches")

class SerialNumber(Base):
    __tablename__ = "serialnumbers"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)
    serial_number: Mapped[str] = mapped_column(unique=True, nullable=False)
    status: Mapped[SerialStatus] = mapped_column(default = SerialStatus.INSTOCK, nullable=False)
    current_warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("itembatches.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc))

    items: Mapped["Item"] = relationship("Item", back_populates="item_serial_number") #type: ignore
    warehouses: Mapped["Warehouse"] = relationship("Warehouse", back_populates="warehouse_serial_number") #type: ignore
    item_batches: Mapped["ItemBatch"] = relationship("ItemBatch", back_populates="serial_numbers")