import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

from app.api.routes import auth, tasks, pdf
from app.core.database import Base, engine


Base.metadata.create_all(bind=engine)

security = HTTPBearer()

ALLOWED_ORIGINS = ["*"]

app = FastAPI(
    title="AI Task Manager",
    description="Gerenciador de tarefas inteligente com IA e leitura de PDFs",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(pdf.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "version": "2.0.0"}
