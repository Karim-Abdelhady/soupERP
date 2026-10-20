from sqlalchemy import select
from sqlalchemy.orm import Session
from app.system_settings.models import SystemSettings, SystemSettingsHistory
from app.system_settings.schemas import SystemSettingCreate
from datetime import datetime, timezone

def create_system_setting(db: Session, setting: SystemSettingCreate):
    db_data = SystemSettings(**setting)
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

def update_system_setting(db: Session, setting: SystemSettings):
    db.commit()
    db.refresh(setting)
    return setting

def get_system_settings(db: Session):
    statement = select(SystemSettings)
    return db.scalars(statement).all()

def get_setting_key(db: Session, setting_key: str):
    statement = select(SystemSettings).where(SystemSettings.key == setting_key)
    return db.scalar(statement)

def get_setting_id(db: Session, setting_id: int):
    statement = select(SystemSettings).where(SystemSettings.id == setting_id)
    return db.scalar(statement)

def get_system_setting_history(db: Session):
    statement = select(SystemSettingsHistory)
    return db.scalars(statement).all()

def create_setting_history(db: Session, history_data: SystemSettingHistory):
    db.add(history_data)
    db.commit()
    db.refresh(history_data)
    return history_data