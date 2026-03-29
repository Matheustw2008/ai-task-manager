from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PDFUploadResponse(BaseModel):
    id: int
    filename: str
    content_preview: str
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class PDFSummarizeResponse(BaseModel):
    id: int
    filename: str
    summary: str


class PDFAskRequest(BaseModel):
    question: str


class PDFAskResponse(BaseModel):
    question: str
    answer: str


class PDFListResponse(BaseModel):
    id: int
    filename: str
    summary: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
