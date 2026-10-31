from sqlalchemy.orm import Session
from app.systemadministration.sessions.models import UserSession
from datetime import datetime, timezone
from sqlalchemy import select
from app.systemadministration.sessions.enums import SessionStatus

def create_session(db: Session, session: UserSession):
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def update_session(db: Session, session: UserSession):
    db.commit()
    db.refresh(session)
    return session

def update_activity(db: Session, session: UserSession):
    session.last_activity_at = datetime.now(timezone.utc)
    db.commit()

def update_revoke(db: Session, session: UserSession):
    session.session_status = SessionStatus.INACTIVE
    session.revoked_at = datetime.now(timezone.utc)
    db.commit()

def get_sessions(db: Session):
    statement = select(UserSession)
    return db.scalars(statement).all()

def get_user_sessions(db: Session, user_id: int):
    statement = select(UserSession).where(UserSession.user_id == user_id)
    return db.scalar(statement)
