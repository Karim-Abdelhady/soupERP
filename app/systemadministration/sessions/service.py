from sqlalchemy.orm import Session
from app.systemadministration.sessions import repository
from app.systemadministration.users import repository as userRepository
from app.systemadministration.sessions.enums import SessionStatus
from app.core.security import verify_password, create_token
from fastapi import HTTPException, status
from datetime import datetime, timezone, timedelta
from app.systemadministration.sessions.models import UserSession

def verify_session(db: Session, user_email: str, password:str, ip_address: str, browser: str):
    user = userRepository.get_user_by_user_email(db, user_email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid Credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "User is not active")

    session_duration = timedelta(hours = 8)
    expires_at = datetime.now(timezone.utc) + session_duration

    existing_session = repository.get_user_sessions(db, user.id)
    if existing_session:
        existing_session.session_status = SessionStatus.ACTIVE
        existing_session.expires_at = expires_at
        existing_session.last_activity_at = datetime.now(timezone.utc)
        existing_session.revoked_at = None
        existing_session.ip_address = ip_address
        existing_session.browser_name = browser
        session = repository.update_session(db, existing_session)
    else:
        new_session = UserSession(
            user_id = user.id,
            session_status = SessionStatus.ACTIVE,
            created_at = datetime.now(timezone.utc),
            last_activity_at = datetime.now(timezone.utc),
            expires_at = expires_at,
            ip_address = ip_address,
            browser_name = browser,
            device_name="Web"
        )
        session = repository.create_session(db, new_session)

    access_token = create_token(data={"sub": str(user.id)}, expires_delta=session_duration)
    return {"access_token": access_token, "token_type": "bearer"}

def terminate_session(db: Session, user_id: int):
    session = repository.get_user_sessions(db, user_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Session is not found")
    repository.update_revoke(db, session)
    return session

def get_sessions(db: Session):
    sessions = repository.get_sessions(db)
    if not sessions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "No sessiosn found")
    return sessions

def get_user_sessions(db: Session, user_id: int):
    session = repository.get_user_sessions(db, user_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "No sessions found for user")
    return session