from pydantic import BaseModel
from app.systemadministration.sessions.enums import SessionStatus
from datetime import datetime

class SessionCreate(BaseModel):
    session_status: SessionStatus
    expires_at: datetime
    ip_address: str
    browser_name: str
    device_name: str


class SessionResponse(BaseModel):
    id: int
    session_status: SessionStatus
    created_at: datetime
    last_activity_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None
    ip_address: str
    browser_name: str
    device_name: str

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"