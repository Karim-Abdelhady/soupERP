from fastapi import APIRouter, Depends, Request
from app.sessions.schemas import TokenResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database.database import get_db
from app.sessions import service
from app.users.models import User
from app.core.security import get_current_user
from app.sessions.schemas import SessionResponse
from typing import List

router = APIRouter()

@router.post("/login", response_model=TokenResponse, tags = ["Authentication"])
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    ip_address = request.client.host if request.client else "Unknown"
    user_agent = request.headers.get("user-agent", "System")
    return service.verify_session(db, form_data.username, form_data.password, ip_address, user_agent)

@router.post("/logout", tags = ["Authentication"])
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.terminate_session(db, user_id=current_user.id)

@router.get("/sessions", response_model=List[SessionResponse], tags = ["Sessions"])
def get_sessions(db: Session = Depends(get_db)):
    return service.get_sessions(db)

@router.get("/users/{user_id}/sessions", response_model=SessionResponse, tags = ["Sessions"])
def get_user_sessions(user_id: int, db: Session = Depends(get_db)):
    return service.get_user_sessions(db, user_id)

@router.delete("/users/{user_id}/sessions", response_model=SessionResponse, tags = ["Sessions"])
def terminate_session(user_id: int, db: Session = Depends(get_db)):
    return service.terminate_session(db, user_id)