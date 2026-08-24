"""Routers package initialization."""
from app.routers.webhook import router as webhook_router
from app.routers.tickets import router as tickets_router
from app.routers.health import router as health_router
from app.routers.dashboard import router as dashboard_router

__all__ = [
    "webhook_router",
    "tickets_router",
    "health_router",
    "dashboard_router",
]
