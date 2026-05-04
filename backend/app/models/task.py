import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.task import TaskCreate, TaskPrioritizeRequest, TaskResponse, TaskUpdate
from app.services.ai_service import AIService
from app.services.task_service import TaskService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["Tarefas"])

@router.get("/", response_model=List[TaskResponse])
def list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        service = TaskService(db)
        return service.get_all(current_user.id)
    except Exception:
        logger.error(f"Erro ao listar tasks user={current_user.id}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        service = TaskService(db)
        return service.create(data, current_user.id)
    except Exception:
        logger.error(f"Erro ao criar task user={current_user.id}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        service = TaskService(db)
        return service.update(task_id, data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        logger.error(f"Erro ao atualizar task={task_id} user={current_user.id}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        service = TaskService(db)
        service.delete(task_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        logger.error(f"Erro ao deletar task={task_id} user={current_user.id}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")

@router.post("/prioritize", response_model=List[TaskResponse])
def prioritize_tasks(
    data: TaskPrioritizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        task_service = TaskService(db)
        ai_service = AIService()
        tasks = task_service.get_by_ids(data.task_ids, current_user.id)
        if not tasks:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhuma tarefa encontrada.")
        return ai_service.prioritize_tasks(tasks)
    except HTTPException:
        raise
    except Exception:
        logger.error(f"Erro ao priorizar tasks user={current_user.id}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")

@router.get("/summary", response_model=dict)
def daily_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        task_service = TaskService(db)
        ai_service = AIService()
        tasks = task_service.get_all(current_user.id)
        summary = ai_service.generate_daily_summary(tasks)
        return {"summary": summary}
    except Exception:
        logger.error(f"Erro ao gerar summary user={current_user.id}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")
