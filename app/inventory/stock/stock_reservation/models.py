from database.database import Base
from datetime import datetime
from app.inventory.stock.stock_reservation.enums import ReservationStatus
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, String
from sqlalchemy.dialects.postgresql import JSON

class StockReservation(Base):
    __tablename__ = "stockreservations"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"),nullable=False)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=False)
    batch_id: Mapped[int] = mapped_column(ForeignKey("itembatches.id"), nullable=True)
    serial_id: Mapped[list[int]] = mapped_column(JSON, default = list, nullable=True)
    quantity: Mapped[int] = mapped_column(default = 0, nullable=False)
    source_document_type: Mapped[str] = mapped_column(nullable=True)
    source_document_id: Mapped[str] = mapped_column(nullable=True)
    source_line_id: Mapped[int] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), 
        default=ReservationStatus.ACTIVE.value, 
        nullable=False
    )
    reserved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    released_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    fulfilled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    item: Mapped["Item"] = relationship("Item", back_populates="item_stock_reservations") #type: ignore
    warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates="warehouse_stock_reservations") #type: ignore