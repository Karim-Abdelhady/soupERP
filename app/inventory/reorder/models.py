from database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime
from datetime import datetime, timezone

class ItemReorderRule(Base):
    __tablename__ = "reorderrules"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=False)
    reorder_level: Mapped[int] = mapped_column(default = 0, nullable=False)
    safety_stock_level: Mapped[int] = mapped_column(nullable=False)
    reorder_qty: Mapped[int] = mapped_column(nullable=False) #minimum_order_qty
    maximum_order_qty: Mapped[int] = mapped_column(nullable=True)
    lead_time_days: Mapped[int] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default= lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc), onupdate= lambda: datetime.now(timezone.utc), nullable=False)

    items: Mapped["Item"] = relationship("Item", back_populates="item_reorder_rule") #type: ignore
    warehouses: Mapped["Warehouse"] = relationship("Warehouse", back_populates="warehouse_reorder_rule") #type: ignore
