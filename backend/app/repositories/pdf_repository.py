from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.pdf_document import PDFDocument


class PDFRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, filename: str, content: str, user_id: int) -> PDFDocument:
        pdf = PDFDocument(filename=filename, content=content, user_id=user_id)
        self.db.add(pdf)
        self.db.commit()
        self.db.refresh(pdf)
        return pdf

    def get_by_id(self, pdf_id: int, user_id: int) -> Optional[PDFDocument]:
        return self.db.query(PDFDocument).filter(
            PDFDocument.id == pdf_id,
            PDFDocument.user_id == user_id
        ).first()

    def get_all_by_user(self, user_id: int) -> List[PDFDocument]:
        return self.db.query(PDFDocument).filter(
            PDFDocument.user_id == user_id
        ).all()

    def update_summary(self, pdf: PDFDocument, summary: str) -> PDFDocument:
        pdf.summary = summary
        self.db.commit()
        self.db.refresh(pdf)
        return pdf

    def delete(self, pdf: PDFDocument) -> None:
        self.db.delete(pdf)
        self.db.commit()
