from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    try:
        service = AuthService(db)
        user = service.register(data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")  # Máximo 5 tentativas por minuto por IP
def login(request: Request, data: UserLogin, db: Session = Depends(get_db)):
    try:
        service = AuthService(db)
        return service.login(data.email, data.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
