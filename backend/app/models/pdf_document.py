from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


def sanitize_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[<>]", "", text)
    text = re.sub(r"[\x00-\x1f]", "", text)
    return text


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
    question: str = Field(..., min_length=3, max_length=500)

    @field_validator("question")
    def clean_question(cls, v):
        return sanitize_text(v)


class PDFAskResponse(BaseModel):
    question: str
    answer: str


class PDFListResponse(BaseModel):
    id: int
    filename: str
    summary: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}
