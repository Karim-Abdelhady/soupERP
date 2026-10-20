from app.users import repository
from .schemas import UserCreate, UserUpdate
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from pydantic import EmailStr
from app.core.security import password_hash, generate_invite_token, create_token, hash_password, send_invitation_email, verify_password
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from app.core.config import settings
from fastapi import BackgroundTasks
from app.core.security import send_invitation_email
from app.core.security import create_token
from app.users.schemas import SetupPasswordRequest
import socket

def get_users(db: Session):
    return repository.get_users(db)

def get_user_by_user_id(db: Session, user_id: int):
    user =  repository.get_user_by_user_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "User with ID is not found")
    return user

def get_user_by_user_email(db: Session, email: EmailStr):
    user = repository.get_user_by_user_email(db, email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "User with Email is not found")
    return user

def update_user(db: Session, user_id: int, updateUser: UserUpdate):
    user = repository.get_user_by_user_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "User with ID is not found")
    update_data = updateUser.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    user.updated_at = datetime.now(timezone.utc)
    return repository.update_user(db, user)

def invite_user(db: Session, newUser: UserCreate, background_task: BackgroundTasks):
    normalized_email = newUser.email.lower().strip()
    exist_user = repository.get_user_by_user_email(db, normalized_email)
    if exist_user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Email is already registered")

    user_data = newUser.model_dump()
    user_data["email"] = normalized_email
    user_data["hashed_password"] = "~UNSET_INVITED_USER~"
    user_data["is_active"] = False
    

    db_user = repository.invite_user(db, user_data)
    token = generate_invite_token(db_user.email)
    background_task.add_task(send_invitation_email, db_user.email, token)
    return db_user

def setup_user_password(db: Session, payload: SetupPasswordRequest):
    try:
        data = jwt.decode(
            payload.token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        print("Decoded Token Data:", data)
        email: str = data.get("sub")
        action: str = data.get("action")

        if not email or action != "password_setup":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token target")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation link is invalid or expired")

    user = repository.get_user_by_user_email(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not found")
    if user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account is already activated.")

    user.hashed_password = hash_password(payload.new_password)
    user.is_active = True
    db.commit()
    db.refresh(user)
    return {"message": "Password successfully configurated, you can log in now."}



