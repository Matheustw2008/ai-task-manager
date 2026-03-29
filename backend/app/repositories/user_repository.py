from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import hash_password


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, name: str, email: str, password: str) -> User:
        user = User(
            name=name,
            email=email,
            hashed_password=hash_password(password),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def exists_by_email(self, email: str) -> bool:
        return self.db.query(User).filter(User.email == email).count() > 0