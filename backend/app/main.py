import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.api.routes import auth, tasks, pdf
from app.core.database import Base, engine
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Logger seguro — erros internos nunca chegam ao cliente
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)
security = HTTPBearer()

# CORREÇÃO 3 — Rate limit com IP real (anti-spoofing)
def get_real_ip(request: Request) -> str:
    return request.headers.get("X-Real-IP") or request.client.host

limiter = Limiter(key_func=get_real_ip)

app = FastAPI(
    title="AI Task Manager",
    description="Gerenciador de tarefas inteligente com IA e leitura de PDFs",
    version="2.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORREÇÃO 1 — Handler global sem vazar erro interno
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro interno em {request.url}: {str(exc)}")  # log só no servidor
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor."},  # nunca vaza detalhes
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ai-task-manager-pearl-alpha.vercel.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # CORREÇÃO 4 — Headers que estavam faltando
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Cache-Control"] = "no-store"
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

# CORREÇÃO 5 — Rate limit aplicado no health também
@app.get("/health")
@limiter.limit("10/minute")
def health_check(request: Request):
    return {"status": "ok", "version": "2.0.0"}
