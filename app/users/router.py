from app.users import service
from database.database import get_db
from fastapi import APIRouter, Depends
from typing import List
from .schemas import UserResponse, UserCreate, UserUpdate
from sqlalchemy.orm import Session
from pydantic import EmailStr
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import status
from fastapi import BackgroundTasks
from .schemas import SetupPasswordRequest
from fastapi.responses import HTMLResponse
from app.users.models import User
from app.auth.permissions import require_permission, PermissionCatalog
from app.core.security import get_current_user

router = APIRouter()

@router.get("/users", response_model=List[UserResponse], tags = ["Users"])
def get_users(db: Session = Depends(get_db), current_user: User = Depends(require_permission(PermissionCatalog.USER_READ))):
    return service.get_users(db)

@router.get("/users/me", response_model=UserResponse, tags = ["Users"])
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user 

@router.get("/users/email/{email}", response_model=UserResponse, tags = ["Users"])
def get_user_by_email(email: EmailStr, db: Session = Depends(get_db), current_user: User = Depends(require_permission(PermissionCatalog.USER_READ))):
    return service.get_user_by_user_email(db, email)

@router.get("/users/{user_id}", response_model=UserResponse, tags = ["Users"])
def get_user_by_user_id(user_id:int, db:Session = Depends(get_db), current_user: User = Depends(require_permission(PermissionCatalog.USER_READ))):
    return service.get_user_by_user_id(db, user_id)

@router.post("/users", response_model=UserResponse, tags = ["Users"])
def invite_user(newUser: UserCreate,background_task: BackgroundTasks ,db: Session = Depends(get_db)):
    return service.invite_user(db, newUser, background_task)

@router.patch("/users/{user_id}", response_model=UserResponse, tags = ["Users"])
def update_user(user_id: int, updateUser: UserUpdate, db:Session = Depends(get_db), current_user: User = Depends(require_permission(PermissionCatalog.USER_UPDATE))):
    return service.update_user(db, user_id, updateUser)

@router.post("/users/setup-password", tags=["Users"])   
def setup_password(data: SetupPasswordRequest, db: Session = Depends(get_db)):
    return service.setup_user_password(db, data)

@router.get("/setup-password", response_class=HTMLResponse, tags=["Users"])  #AI-Generated
def setup_password_page(token: str):
    return f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Setup Password - soupERP</title>
            <style>
                body {{ font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background-color: #f4f4f9; }}
                .card {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 320px; }}
                input {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }}
                button {{ width: 100%; padding: 10px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }}
                button:hover {{ background-color: #0056b3; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>Set Your Password</h2>
                <form id="passwordForm">
                    <input type="hidden" id="token" value="{token}" />
                    <label for="password">New Password</label>
                    <input type="password" id="password" required placeholder="Enter new password" />
                    <button type="submit">Submit</button>
                </form>
                <p id="msg" style="margin-top: 15px;"></p>
            </div>
            <script>
                document.getElementById('passwordForm').addEventListener('submit', async (e) => {{
                    e.preventDefault();
                    const token = document.getElementById('token').value;
                    const password = document.getElementById('password').value;
                    const response = await fetch('/users/setup-password', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ token: token, new_password: password }})
                    }});
                    const resData = await response.json();
                    if (response.ok) {{
                        document.getElementById('msg').style.color = 'green';
                        document.getElementById('msg').innerText = 'Password set successfully! You can now log in.';
                    }} else {{
                        document.getElementById('msg').style.color = 'red';
                        document.getElementById('msg').innerText = resData.detail || 'An error occurred.';
                    }}
                }});
            </script>
        </body>
    </html>
    """