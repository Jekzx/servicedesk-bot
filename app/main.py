"""FastAPI Application Main Entry Point."""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

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


def ensure_initial_seed(db):
    """Seed sample tickets and corporate catalog if database is empty (e.g. on Vercel preview cold start)."""
    auto_fix_service.ensure_default_services(db)
    if db.query(Ticket).count() == 0:
        from scripts.seed_data import seed
        seed()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize database and corporate catalog on startup."""
    logger.info("🚀 Starting ServiceDesk Bot & Diagnostics API...")
    init_db()
    
    db = SessionLocal()
    try:
        ensure_initial_seed(db)
        logger.info("✅ Database tables, sample tickets, and corporate services catalog verified.")
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

### 🌟 Funcionalidades Principais:
* 📡 **Webhook WhatsApp (Meta Cloud API & Mock)**: Recepção de mensagens, áudios, imagens e mídias.
* 🧠 **Motor de Triagem Inteligente**: Classificação em tempo real (VPN, Active Directory, Erro 500, Hardware, ERP/CRM) e cálculo de prioridade P1-P4.
* 🛠️ **Auto-Remediação N1**: Instruções imediatas de autosserviço (AD/MFA) e healthcheck de serviços corporativos em tempo real.
* 🎫 **Gestão RESTful de Tickets**: CRUD completo com filtros por status, prioridade, data e notificação ao solicitante.
* 🖥️ **Painel Web Integrado**: Dashboard de métricas e Simulador Interativo do WhatsApp Web para testes instantâneos.
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

# Mount Static Files & Templates
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_dir = os.path.join(base_dir, "static")
templates_dir = os.path.join(base_dir, "templates")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates = Jinja2Templates(directory=templates_dir) if os.path.exists(templates_dir) else None


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_dashboard_ui(request: Request):
    """Serve the modern Service Desk Web Dashboard & WhatsApp Web Simulator."""
    index_path = os.path.join(templates_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>Service Desk Bot API is running! Access <a href='/docs'>/docs</a> for Swagger UI.</h1>")
