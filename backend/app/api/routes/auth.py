import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService
from slowapi import Limiter

logger = logging.getLogger(__name__)

# 🔒 CORREÇÃO — confiar ZERO em headers do cliente
def get_real_ip(request: Request) -> str:
    return request.client.host  # <-- ALTERADO (sem X-Real-IP)

limiter = Limiter(key_func=get_real_ip)

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    try:
        service = AuthService(db)
        user = service.register(data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        logger.error("Erro inesperado no registro")
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request, data: UserLogin, db: Session = Depends(get_db)):
    try:
        service = AuthService(db)
        return service.login(data.email, data.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception:
        logger.error("Erro inesperado no login")
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")
