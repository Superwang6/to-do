from sqlalchemy.orm import Session
from src.model.user import User
from src.model.user_setting import UserSetting
from src.schema import UserUpdate
from src.util.auth import verify_password, hash_password
from typing import Dict, List, Optional


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> Dict:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar": user.avatar,
            "created_at": user.created_at
        }

    def update_user(self, user_id: int, user_update: UserUpdate) -> Dict:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Update fields
        if user_update.username:
            # Check if username already exists
            existing_user = self.db.query(User).filter(
                User.username == user_update.username,
                User.id != user_id
            ).first()
            if existing_user:
                raise ValueError("Username already exists")
            user.username = user_update.username
        
        if user_update.email:
            # Check if email already exists
            existing_user = self.db.query(User).filter(
                User.email == user_update.email,
                User.id != user_id
            ).first()
            if existing_user:
                raise ValueError("Email already exists")
            user.email = user_update.email
        
        self.db.commit()
        self.db.refresh(user)
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar": user.avatar
        }

    def update_avatar(self, user_id: int, avatar_url: str) -> Dict:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        user.avatar = avatar_url
        self.db.commit()
        self.db.refresh(user)
        
        return {
            "id": user.id,
            "username": user.username,
            "avatar": user.avatar
        }

    def change_password(self, user_id: int, current_password: str, new_password: str) -> None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")
        
        # Update password
        user.password_hash = hash_password(new_password)
        self.db.commit()

    def get_user_settings(self, user_id: int) -> Dict:
        settings = self.db.query(UserSetting).filter(UserSetting.user_id == user_id).all()
        return {setting.key: setting.value for setting in settings}

    def update_user_settings(self, user_id: int, settings: Dict) -> Dict:
        for key, value in settings.items():
            # Check if setting exists
            setting = self.db.query(UserSetting).filter(
                UserSetting.user_id == user_id,
                UserSetting.key == key
            ).first()
            
            if setting:
                setting.value = value
            else:
                # Create new setting
                new_setting = UserSetting(
                    user_id=user_id,
                    key=key,
                    value=value
                )
                self.db.add(new_setting)
        
        self.db.commit()
        return self.get_user_settings(user_id)