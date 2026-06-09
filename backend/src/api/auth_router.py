from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.dependencies import get_current_user
from src.schema import ApiResponse, AuthLogin, AuthRegister, ok
from src.service.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=ApiResponse)
def register(body: AuthRegister, db: Session = Depends(get_db)):
    service = AuthService(db)
    result = service.register(body.username, body.password)
    return ok(data=result, message="registered")


@router.post("/login", response_model=ApiResponse)
def login(body: AuthLogin, db: Session = Depends(get_db)):
    service = AuthService(db)
    result = service.login(body.username, body.password)
    return ok(data=result, message="logged in")


@router.get("/me", response_model=ApiResponse)
def me(current_user: dict = Depends(get_current_user)):
    return ok(data=current_user)
