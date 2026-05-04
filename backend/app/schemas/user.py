from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


def sanitize_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[<>]", "", text)
    text = re.sub(r"[\x00-\x1f]", "", text)
    return text


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("name")
    def clean_name(cls, v):
        return sanitize_text(v)

    @field_validator("password")
    def validate_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Senha deve ter ao menos uma letra maiúscula.")
        if not re.search(r"[0-9]", v):
            raise ValueError("Senha deve ter ao menos um número.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Senha deve ter ao menos um caractere especial.")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
