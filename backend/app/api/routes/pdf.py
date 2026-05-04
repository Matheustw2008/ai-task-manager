import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Request
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.pdf_document import PDFAskRequest, PDFAskResponse, PDFListResponse, PDFSummarizeResponse, PDFUploadResponse
from app.services.pdf_service import PDFService
from app.main import limiter  

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pdf", tags=["PDF"])

@router.post("/upload", response_model=PDFUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF sao aceitos.")
    try:
        file_bytes = await file.read()
        service = PDFService(db)
        pdf = service.upload(file.filename, file_bytes, current_user.id)
        return PDFUploadResponse(
            id=pdf.id,
            filename=pdf.filename,
            content_preview=pdf.content[:300] + "..." if len(pdf.content) > 300 else pdf.content,
            user_id=pdf.user_id,
            created_at=pdf.created_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.error(f"Erro no upload de PDF user={current_user.id}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")

@router.get("/", response_model=List[PDFListResponse])
def list_pdfs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        service = PDFService(db)
        return service.get_all(current_user.id)
    except Exception:
        logger.error(f"Erro ao listar PDFs user={current_user.id}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")

@router.post("/{pdf_id}/summarize", response_model=PDFSummarizeResponse)
@limiter.limit("5/minute")  # <-- ADICIONADO
def summarize_pdf(
    request: Request,  # <-- ADICIONADO
    pdf_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        service = PDFService(db)
        pdf = service.summarize(pdf_id, current_user.id)
        return PDFSummarizeResponse(id=pdf.id, filename=pdf.filename, summary=pdf.summary)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        logger.error(f"Erro ao resumir pdf={pdf_id} user={current_user.id}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")

@router.post("/{pdf_id}/ask", response_model=PDFAskResponse)
@limiter.limit("10/minute")  # <-- ADICIONADO
def ask_pdf(
    request: Request,  # <-- ADICIONADO
    pdf_id: int,
    data: PDFAskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        service = PDFService(db)
        answer = service.ask(pdf_id, current_user.id, data.question)
        return PDFAskResponse(question=data.question, answer=answer)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        logger.error(f"Erro ao responder pdf={pdf_id} user={current_user.id}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")

@router.delete("/{pdf_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pdf(
    pdf_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        service = PDFService(db)
        service.delete(pdf_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        logger.error(f"Erro ao deletar pdf={pdf_id} user={current_user.id}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")
