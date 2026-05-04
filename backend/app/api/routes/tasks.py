import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.task import TaskCreate, TaskPrioritizeRequest, TaskResponse, TaskUpdate
from app.services.ai_service import AIService
from app.services.task_service import TaskService
from app.main import limiter  # importa limiter global

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tasks", tags=["Tarefas"])


@router.get("/", response_model=List[TaskResponse])
def list_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return TaskService(db).get_all(current_user.id)
    except Exception:
        logger.error("Erro ao listar tasks", extra={"user_id": current_user.id})
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return TaskService(db).create(data, current_user.id)
    except Exception:
        logger.error("Erro ao criar task", extra={"user_id": current_user.id})
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return TaskService(db).update(task_id, data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        logger.error("Erro ao atualizar task", extra={"task_id": task_id, "user_id": current_user.id})
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        TaskService(db).delete(task_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        logger.error("Erro ao deletar task", extra={"task_id": task_id, "user_id": current_user.id})
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")


@router.post("/prioritize", response_model=List[TaskResponse])
@limiter.limit("10/minute")
def prioritize_tasks(request: Request, data: TaskPrioritizeRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        tasks = TaskService(db).get_by_ids(data.task_ids, current_user.id)
        if not tasks:
            raise HTTPException(status_code=404, detail="Nenhuma tarefa encontrada.")
        return AIService().prioritize_tasks(tasks)
    except HTTPException:
        raise
    except Exception:
        logger.error("Erro ao priorizar tasks", extra={"user_id": current_user.id})
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")


@router.get("/summary", response_model=dict)
@limiter.limit("10/minute")
def daily_summary(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        tasks = TaskService(db).get_all(current_user.id)
        summary = AIService().generate_daily_summary(tasks)
        return {"summary": summary}
    except Exception:
        logger.error("Erro ao gerar summary", extra={"user_id": current_user.id})
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")
