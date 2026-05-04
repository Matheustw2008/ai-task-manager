import logging
import magic
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Request
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.pdf_document import PDFAskRequest, PDFAskResponse, PDFListResponse, PDFSummarizeResponse, PDFUploadResponse
from app.services.pdf_service import PDFService
from app.main import limiter  # importa limiter global

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/pdf", tags=["PDF"])


@router.post("/upload", response_model=PDFUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        file_bytes = await file.read()
        if len(file_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Arquivo muito grande. Máximo 10MB.")
        mime = magic.from_buffer(file_bytes[:2048], mime=True)
        if mime != "application/pdf":
            raise HTTPException(status_code=400, detail="Arquivo inválido. Apenas PDFs são aceitos.")
        service = PDFService(db)
        pdf = service.upload(file.filename, file_bytes, current_user.id)
        return PDFUploadResponse(
            id=pdf.id,
            filename=pdf.filename,
            content_preview=pdf.content[:200],
            user_id=pdf.user_id,
            created_at=pdf.created_at,
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.error("Erro no upload PDF", extra={"user_id": current_user.id})
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")


@router.get("/", response_model=List[PDFListResponse])
def list_pdfs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return PDFService(db).get_all(current_user.id)
    except Exception:
        logger.error("Erro ao listar PDFs", extra={"user_id": current_user.id})
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")


@router.post("/{pdf_id}/summarize", response_model=PDFSummarizeResponse)
@limiter.limit("5/minute")
def summarize_pdf(request: Request, pdf_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        pdf = PDFService(db).summarize(pdf_id, current_user.id)
        return PDFSummarizeResponse(id=pdf.id, filename=pdf.filename, summary=pdf.summary)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        logger.error("Erro ao resumir PDF", extra={"pdf_id": pdf_id, "user_id": current_user.id})
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")


@router.post("/{pdf_id}/ask", response_model=PDFAskResponse)
@limiter.limit("10/minute")
def ask_pdf(request: Request, pdf_id: int, data: PDFAskRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        answer = PDFService(db).ask(pdf_id, current_user.id, data.question)
        return PDFAskResponse(question=data.question, answer=answer)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        logger.error("Erro ao responder PDF", extra={"pdf_id": pdf_id, "user_id": current_user.id})
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")


@router.delete("/{pdf_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pdf(pdf_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        PDFService(db).delete(pdf_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        logger.error("Erro ao deletar PDF", extra={"pdf_id": pdf_id, "user_id": current_user.id})
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")
