from database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey
from datetime import datetime, timezone

class SystemSettings(Base):
    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(unique=True,index=True, nullable=False)
    value: Mapped[str] = mapped_column(nullable=False)
    category: Mapped[str] = mapped_column(nullable=False)
    data_type: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    is_editable: Mapped[bool] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    updated_by: Mapped[str] = mapped_column(nullable=False, default = "System")
    history = relationship("SystemSettingsHistory", back_populates="setting", cascade="all, delete-orphan")

class SystemSettingsHistory(Base):
    __tablename__ = "system_settings_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    system_setting_id: Mapped[int] = mapped_column(ForeignKey("system_settings.id"), nullable=False) 
    key: Mapped[str] = mapped_column(index=True, nullable=False)
    old_value: Mapped[str] = mapped_column(nullable=False)
    new_value: Mapped[str] = mapped_column(nullable=False)
    default_key: Mapped[str] = mapped_column(nullable=False)
    changed_by: Mapped[str] = mapped_column(nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    reason: Mapped[str] = mapped_column(nullable=True)

    setting = relationship("SystemSettings", back_populates="history")