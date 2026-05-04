from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
import re


def sanitize_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[<>]", "", text)
    text = re.sub(r"[\x00-\x1f]", "", text)
    return text


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: str = Field("geral", min_length=1, max_length=50)

    @field_validator("title")
    def clean_title(cls, v):
        return sanitize_text(v)

    @field_validator("description")
    def clean_description(cls, v):
        if v is None:
            return v
        return sanitize_text(v)

    @field_validator("category")
    def clean_category(cls, v):
        return sanitize_text(v)


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    is_completed: Optional[bool] = None
    category: Optional[str] = Field(None, min_length=1, max_length=50)

    @field_validator("title")
    def clean_title(cls, v):
        if v is None:
            return v
        return sanitize_text(v)

    @field_validator("description")
    def clean_description(cls, v):
        if v is None:
            return v
        return sanitize_text(v)

    @field_validator("category")
    def clean_category(cls, v):
        if v is None:
            return v
        return sanitize_text(v)


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    is_completed: bool
    priority: int
    category: str
    ai_suggestion: Optional[str]
    user_id: int
    created_at: datetime
    model_config = {"from_attributes": True}


class TaskPrioritizeRequest(BaseModel):
    task_ids: List[int] = Field(..., min_length=1, max_length=50)

    @field_validator("task_ids")
    def validate_ids(cls, v):
        if any(i <= 0 for i in v):
            raise ValueError("IDs devem ser números positivos.")
        if len(v) != len(set(v)):
            raise ValueError("IDs duplicados não são permitidos.")
        return v


class AIResponse(BaseModel):
    summary: str
    prioritized_tasks: List[TaskResponse]
