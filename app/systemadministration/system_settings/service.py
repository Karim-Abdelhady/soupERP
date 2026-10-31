from sqlalchemy.orm import Session
from app.systemadministration.system_settings import repository
from fastapi import HTTPException, status
from app.systemadministration.system_settings.models import SystemSettingsHistory
from app.systemadministration.system_settings.schemas import SystemSettingCreate, SystemSettingUpdate
from datetime import datetime, timezone
from sqlalchemy import select

def create_system_setting(db: Session, newSetting: SystemSettingCreate):
    existing_setting = repository.get_setting_key(db, newSetting.key)
    if existing_setting is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Setting key already exists")

    new_data = newSetting.model_dump(exclude_unset=True)
    return repository.create_system_setting(db, new_data)

def update_system_setting(db: Session, setting_id: int, updateSetting: SystemSettingUpdate):
    setting = repository.get_setting_id(db, setting_id)
    if not setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Setting with ID is not found")
    if not setting.is_editable:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Setting is not editable")

    old_value = setting.value
    update_data = updateSetting.model_dump(exclude_unset=True)
    reason = update_data.pop("reason", None)
    new_value = update_data.get("value", old_value)

    for key, value in update_data.items():
        setattr(setting, key, value)
    setting.updated_at = datetime.now(timezone.utc)

    updated_setting = repository.update_system_setting(db, setting)

    statement = (
        select(SystemSettingsHistory).where(SystemSettingsHistory.system_setting_id == setting_id).order_by(SystemSettingsHistory.changed_at.asc())
    )
    first_history = db.scalar(statement)

    original_default_key = first_history.default_key if first_history else old_value

    if old_value != new_value:
        history_entry = SystemSettingsHistory(
            system_setting_id = updated_setting.id,
            key = updated_setting.key,
            old_value = old_value,
            new_value = new_value,
            default_key = original_default_key,
            changed_by = "System",
            changed_at = datetime.now(timezone.utc),
            reason = reason
        )
        repository.create_setting_history(db, history_entry)

    return updated_setting

def get_system_settings(db: Session):
    settings = repository.get_system_settings(db)
    if not settings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No setting found")
    return settings

def get_setting_id(db: Session, setting_id: int):
    setting = repository.get_setting_id(db, setting_id)
    if setting is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "No setting with ID found")
    return setting

def get_system_setting_history(db: Session):
    history = repository.get_system_setting_history(db)
    if not history:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "No setting history is found")
    return history
    
