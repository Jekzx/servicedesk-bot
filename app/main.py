"""FastAPI Application Main Entry Point."""
import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.core.database import init_db, SessionLocal
from app.models.ticket import Ticket
from app.services.auto_fix import auto_fix_service
from app.routers import webhook_router, tickets_router, health_router, dashboard_router

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("servicedesk-bot")

# Resolve paths robustly across local and Vercel/Lambda environments
BASE_DIR = Path(__file__).resolve().parent.parent


def find_file_in_candidate_paths(relative_path: str) -> Path | None:
    """Find a file across multiple candidate directories in serverless environments."""
    candidates = [
        BASE_DIR / relative_path,
        Path.cwd() / relative_path,
        Path("/var/task") / relative_path,
        Path(__file__).resolve().parent / relative_path,
    ]
    for c in candidates:
        if c.exists() and c.is_file():
            return c
    return None


def ensure_initial_seed(db):
    """Seed sample tickets and corporate catalog if database is empty."""
    try:
        auto_fix_service.ensure_default_services(db)
        if db.query(Ticket).count() == 0:
            from scripts.seed_data import seed
            seed()
    except Exception as e:
        logger.warning(f"Initial seed warning (non-fatal): {e}")


# Run initial DB setup eagerly for serverless environments where lifespan might not trigger
try:
    init_db()
    _init_db_session = SessionLocal()
    ensure_initial_seed(_init_db_session)
    _init_db_session.close()
except Exception as e:
    logger.warning(f"Eager DB init warning: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan for ASGI servers."""
    logger.info("🚀 Starting ServiceDesk Bot & Diagnostics API...")
    init_db()
    db = SessionLocal()
    try:
        ensure_initial_seed(db)
    finally:
        db.close()
    yield
    logger.info("🛑 Shutting down ServiceDesk Bot & Diagnostics API...")


# FastAPI Application instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
# 🤖 Service Desk WhatsApp Automation & Diagnostics Bot

API corporativa de autoatendimento, diagnóstico N1 de infraestrutura e gestão de chamados com integração ao WhatsApp.
    """,
    openapi_tags=[
        {"name": "WhatsApp Webhook", "description": "Recepção de mensagens e verificação de webhook da Meta."},
        {"name": "Service Desk Tickets", "description": "Gestão de chamados, filtros e atualização de status com notificação."},
        {"name": "Health & Diagnostics", "description": "Healthcheck e diagnóstico ativo de servidores corporativos."},
        {"name": "Dashboard & Analytics", "description": "Métricas SLA, taxa de auto-remediação e estatísticas em tempo real."},
    ],
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers Registration
app.include_router(webhook_router)
app.include_router(tickets_router)
app.include_router(health_router)
app.include_router(dashboard_router)

# Mount Static Directory if exists
static_dir = BASE_DIR / "static"
if static_dir.exists():
    try:
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    except Exception as e:
        logger.warning(f"StaticFiles mount warning: {e}")


# Explicit routes for static assets as serverless safety fallback
@app.get("/static/style.css", include_in_schema=False)
async def serve_css():
    file_path = find_file_in_candidate_paths("static/style.css")
    if file_path:
        return Response(content=file_path.read_text(encoding="utf-8"), media_type="text/css")
    return Response(content="/* CSS fallback */", media_type="text/css")


@app.get("/static/app.js", include_in_schema=False)
async def serve_js():
    file_path = find_file_in_candidate_paths("static/app.js")
    if file_path:
        return Response(content=file_path.read_text(encoding="utf-8"), media_type="application/javascript")
    return Response(content="// JS fallback", media_type="application/javascript")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_dashboard_ui(request: Request):
    """Serve the modern Service Desk Web Dashboard & WhatsApp Web Simulator."""
    file_path = find_file_in_candidate_paths("templates/index.html")
    if file_path:
        content = file_path.read_text(encoding="utf-8")
        return HTMLResponse(content=content)
    return HTMLResponse("<h1>Service Desk Bot API is running! Access <a href='/docs'>/docs</a> for Swagger UI.</h1>")
