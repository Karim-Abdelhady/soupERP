from fastapi import APIRouter, Depends
from database.database import get_db
from app.systemadministration.system_settings.schemas import SystemSettingResponse, SystemSettingHistoryResponse, SystemSettingCreate, SystemSettingUpdate
from app.systemadministration.system_settings import service
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()

@router.post("/system-settings/", response_model = SystemSettingResponse, tags = ["System Settings"])
def create_system_setting(new_setting: SystemSettingCreate, db: Session = Depends(get_db)):
    return service.create_system_setting(db, new_setting)

@router.patch("/system-settings/{setting_id}", response_model=SystemSettingResponse, tags = ["System Settings"])
def update_system_setting(setting_id: int, update_setting:SystemSettingUpdate, db: Session = Depends(get_db)):
    return service.update_system_setting(db, setting_id, update_setting)

@router.get("/system-settings/", response_model=List[SystemSettingResponse], tags = ["System Settings"])
def get_system_settings(db: Session = Depends(get_db)):
    return service.get_system_settings(db)

@router.get("/system-settings/{setting_id}", response_model=SystemSettingResponse, tags = ["System Settings"])
def get_setting_id(setting_id: int, db: Session = Depends(get_db)):
    return  service.get_setting_id(db, setting_id)

@router.get("/system-settings/history/", response_model=List[SystemSettingHistoryResponse], tags = ["System Settings"])
def get_system_setting_history(db: Session = Depends(get_db)):
    return service.get_system_setting_history(db)