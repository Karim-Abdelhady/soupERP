from database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime
from datetime import datetime, timezone


class StockLedger(Base):
    __tablename__ = "stockledgers"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=False)
    posting_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc), nullable=False)
    quantity_delta: Mapped[int] = mapped_column(nullable=False, default = 0)
    qty_after_transaction: Mapped[int] = mapped_column(nullable=False, default = 0)
    incoming_rate: Mapped[float] = mapped_column(nullable=False, default = 0.0)
    outgoing_rate: Mapped[float] = mapped_column(nullable=False, default = 0.0)
    stock_value_delta: Mapped[float] = mapped_column(nullable=False, default = 0.0)
    stock_value_after_transaction: Mapped[float] = mapped_column(nullable=False, default = 0.0)
    voucher_type: Mapped[str] = mapped_column(nullable=False, default = "Sales Invoice")
    voucher_id: Mapped[str] = mapped_column(nullable=False, default = "SINV-001")
    voucher_line_id: Mapped[str] = mapped_column(nullable=False, default = "SINV-001-L12")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc), nullable=False)

    item: Mapped["Item"] = relationship(back_populates="itemstockledger") #type: ignore
    warehouse: Mapped["Warehouse"] = relationship(back_populates="warehousestockledger") #type: ignore