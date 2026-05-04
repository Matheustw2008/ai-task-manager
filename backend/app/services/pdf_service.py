import logging
from typing import List
import fitz
from groq import Groq, APIError, AuthenticationError, RateLimitError
from sqlalchemy.orm import Session
from app.core.settings import settings
from app.models.pdf_document import PDFDocument
from app.repositories.pdf_repository import PDFRepository

logger = logging.getLogger(__name__)

class PDFService:
    def __init__(self, db: Session):
        self.repository = PDFRepository(db)
        self.groq = Groq(api_key=settings.GROQ_API_KEY)

    def extract_text(self, file_bytes: bytes) -> str:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()

    def upload(self, filename: str, file_bytes: bytes, user_id: int) -> PDFDocument:
        # Validação em 2 camadas — service também valida
        if len(file_bytes) > 10 * 1024 * 1024:
            raise ValueError("Arquivo muito grande. Máximo 10MB.")
        content = self.extract_text(file_bytes)
        if not content:
            raise ValueError("PDF vazio ou sem texto legivel.")
        return self.repository.create(filename=filename, content=content, user_id=user_id)

    def summarize(self, pdf_id: int, user_id: int) -> PDFDocument:
        pdf = self.repository.get_by_id(pdf_id, user_id)
        if not pdf:
            raise ValueError("PDF nao encontrado.")
        content_truncated = pdf.content[:4000]
        prompt = f"Resuma o seguinte texto em portugues de forma clara e objetiva (maximo 5 paragrafos):\n\n{content_truncated}"
        try:
            response = self.groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
                timeout=10,  # timeout de 10 segundos
            )
            summary = response.choices[0].message.content.strip()
            return self.repository.update_summary(pdf, summary)
        except AuthenticationError:
            raise ValueError("Chave do Groq invalida ou expirada.")
        except RateLimitError:
            raise ValueError("Limite de uso do Groq atingido. Tente em instantes.")
        except APIError as e:
            raise ValueError(f"Erro na API do Groq: {str(e)}")
        except Exception as e:
            raise ValueError(f"Erro inesperado ao resumir: {str(e)}")

    def ask(self, pdf_id: int, user_id: int, question: str) -> str:
        pdf = self.repository.get_by_id(pdf_id, user_id)
        if not pdf:
            raise ValueError("PDF nao encontrado.")
        content_truncated = pdf.content[:4000]
        prompt = f"Com base no texto abaixo, responda a pergunta em portugues:\n\nTexto:\n{content_truncated}\n\nPergunta: {question}"
        try:
            response = self.groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
                timeout=10,  # timeout de 10 segundos
            )
            return response.choices[0].message.content.strip()
        except AuthenticationError:
            raise ValueError("Chave do Groq invalida ou expirada.")
        except RateLimitError:
            raise ValueError("Limite de uso do Groq atingido. Tente em instantes.")
        except APIError as e:
            raise ValueError(f"Erro na API do Groq: {str(e)}")
        except Exception as e:
            raise ValueError(f"Erro inesperado ao responder: {str(e)}")

    def get_all(self, user_id: int) -> List[PDFDocument]:
        return self.repository.get_all_by_user(user_id)

    def delete(self, pdf_id: int, user_id: int) -> None:
        pdf = self.repository.get_by_id(pdf_id, user_id)
        if not pdf:
            raise ValueError("PDF nao encontrado.")
        self.repository.delete(pdf)
