from datetime import timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.core.settings import settings
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import Token, UserCreate


class AuthService:

    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def register(self, data: UserCreate) -> User:
        if self.repository.exists_by_email(data.email):
            raise ValueError("Email já cadastrado.")
        return self.repository.create(
            name=data.name,
            email=data.email,
            password=data.password,
        )

    def login(self, email: str, password: str) -> Token:
        user = self.repository.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Email ou senha inválidos.")
        if not user.is_active:
            raise ValueError("Usuário inativo.")
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return Token(access_token=access_token, token_type="bearer")

    def get_current_user(self, email: str) -> Optional[User]:
        return self.repository.get_by_email(email)
