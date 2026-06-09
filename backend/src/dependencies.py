from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.model.user import User
from src.util.auth import decode_access_token


def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization[len("Bearer "):]
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return {"user_id": user.id, "username": user.username}
