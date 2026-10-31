from database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, ForeignKey

class Currency(Base):
    __tablename__ = "currencies"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(unique=True, nullable=False) #ISO code such as EGP
    name: Mapped[str] = mapped_column(unique=True, nullable=False) #Egyptian Pound
    symbol: Mapped[str] = mapped_column(nullable=True) #E£
    decimal_places: Mapped[float] = mapped_column(Float, nullable=False) 
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_system: Mapped[bool] = mapped_column(default=False, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    created_by: Mapped[str] = mapped_column(nullable=False, default = "System")

    from_rate = relationship("ExchangeRate", foreign_keys="[ExchangeRate.from_currency_id]", back_populates="from_currency")
    to_rate = relationship("ExchangeRate", foreign_keys="[ExchangeRate.to_currency_id]", back_populates="to_currency")

class ExchangeRate(Base):
    __tablename__ = "exchangerates"

    id: Mapped[int] = mapped_column(primary_key=True)
    from_currency_id: Mapped[int] = mapped_column(ForeignKey("currencies.id"), nullable=False)
    to_currency_id: Mapped[int] = mapped_column(ForeignKey("currencies.id"), nullable=False)
    rate: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[str] = mapped_column(nullable=False, default = "Other")
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_to: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    from_currency = relationship("Currency", foreign_keys=[from_currency_id], back_populates="from_rate")
    to_currency = relationship("Currency", foreign_keys=[to_currency_id], back_populates="to_rate")