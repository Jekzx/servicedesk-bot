"""FastAPI Application Main Entry Point."""
import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from starlette.types import ASGIApp, Scope, Receive, Send
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.core.database import init_db, SessionLocal
from app.models.ticket import Ticket
from app.services.auto_fix import auto_fix_service
from app.routers import webhook_router, tickets_router, health_router, dashboard_router
from app.embedded_assets import get_html_content, get_css_content, get_js_content

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("servicedesk-bot")

BASE_DIR = Path(__file__).resolve().parent.parent


class VercelPathFixMiddleware:
    """Middleware to normalize paths rewritten by Vercel serverless functions."""
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            # Vercel sends the true requested URI in x-matched-path or x-forwarded-uri
            matched_path = headers.get(b"x-matched-path") or headers.get(b"x-forwarded-uri") or headers.get(b"x-original-uri")
            if matched_path:
                decoded = matched_path.decode("utf-8").split("?")[0]
                scope["path"] = decoded
            else:
                path = scope.get("path", "")
                for prefix in ("/api/index.py", "/api/index"):
                    if path == prefix or path == prefix + "/":
                        scope["path"] = "/"
                        break
                    elif path.startswith(prefix + "/"):
                        scope["path"] = path[len(prefix):]
                        break
        await self.app(scope, receive, send)


def ensure_initial_seed(db):
    """Seed sample tickets and corporate catalog if database is empty."""
    try:
        auto_fix_service.ensure_default_services(db)
        if db.query(Ticket).count() == 0:
            from scripts.seed_data import seed
            seed()
    except Exception as e:
        logger.warning(f"Initial seed warning (non-fatal): {e}")


# Run initial DB setup eagerly for serverless environments
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

# Vercel Path Normalization Middleware
app.add_middleware(VercelPathFixMiddleware)

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


# Explicit routes for static assets and HTML
@app.get("/static/style.css", include_in_schema=False)
async def serve_css():
    return Response(content=get_css_content(), media_type="text/css")


@app.get("/static/app.js", include_in_schema=False)
async def serve_js():
    return Response(content=get_js_content(), media_type="application/javascript")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/api/index", response_class=HTMLResponse, include_in_schema=False)
@app.get("/api/index.py", response_class=HTMLResponse, include_in_schema=False)
async def serve_dashboard_ui(request: Request):
    """Serve the modern Service Desk Web Dashboard & WhatsApp Web Simulator."""
    html_content = get_html_content()
    return HTMLResponse(content=html_content)
