from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str = "geral"


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    category: Optional[str] = None


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
    task_ids: List[int]


class AIResponse(BaseModel):
    summary: str
    prioritized_tasks: List[TaskResponse]