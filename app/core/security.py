from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from sqlalchemy.orm import Session
from app.core.config import settings
from database.database import get_db
from app.users.models import User
from app.users import repository as userRepository
from app.sessions.models import UserSession
from app.sessions.enums import SessionStatus
from app.sessions import repository as sessionRepository



password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=587,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password:str, hashed_password:str) -> bool:
    try:
        return password_hash.verify(plain_password,hashed_password)
    except Exception:
        return False


def create_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp":expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        settings.algorithm
    )
    return encoded_jwt

def generate_invite_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours = 24)

    to_encode = {
        "sub": email.lower().strip(),
        "exp": expire,
        "action": "password_setup",
    }

    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    except (InvalidTokenError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    try:
        parsed_user_id = int(user_id)
    except (InvalidTokenError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    user = userRepository.get_user_by_user_id(db, parsed_user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

    session = sessionRepository.get_user_sessions(db, parsed_user_id)
    if session is None or session.session_status != SessionStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session not found or inactive")

    if session.expires_at < datetime.now(timezone.utc):
        sessionRepository.update_revoke(db, session)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
    
    sessionRepository.update_activity(db, session)
    return user

async def send_invitation_email(email: str, token: str):
    test_url = getattr(settings, "TEST_URL", "http://127.0.0.1:8000")
    setup_link = f"{test_url}/setup-password?token={token}"
    content = f"""
    <h3>Welcome to soupERP!</h3>
    <p>You have been invited to set up your business account.</p>
    <p>Please click the link below to finalize your registration and choose a secure password:</p>
    <a href="{setup_link}" style="padding:10px 20px; background:#007bff; color:white; text-decoration:none; border-radius:5px;">Set Up Account</a>
    <p>This link will expire in 24 hours.</p>
    """

    message = MessageSchema(
        subject="Action Required: Setup Your soupERP Account",
        recipients=[email],
        body = content,
        subtype=MessageType.html
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)