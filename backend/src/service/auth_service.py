from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.model.user import User
from src.util.auth import create_access_token, hash_password, verify_password


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, username: str, password: str) -> dict:
        existing = self.db.query(User).filter(User.username == username).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")
        user = User(username=username, password_hash=hash_password(password))
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        token = create_access_token({"user_id": user.id, "username": user.username})
        return {"token": token, "user_id": user.id, "username": user.username}

    def login(self, username: str, password: str) -> dict:
        user = self.db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        token = create_access_token({"user_id": user.id, "username": user.username})
        return {"token": token, "user_id": user.id, "username": user.username}
