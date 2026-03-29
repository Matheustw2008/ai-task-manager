from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.task import Task


class TaskRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all_by_user(self, user_id: int) -> List[Task]:
        return self.db.query(Task).filter(Task.user_id == user_id).all()

    def get_by_id(self, task_id: int, user_id: int) -> Optional[Task]:
        return (
            self.db.query(Task)
            .filter(Task.id == task_id, Task.user_id == user_id)
            .first()
        )

    def create(self, title: str, description: Optional[str], category: str, user_id: int) -> Task:
        task = Task(
            title=title,
            description=description,
            category=category,
            user_id=user_id,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update(self, task: Task, **kwargs) -> Task:
        for key, value in kwargs.items():
            if value is not None:
                setattr(task, key, value)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()

    def get_by_ids(self, task_ids: List[int], user_id: int) -> List[Task]:
        return (
            self.db.query(Task)
            .filter(Task.id.in_(task_ids), Task.user_id == user_id)
            .all()
        )