from database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime
from datetime import datetime, timezone
from typing import List

class ItemGroup(Base):
    __tablename__ = "itemgroups"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_code: Mapped[str] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by: Mapped[str] = mapped_column(nullable=False, default = "System")
    is_active: Mapped[bool] = mapped_column(nullable=False, default = True)

    items: Mapped[list["Item"]] = relationship(back_populates="group")


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_code: Mapped[str] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    item_type: Mapped[str] = mapped_column(nullable=True)
    stock_uom_id: Mapped[int] = mapped_column(ForeignKey("unitmeasures.id"), nullable=False)
    item_group_id: Mapped[int] = mapped_column(ForeignKey("itemgroups.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default = True)
    is_batch_tracked: Mapped[bool] = mapped_column(nullable=False, default = False)
    is_serial_tracked: Mapped[bool] = mapped_column(nullable=False, default = False)
    has_expiry_date: Mapped[bool] = mapped_column(nullable=False, default = False)
    valuation_method: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default= lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc), onupdate= lambda: datetime.now(timezone.utc))
    created_by: Mapped[str] = mapped_column(nullable=False, default = "System")

    group: Mapped["ItemGroup"] = relationship(back_populates="items")
    uom: Mapped["UnitOfMeasure"] = relationship(back_populates="items") #type: ignore
    itemstockbalance: Mapped[List["StockBalance"]] = relationship("StockBalance", back_populates="item") #type:ignore
    itemstockledger: Mapped[List["StockLedger"]] = relationship("StockLedger", back_populates="item") #type: ignore
    stock_entry_line: Mapped[List["StockEntryLine"]] = relationship("StockEntryLine", back_populates="items") #type: ignore
    stock_reconciliation_lines: Mapped[List["StockReconciliationLine"]] = relationship("StockReconciliationLine", back_populates="item") #type: ignore
    item_stock_reservations: Mapped[List["StockReservation"]] = relationship("StockReservation", back_populates="item") #type: ignore
    item_batch_track: Mapped[List["ItemBatch"]] = relationship("ItemBatch", back_populates="items") #type: ignore
    item_serial_number: Mapped[List["SerialNumber"]] = relationship("SerialNumber", back_populates="items") #type: ignore