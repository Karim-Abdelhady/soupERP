from database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime
from datetime import datetime, timezone

class StockBalance(Base):
    __tablename__ = "stockbalances"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=False)
    actual_qty: Mapped[int] = mapped_column(nullable=False, default = 0)
    reserved_qty: Mapped[int] = mapped_column(nullable=False, default = 0)
    available_qty: Mapped[int] = mapped_column(nullable=False, default = 0)
    valuation_rate: Mapped[float] = mapped_column(nullable=False, default = 0.0)
    stock_value: Mapped[float] = mapped_column(nullable=False, default = 0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc), nullable=False)

    item: Mapped["Item"] = relationship(back_populates="itemstockbalance") #type: ignore
    warehouse: Mapped["Warehouse"] = relationship(back_populates="warehousestockbalance") #type: ignore