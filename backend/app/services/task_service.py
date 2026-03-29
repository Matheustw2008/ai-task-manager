from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.task import Task
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:

    def __init__(self, db: Session):
        self.repository = TaskRepository(db)

    def get_all(self, user_id: int) -> List[Task]:
        return self.repository.get_all_by_user(user_id)

    def get_by_id(self, task_id: int, user_id: int) -> Task:
        task = self.repository.get_by_id(task_id, user_id)
        if not task:
            raise ValueError("Tarefa não encontrada.")
        return task

    def create(self, data: TaskCreate, user_id: int) -> Task:
        return self.repository.create(
            title=data.title,
            description=data.description,
            category=data.category,
            user_id=user_id,
        )

    def update(self, task_id: int, data: TaskUpdate, user_id: int) -> Task:
        task = self.get_by_id(task_id, user_id)
        return self.repository.update(
            task,
            title=data.title,
            description=data.description,
            is_completed=data.is_completed,
            category=data.category,
        )

    def delete(self, task_id: int, user_id: int) -> None:
        task = self.get_by_id(task_id, user_id)
        self.repository.delete(task)

    def get_by_ids(self, task_ids: List[int], user_id: int) -> List[Task]:
        return self.repository.get_by_ids(task_ids, user_id)
