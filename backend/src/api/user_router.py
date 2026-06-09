from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from src.database import get_db
from src.dependencies import get_current_user
from src.schema import ApiResponse, UserUpdate, ChangePassword, ok
from src.service.user_service import UserService
import os
from datetime import datetime

router = APIRouter(prefix="/api/user", tags=["user"])

UPLOAD_DIR = "uploads/avatars"

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/profile", response_model=ApiResponse)
def get_profile(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.get_user_by_id(current_user["id"])
    return ok(data=user)


@router.put("/profile", response_model=ApiResponse)
def update_profile(body: UserUpdate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    service = UserService(db)
    updated_user = service.update_user(current_user["id"], body)
    return ok(data=updated_user, message="Profile updated")


@router.post("/change-password", response_model=ApiResponse)
def change_password(body: ChangePassword, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    service = UserService(db)
    service.change_password(current_user["id"], body.current_password, body.new_password)
    return ok(message="Password changed successfully")


@router.post("/avatar", response_model=ApiResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{current_user['id']}_{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Update user avatar
    service = UserService(db)
    avatar_url = f"/uploads/avatars/{filename}"
    updated_user = service.update_avatar(current_user["id"], avatar_url)
    
    return ok(data={"avatar": avatar_url}, message="Avatar uploaded")


@router.get("/settings", response_model=ApiResponse)
def get_settings(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    service = UserService(db)
    settings = service.get_user_settings(current_user["id"])
    return ok(data=settings)


@router.put("/settings", response_model=ApiResponse)
def update_settings(
    settings: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = UserService(db)
    updated_settings = service.update_user_settings(current_user["id"], settings)
    return ok(data=updated_settings, message="Settings updated")