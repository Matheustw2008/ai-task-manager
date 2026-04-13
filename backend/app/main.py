import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from app.api.routes import auth, tasks, pdf
from app.core.database import Base, engine
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

Base.metadata.create_all(bind=engine)
security = HTTPBearer()

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="AI Task Manager",
    description="Gerenciador de tarefas inteligente com IA e leitura de PDFs",
    version="2.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

# Registrar o rate limiter no app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ai-task-manager-pearl-alpha.vercel.app"],  # CORRIGIDO
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if "X-Powered-By" in response.headers:
        del response.headers["X-Powered-By"]
    if "X-Real-IP" in response.headers:
        del response.headers["X-Real-IP"]
    if "X-Forwarded-For" in response.headers:
        del response.headers["X-Forwarded-For"]
    return response

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(pdf.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "2.0.0"}
